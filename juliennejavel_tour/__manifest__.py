# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Julienne Javel Tours",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": "Visites guidées pour les modules Julienne Javel",
    "description": """
Julienne Javel Tours
====================

Ce module fournit des visites guidées interactives pour les modules Julienne Javel :

Fonctionnalités
---------------
* Tours interactifs personnalisés
* Interface de sélection des tours
* Styles et animations personnalisés
* Compatible avec le framework de tours d'Odoo 16.0

Tours disponibles
-----------------
* Tour Simple BET : Présentation rapide des fonctionnalités (2 minutes)
* Tour Avancé BET : Découverte détaillée du module (5 minutes)

Utilisation
-----------
1. Allez dans BET → Configuration → Visite guidée
2. Ou utilisez le raccourci "Démo rapide" dans le menu BET
    """,
    "author": "Nicolas JEUDY",
    "website": "https://github.com/alusage/juliennejavel-addons",
    "depends": [
        "web",
        "web_tour",
        "juliennejavel_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tour_launcher_views.xml",
        "views/tour_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "juliennejavel_tour/static/src/js/bet_tours.js",
            "juliennejavel_tour/static/src/js/simple_tour_launcher.js",
            "juliennejavel_tour/static/src/js/tour_helper.js",
            "juliennejavel_tour/static/src/css/tour_styles.css",
        ],
    },
    "installable": True,
    "auto_install": False,
}
