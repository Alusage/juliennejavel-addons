# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Julienne Javel - Restrict contact and product creation",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Prevent creating contacts and products from quotations and "
    "invoices, except for a dedicated group",
    "author": "Elabore",
    "website": "https://github.com/alusage/juliennejavel-addons",
    "depends": [
        "account",
        "sale",
        # The duplicated fields reproduce the definitions of these modules
        "sale_management",
        "sale_product_configurator",
    ],
    "data": [
        "security/groups.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
}
