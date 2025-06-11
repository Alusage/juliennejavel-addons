from odoo import models, fields, api


class TourLauncher(models.TransientModel):
    _name = "bet.tour.launcher"
    _description = "Lanceur de visite guidée BET"

    tour_name = fields.Selection([
        ('bet_simple_tour', 'Tour Simple BET'),
        ('bet_advanced_tour', 'Tour Avancé BET'),
    ], string="Tour à lancer", default='bet_advanced_tour', required=True)

    def launch_tour(self):
        """Lance le tour sélectionné en utilisant JavaScript côté client"""
        return {
            'type': 'ir.actions.client',
            'tag': 'simple_tour_launcher',
            'params': {
                'tour_name': self.tour_name
            }
        }

    @api.model
    def get_available_tours(self):
        """Retourne la liste des tours disponibles"""
        return [
            {
                'name': 'bet_simple_tour',
                'description': 'Tour simple de présentation du module BET',
                'duration': '2 minutes'
            },
            {
                'name': 'bet_advanced_tour', 
                'description': 'Tour avancé avec navigation dans l\'interface BET',
                'duration': '5 minutes'
            }
        ]
