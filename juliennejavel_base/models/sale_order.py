import logging
from odoo import models, fields, api, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    devis_tzee_id = fields.Many2one("sale.order", string="Devis TZEE")
    client_tzee_id = fields.Many2one("sale.order", string="Client TZEE")
    order_state_id = fields.Many2one(
        "sale.order.state",
        string="Jalon",
        group_expand="_read_group_order_state_ids",
        index=True,
        tracking=True,
    )
    fiscal_revenue = fields.Selection(
        selection=[("TM", "Très Modeste"), ("RI", "Revenu Intermediare"), ("M", "Modeest"), ("RS", "Revenu Supérieur")],
        string="Revenu Fiscal",
    )

    energy_gain = fields.Float(string="Gain Énergétique (%)")
    total_work_cost = fields.Monetary(string="Coût Total des Travaux", currency_field='currency_id')
    total_subsidies = fields.Monetary(string="Somme des Subventions", currency_field='currency_id')
    financing_rate = fields.Float(string="Taux de Financement (%)")
    delegataire_id = fields.Many2one("res.partner", string="Délégataire")
    procivis_file = fields.Char(string="Dossier Procivis (URL)")

    @api.model
    def _read_group_order_state_ids(self, order_states, domain, order):
        _logger.info(
            "#### order_states: %s - %s - %s - %s", order_states, domain, order, self
        )
        stage_ids = order_states._search(
            [], order=order, access_rights_uid=SUPERUSER_ID
        )
        return order_states.browse(stage_ids)
    
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.fiscal_revenue = self.partner_id.fiscal_revenue

    def set_delivered_line_from_state(self, order_state):
        if not order_state or not order_state.product_category_id:
            return
        for line in self.order_line:
            if line.order_id.state == 'sale' and line.order_id.order_state_id == order_state and line.product_id.categ_id == order_state.product_category_id:
                line.qty_delivered = line.product_uom_qty


class SaleOrderJalon(models.Model):
    _name = "sale.order.state"
    _description = "Etape de commande"
    _order = 'sequence, id'

    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=1)
    product_category_id = fields.Many2one(
        "product.category", string="Categorie de produit"
    )
