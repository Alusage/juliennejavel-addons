import logging
from odoo import Command, _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_account_move_export_line(self, export_options):
        self.ensure_one()
        res = super(AccountMoveLine, self)._prepare_account_move_export_line(
            export_options
        )
        invoice = (
            self.env["account.move"].search([("name", "=", res["entry_ref"])], limit=1)
            if res["entry_ref"]
            else self.move_id
        )

        if res["journal_code"] in ["CA", "CCOOP"]:
            if res["account_code"].startswith("512"):
                res["account_code"] = self.journal_id.default_account_id.code
                res["account_name"] = self.journal_id.default_account_id.name
        else:
            if res["account_code"].startswith("411") or res["account_code"].startswith(
                "7"
            ):
                res["item_label"] = "%s - %s" % (
                    self.partner_id.commercial_partner_id.name,
                    res["item_label"],
                )

        if invoice.payment_mode_id and (
            res["account_code"].startswith("411")
            or res["account_code"].startswith("512")
        ):
            res["item_label"] = "%s - %s" % (
                invoice.payment_mode_id.name,
                res["item_label"],
            )

        return res
