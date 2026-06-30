import logging
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Identifiants des modèles de devis (sale.order.template) du workflow TZEE
TEMPLATE_MAR_CLIENT_TZEE = 2  # "Projet MAR (Client TZEE)" : devis facturé au client final
TEMPLATE_TZEE = 3  # "Projet TZEE (ZEE)" : devis facturé à la structure publique

# Jalon final : déclenche la facturation client (MAR) et le désarchivage du devis MAR
JALON_TRAVAUX_TERMINES = "Travaux terminés"


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    # Activer le mécanisme d'archivage d'Odoo
    _order = "date_order desc, name desc, id desc"

    devis_tzee_id = fields.Many2one(
        "sale.order", 
        string="Devis TZEE",
        domain=f"[('sale_order_template_id', '=', {TEMPLATE_TZEE})]",
        help="Devis associé utilisant le modèle TZEE (ID=3)"
    )
    client_tzee_id = fields.Many2one(
        "sale.order", 
        string="Client TZEE",
        domain=f"[('sale_order_template_id', '=', {TEMPLATE_MAR_CLIENT_TZEE})]",
        help="Client associé utilisant le modèle Client TZEE (ID=2)"
    )
    order_state_id = fields.Many2one(
        "sale.order.state",
        string="Jalon",
        group_expand="_read_group_order_state_ids",
        index=True,
        tracking=True,
        default=lambda self: self.env['sale.order.state'].browse(1)
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
    
    # Forcer le mode de paiement à 30 jours par défaut
    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Conditions de paiement",
        default=lambda self: self.env['account.payment.term'].browse(4)
    )
    
    # Champ active pour permettre l'archivage des devis
    active = fields.Boolean(default=True, export_string_translation=False)

    
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

    def write(self, vals):
        """Surcharge write pour déclencher set_delivered_line_from_state lors du changement de jalon"""
        result = super().write(vals)
        
        # Si le champ order_state_id a été modifié, déclencher la mise à jour des lignes livrées
        if 'order_state_id' in vals:
            for record in self:
                if record.order_state_id:
                    # Mémoriser l'état des lignes avant modification
                    lines_before = {line.id: line.qty_delivered for line in record.order_line}
                    
                    # Déclencher la mise à jour des lignes livrées
                    record.set_delivered_line_from_state(record.order_state_id)
                    
                    # Vérifier si des lignes ont été modifiées et générer une facture si nécessaire
                    record._auto_create_invoice_if_delivered(lines_before)
                    
                    # Synchroniser le jalon avec le devis client TZEE archivé (si applicable)
                    record._sync_jalon_with_client_tzee()
                    
                    # Désarchiver le devis client si le jalon est "Travaux terminés"
                    record._handle_client_tzee_unarchive()
        
        return result
    
    def _sync_jalon_with_client_tzee(self):
        """Synchronise le jalon du devis TZEE avec le devis client TZEE archivé"""
        self.ensure_one()
        
        # Si c'est un devis TZEE principal (modèle 3) qui a un client_tzee_id
        if (self.sale_order_template_id and
            self.sale_order_template_id.id == TEMPLATE_TZEE and
            self.client_tzee_id):
            
            # Mettre à jour le jalon du devis client archivé
            self.client_tzee_id.order_state_id = self.order_state_id
            
            _logger.info(
                "Jalon synchronisé: Devis TZEE %s -> Devis Client %s (%s)", 
                self.name, 
                self.client_tzee_id.name,
                self.order_state_id.name if self.order_state_id else 'None'
            )
    
    def _handle_client_tzee_unarchive(self):
        """Désarchive le devis client quand le devis TZEE atteint 'Travaux terminés'"""
        self.ensure_one()
        
        # Vérifier si c'est un devis TZEE principal avec un jalon "Travaux terminés"
        if (self.sale_order_template_id and
            self.sale_order_template_id.id == TEMPLATE_TZEE and
            self.client_tzee_id and
            self.order_state_id and
            self.order_state_id.name == JALON_TRAVAUX_TERMINES):
            
            # Désarchiver le devis client
            self.client_tzee_id.active = True
            
            # Ajouter un message dans le chatter
            self.client_tzee_id.message_post(
                body=f"🔄 <strong>Devis désarchivé automatiquement</strong><br/>"
                     f"📋 Suite au passage du devis TZEE <a href='/web#id={self.id}&view_type=form&model=sale.order'>{self.name}</a> "
                     f"au jalon '<strong>Travaux terminés</strong>'",
                message_type='comment'
            )
            
            _logger.info(
                "Devis client %s désarchivé suite à la finalisation du devis TZEE %s", 
                self.client_tzee_id.name,
                self.name
            )

    def set_delivered_line_from_state(self, order_state):
        """Marque les lignes livrées (qty_delivered) selon le jalon atteint.

        Deux régimes :
        - devis MAR « fantôme » (client final) : on ne facture qu'au jalon final
          « Travaux terminés », et on y facture TOUTES ses lignes ;
        - autres devis (TZEE, Projet MAR classique, etc) : à chaque jalon, on livre
          les lignes dont la catégorie correspond à celle du jalon.
        """
        self.ensure_one()
        if not order_state or self.state != 'sale':
            return

        if self.sale_order_template_id.id == TEMPLATE_MAR_CLIENT_TZEE:
            self._deliver_mar_ghost_lines(order_state)
        else:
            self._deliver_lines_for_jalon(order_state)

    def _deliver_mar_ghost_lines(self, order_state):
        """Devis MAR « fantôme » : facture le client final, mais uniquement au
        jalon « Travaux terminés », et y facture TOUTES ses lignes (quelle que
        soit leur catégorie). Aux étapes intermédiaires, on ne marque rien (elles
        sont facturées à la structure publique via le devis TZEE)."""
        if order_state.name != JALON_TRAVAUX_TERMINES:
            return
        for line in self.order_line:
            line.qty_delivered = line.product_uom_qty

    def _deliver_lines_for_jalon(self, order_state):
        """Flux standard : on livre les lignes dont la catégorie correspond à
        celle du jalon courant."""
        if not order_state.product_category_id or self.order_state_id != order_state:
            return
        for line in self.order_line:
            if line.product_id.categ_id == order_state.product_category_id:
                line.qty_delivered = line.product_uom_qty

    def _auto_create_invoice_if_delivered(self, lines_before):
        """
        Génère automatiquement une facture en brouillon si des lignes ont été marquées comme livrées
        lors du changement d'étape - utilise les méthodes standard d'Odoo
        """
        self.ensure_one()

        # Vérifier que la commande est confirmée
        if self.state != 'sale':
            return

        # Vérifier si des lignes ont été modifiées (passées de 0 à une valeur > 0 en qty_delivered)
        lines_modified = []
        for line in self.order_line:
            old_qty = lines_before.get(line.id, 0)
            new_qty = line.qty_delivered
            
            # Si la ligne était non livrée (0) et est maintenant livrée (> 0)
            if old_qty == 0 and new_qty > 0:
                lines_modified.append(line)
        
        # Si aucune ligne n'a été modifiée, ne rien faire
        if not lines_modified:
            return
        
        # Vérifier s'il y a des lignes livrées non facturées
        lines_to_invoice = self.order_line.filtered(lambda l: l.qty_delivered > l.qty_invoiced)
        
        if not lines_to_invoice:
            return
        
        try:
            # Utiliser la méthode standard d'Odoo pour créer les factures
            # Cela réutilise toute la logique existante de facturation
            invoice = self._create_invoices()
            
            if invoice:
                # Préparer la liste des lignes concernées avec formatage HTML
                lines_list = "<br/>".join([f"• {line.product_id.name}" for line in lines_modified])
                
                # Ajouter un message dans le chatter pour traçabilité avec lien vers la facture
                self.message_post(
                    body=f"✅ <strong>Facture générée automatiquement</strong><br/>"
                         f"📄 Facture: <a href='/web#id={invoice.id}&view_type=form&model=account.move' style='font-weight:bold;'>Voir la facture</a><br/>"
                         f"🎯 Suite au changement d'étape: <strong>{self.order_state_id.name}</strong><br/>"
                         f"📦 <strong>Lignes concernées:</strong><br/>{lines_list}",
                    message_type='comment'
                )
                
                return invoice
                
        except Exception as e:
            _logger.error(
                "Erreur lors de la création automatique de facture pour la commande %s: %s",
                self.name, str(e)
            )
            # Ne pas bloquer le processus en cas d'erreur, juste logger
            return False

    def create_tzee_order(self):
        """Créer un devis TZEE lié au devis client actuel"""
        self.ensure_one()
        
        # Vérifier les conditions
        if not self.sale_order_template_id or self.sale_order_template_id.id != TEMPLATE_MAR_CLIENT_TZEE:
            raise UserError(_("Cette action n'est disponible que pour les devis avec le modèle Client TZEE (ID=2)"))
        
        if self.devis_tzee_id:
            raise UserError(_("Un devis TZEE est déjà associé à ce devis. Utilisez le bouton 'Voir devis TZEE' pour y accéder."))
        
        if not self.partner_id:
            raise UserError(_("Veuillez d'abord sélectionner un client avant de créer un devis TZEE"))
        
        # Récupérer le modèle TZEE (ID=3)
        tzee_template = self.env['sale.order.template'].browse(TEMPLATE_TZEE)
        if not tzee_template.exists():
            raise UserError(_("Le modèle de devis TZEE (ID=3) n'existe pas. Veuillez contacter votre administrateur."))

        # Créer le nouveau devis TZEE avec les lignes du modèle
        tzee_order_vals = {
            'partner_id': self.partner_id.id,
            'sale_order_template_id': TEMPLATE_TZEE,
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
        
        # Ajouter une ligne de note en première position si client_tzee_id est défini
        if self.partner_id:
            client_name = self.partner_id.name
            note_line = (0, 0, {
                'display_type': 'line_note',
                'name': f"Pour le dossier de {client_name}",
                'sequence': 1,  # Première ligne
            })
            tzee_order_vals['order_line'].append(note_line)
        
        # Ajouter explicitement les lignes du modèle TZEE (même logique que dans sale_order_import.py)
        sequence = 10  # Commencer à 10 pour les lignes normales
        for line in tzee_template.sale_order_template_line_ids:
            tzee_order_vals['order_line'].append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom_id.id,
                'name': line.name,
                'sequence': sequence,
            }))
            sequence += 1
        
        _logger.info("Creating TZEE order with values: %s", tzee_order_vals)
        
        # Créer le devis avec toutes les valeurs (y compris les lignes du modèle)
        tzee_order = self.create(tzee_order_vals)
        
        # Lier le devis TZEE au devis client
        self.devis_tzee_id = tzee_order.id
        
        # Archiver le devis client TZEE (modèle 2) car on va gérer uniquement le devis TZEE principal
        self.active = False
        
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

    def toggle_active(self):
        """Basculer l'état actif/archivé du devis"""
        for record in self:
            record.active = not record.active
            
            # Ajouter un message dans le chatter
            action = "archivé" if not record.active else "désarchivé"
            record.message_post(
                body=f"📁 Devis {action} manuellement",
                message_type='comment'
            )


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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    force_invoicing = fields.Boolean(
        string="Forcer la facturation",
        help="Cocher cette case pour forcer qty_invoiced et qty_delivered à la quantité commandée (utile pour l'import d'historique)"
    )

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'force_invoicing')
    def _compute_qty_invoiced(self):
        """Override pour gérer le force_invoicing"""
        # Appel de la méthode parent pour le calcul normal
        super()._compute_qty_invoiced()
        
        # Ensuite, forcer à la quantité commandée si force_invoicing est coché
        for line in self:
            if line.force_invoicing:
                line.qty_invoiced = line.product_uom_qty

    @api.depends(
        'qty_delivered_method',
        'analytic_line_ids.so_line',
        'analytic_line_ids.unit_amount',
        'analytic_line_ids.product_uom_id',
        'force_invoicing')
    def _compute_qty_delivered(self):
        """Override pour gérer le force_invoicing"""
        # Filtrer les lignes avec force_invoicing pour les traiter séparément
        forced_lines = self.filtered('force_invoicing')
        remaining_lines = self - forced_lines
        
        # Appel de la méthode parent pour le calcul normal sur les lignes restantes
        if remaining_lines:
            super(SaleOrderLine, remaining_lines)._compute_qty_delivered()
        
        # Forcer à la quantité commandée pour les lignes avec force_invoicing
        for line in forced_lines:
            line.qty_delivered = line.product_uom_qty
