{
    "name": "Mail Tracking Export",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "summary": "Export mail tracking value changes to XLSX",
    "author": "Julienne Javel",
    "license": "LGPL-3",
    "depends": ["mail"],
    "external_dependencies": {"python": ["xlsxwriter"]},
    "data": [
        "security/ir.model.access.csv",
        "wizards/mail_tracking_export_wizard_views.xml",
    ],
    "installable": True,
}
