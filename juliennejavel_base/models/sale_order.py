import logging
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    devis_tzee_id = fields.Many2one(
        "sale.order", 
        string="Devis TZEE", 
        domain="[('sale_order_template_id', '=', 3)]",
        help="Devis associé utilisant le modèle TZEE (ID=3)"
    )
    client_tzee_id = fields.Many2one(
        "sale.order", 
        string="Client TZEE", 
        domain="[('sale_order_template_id', '=', 2)]",
        help="Client associé utilisant le modèle Client TZEE (ID=2)"
    )
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
    
    # Champ couleur calculé basé sur le modèle de devis
    color = fields.Integer(string="Couleur", compute="_compute_color", store=False)

    @api.depends('sale_order_template_id')
    def _compute_color(self):
        """Calcule la couleur de la carte kanban basée sur le modèle de devis"""
        for record in self:
            if record.sale_order_template_id:
                # Utilise l'ID du modèle de devis pour générer une couleur
                # On utilise le modulo pour obtenir une couleur entre 0 et 11 (12 couleurs disponibles dans Odoo)
                record.color = (record.sale_order_template_id.id % 12)
            else:
                record.color = 0  # Couleur par défaut (gris)

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

    @api.onchange("sale_order_template_id")
    def _onchange_sale_order_template_id(self):
        """Nettoie les champs TZEE quand le modèle change"""
        if self.sale_order_template_id:
            # Si ce n'est pas le modèle ID=2, vider le champ devis_tzee_id
            if self.sale_order_template_id.id != 2:
                self.devis_tzee_id = False
            # Si ce n'est pas le modèle ID=3, vider le champ client_tzee_id  
            if self.sale_order_template_id.id != 3:
                self.client_tzee_id = False
        else:
            # Si aucun modèle, vider les deux champs
            self.devis_tzee_id = False
            self.client_tzee_id = False

    def write(self, vals):
        """Surcharge write pour déclencher set_delivered_line_from_state lors du changement de jalon"""
        result = super().write(vals)
        
        # Si le champ order_state_id a été modifié, déclencher la mise à jour des lignes livrées
        if 'order_state_id' in vals:
            for record in self:
                if record.order_state_id:
                    record.set_delivered_line_from_state(record.order_state_id)
        
        return result

    def set_delivered_line_from_state(self, order_state):
        if not order_state or not order_state.product_category_id:
            return
        for line in self.order_line:
            if line.order_id.state == 'sale' and line.order_id.order_state_id == order_state and line.product_id.categ_id == order_state.product_category_id:
                line.qty_delivered = line.product_uom_qty

    def create_tzee_order(self):
        """Créer un devis TZEE lié au devis client actuel"""
        self.ensure_one()
        
        # Vérifier les conditions
        if not self.sale_order_template_id or self.sale_order_template_id.id != 2:
            raise UserError(_("Cette action n'est disponible que pour les devis avec le modèle Client TZEE (ID=2)"))
        
        if self.devis_tzee_id:
            raise UserError(_("Un devis TZEE est déjà associé à ce devis. Utilisez le bouton 'Voir devis TZEE' pour y accéder."))
        
        if not self.partner_id:
            raise UserError(_("Veuillez d'abord sélectionner un client avant de créer un devis TZEE"))
        
        # Récupérer le modèle TZEE (ID=3)
        tzee_template = self.env['sale.order.template'].browse(3)
        if not tzee_template.exists():
            raise UserError(_("Le modèle de devis TZEE (ID=3) n'existe pas. Veuillez contacter votre administrateur."))
        
        # Créer le nouveau devis TZEE avec les lignes du modèle
        tzee_order_vals = {
            'partner_id': self.partner_id.id,
            'sale_order_template_id': 3,
            'client_tzee_id': self.id,  # Lien vers le devis client original
            'state': 'draft',
            'origin': f"Généré depuis {self.name}",
            # Copier les informations importantes du devis client
            'fiscal_revenue': self.fiscal_revenue,
            'energy_gain': self.energy_gain,
            'total_work_cost': self.total_work_cost,
            'total_subsidies': self.total_subsidies,
            'financing_rate': self.financing_rate,
            'delegataire_id': self.delegataire_id.id if self.delegataire_id else False,
            'procivis_file': self.procivis_file,
            'order_state_id': self.order_state_id.id if self.order_state_id else False,
            'order_line': [],  # Initialiser la liste des lignes
        }
        
        # Ajouter explicitement les lignes du modèle TZEE (même logique que dans sale_order_import.py)
        for line in tzee_template.sale_order_template_line_ids:
            tzee_order_vals['order_line'].append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom_id.id,
                'name': line.name,
            }))
        
        _logger.info("Creating TZEE order with values: %s", tzee_order_vals)
        
        # Créer le devis avec toutes les valeurs (y compris les lignes du modèle)
        tzee_order = self.create(tzee_order_vals)
        
        # Lier le devis TZEE au devis client
        self.devis_tzee_id = tzee_order.id
        
        # Ajouter un message dans le chatter du nouveau devis TZEE
        tzee_order.message_post(
            body=f"Devis TZEE généré automatiquement depuis le devis client <a href='/web#id={self.id}&view_type=form&model=sale.order'>{self.name}</a>",
            message_type='comment'
        )
        
        # Ajouter un message dans le chatter du devis client
        self.message_post(
            body=f"Devis TZEE <a href='/web#id={tzee_order.id}&view_type=form&model=sale.order'>{tzee_order.name}</a> créé automatiquement",
            message_type='comment'
        )
        
        # Notifier l'utilisateur du succès
        message = _("Devis TZEE créé avec succès ! Vous allez être redirigé vers le nouveau devis.")
        
        # Retourner une action pour ouvrir le nouveau devis
        return {
            'type': 'ir.actions.act_window',
            'name': 'Devis TZEE créé',
            'res_model': 'sale.order',
            'res_id': tzee_order.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_message': message,
            }
        }
    
    def action_view_tzee_order(self):
        """Action pour ouvrir le devis TZEE associé"""
        self.ensure_one()
        if not self.devis_tzee_id:
            raise UserError(_("Aucun devis TZEE n'est associé à ce devis"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Devis TZEE associé',
            'res_model': 'sale.order',
            'res_id': self.devis_tzee_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


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
