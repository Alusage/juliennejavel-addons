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

    @api.model
    def _read_group_order_state_ids(self, order_states, domain, order):
        _logger.info(
            "#### order_states: %s - %s - %s - %s", order_states, domain, order, self
        )
        stage_ids = order_states._search(
            [], order=order, access_rights_uid=SUPERUSER_ID
        )
        return order_states.browse(stage_ids)


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
