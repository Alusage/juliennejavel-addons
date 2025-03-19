from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    fiscal_revenue = fields.Selection(
        selection=[("TM", "TM"), ("RI", "RI"), ("M", "M"), ("RS", "RS")],
        string="Revenu Fiscal",
    )
