from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    fiscal_revenue = fields.Selection(
        selection=[("TM", "Très Modeste"), ("RI", "Revenu Intermediare"), ("M", "Modeest"), ("RS", "Revenu Supérieur")],
        string="Revenu Fiscal",
    )
