# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Julienne Javel Base",
    "version": "16.0.1.0.0",
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
        "views/account_payment_view.xml",
        "views/account_move_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_state_view.xml",
        "views/sale_order_view.xml",
        "security/ir.model.access.csv",
        "wizards/sale_order_import_views.xml",
    ],
    "installable": True,
}
