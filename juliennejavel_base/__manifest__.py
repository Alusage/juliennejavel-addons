# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Julienne Javel Base",
    "version": "16.0.2.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Julienne Javel Base",
    "author": "Nicolas JEUDY",
    "website": "https://github.com/alusage/juliennejavel-addons",
    "depends": [
        "account",
        "account_move_export",
        "account_payment_mode",
        "sale",
        "sales_team",
        "sale_management",
        "onchange_helper",
    ],
    "data": [
        #"data/bet_saleorder_template.csv",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/account_payment_view.xml",
        "views/account_move_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_state_view.xml",
        "views/sale_order_view.xml",
        "views/menu.xml",
        "wizards/sale_order_import_views.xml",
        "wizards/sale_order_import_views_contact.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "juliennejavel_base/static/src/css/kanban_colors.css",
        ],
    },
    "installable": True,
}
