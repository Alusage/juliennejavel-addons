import base64
import io

from odoo import api, fields, models, _
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class MailTrackingExportWizard(models.TransientModel):
    _name = "mail.tracking.export.wizard"
    _description = "Mail Tracking Export Wizard"

    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        domain=[("is_mail_thread", "=", True)],
    )
    model_name = fields.Char(related="model_id.model", string="Model Name")
    field_ids = fields.Many2many(
        "ir.model.fields",
        "mail_tracking_export_field_rel",
        "wizard_id",
        "field_id",
        string="Context Fields",
        help="Fields from the source record to include as columns in the export.",
    )
    tracked_field_ids = fields.Many2many(
        "ir.model.fields",
        "mail_tracking_export_tracked_field_rel",
        "wizard_id",
        "field_id",
        string="Tracked Fields Filter",
        help="Only export changes for these tracked fields. "
        "Leave empty to export all tracked changes.",
    )
    date_from = fields.Datetime(string="From")
    date_to = fields.Datetime(string="To")
    data = fields.Binary(string="File", readonly=True)
    filename = fields.Char(string="Filename", readonly=True)

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_ids = False
        self.tracked_field_ids = False

    def _get_tracking_domain(self):
        domain = [("mail_message_id.model", "=", self.model_name)]
        if self.date_from:
            domain.append(("mail_message_id.date", ">=", self.date_from))
        if self.date_to:
            domain.append(("mail_message_id.date", "<=", self.date_to))
        if self.tracked_field_ids:
            domain.append(
                ("field", "in", self.tracked_field_ids.ids)
            )
        return domain

    def _get_display_value(self, tracking, prefix):
        """Get human-readable display value for a tracking record."""
        field_type = tracking.field_type
        if field_type in ("integer", "float", "char", "text", "monetary"):
            return tracking["%s_value_%s" % (prefix, field_type)]
        elif field_type == "datetime":
            return tracking["%s_value_datetime" % prefix] or ""
        elif field_type == "date":
            val = tracking["%s_value_datetime" % prefix]
            return fields.Date.to_string(val) if val else ""
        elif field_type == "boolean":
            return bool(tracking["%s_value_integer" % prefix])
        else:
            return tracking["%s_value_char" % prefix] or ""

    def _get_record_field_value(self, record, field):
        """Get a display-friendly value for a field on a record."""
        value = record[field.name]
        if field.ttype in ("many2one",):
            return value.display_name or ""
        elif field.ttype in ("many2many", "one2many"):
            return ", ".join(value.mapped("display_name"))
        elif field.ttype == "selection":
            selection_dict = dict(
                record._fields[field.name]._description_selection(self.env)
            )
            return selection_dict.get(value, value or "")
        elif field.ttype in ("date", "datetime"):
            return str(value) if value else ""
        elif field.ttype == "boolean":
            return _("Yes") if value else _("No")
        return value if value is not None else ""

    def action_export(self):
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(
                _("xlsxwriter library is required. "
                  "Install it with: pip install xlsxwriter")
            )

        domain = self._get_tracking_domain()
        trackings = self.env["mail.tracking.value"].search(
            domain, order="mail_message_id desc"
        )
        if not trackings:
            raise UserError(_("No tracking values found for the given criteria."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet(_("Tracking Changes"))

        # Formats
        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#4472C4",
            "font_color": "white",
            "border": 1,
        })
        date_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
        cell_format = workbook.add_format({"border": 1})

        # Headers
        context_fields = self.field_ids
        headers = []
        for f in context_fields:
            headers.append(f.field_description)
        headers.extend([
            _("Changed Field"),
            _("Old Value"),
            _("New Value"),
            _("Date"),
            _("User"),
        ])

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        # Cache source records
        res_ids = trackings.mapped("mail_message_id.res_id")
        SourceModel = self.env[self.model_name]
        existing_records = SourceModel.search([("id", "in", res_ids)])
        record_map = {r.id: r for r in existing_records}

        # Data rows
        row = 1
        for tracking in trackings:
            message = tracking.mail_message_id
            record = record_map.get(message.res_id)

            col = 0
            # Context fields
            for f in context_fields:
                if record:
                    val = self._get_record_field_value(record, f)
                else:
                    val = _("(deleted)")
                sheet.write(row, col, str(val) if val else "", cell_format)
                col += 1

            # Tracking info
            sheet.write(row, col, tracking.field_desc or "", cell_format)
            col += 1
            sheet.write(
                row, col,
                str(self._get_display_value(tracking, "old")),
                cell_format,
            )
            col += 1
            sheet.write(
                row, col,
                str(self._get_display_value(tracking, "new")),
                cell_format,
            )
            col += 1
            if message.date:
                sheet.write_datetime(row, col, message.date, date_format)
            else:
                sheet.write(row, col, "", cell_format)
            col += 1
            sheet.write(
                row, col,
                message.author_id.display_name or "",
                cell_format,
            )
            row += 1

        # Auto-fit columns
        for col_idx in range(len(headers)):
            sheet.set_column(col_idx, col_idx, 20)

        workbook.close()
        output.seek(0)

        self.write({
            "data": base64.b64encode(output.read()),
            "filename": "tracking_export_%s.xlsx" % self.model_name.replace(".", "_"),
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "context": {"default_download": True},
        }
