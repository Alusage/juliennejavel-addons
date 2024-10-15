import logging
from odoo import Command, _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMoveExport(models.Model):
    _inherit = "account.move.export"

    def _csv_postprocess_line(self, ldict, export_options):
        row = super(AccountMoveExport, self)._csv_postprocess_line(
            ldict, export_options
        )
        return row
