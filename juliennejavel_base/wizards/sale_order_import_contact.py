# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype
from datetime import datetime, date as datelib
import csv
from tempfile import NamedTemporaryFile
from collections import OrderedDict
import base64
import logging

logger = logging.getLogger(__name__)
try:
    import openpyxl  # for XLSX
except ImportError:
    logger.debug('Cannot import openpyxl')
try:
    import xlrd  # for XLS
except ImportError:
    logger.debug('Cannot import xlrd')
try:
    import rows  # for ODS
except ImportError:
    rows = None
    logger.debug('Cannot import rows')


GENERIC_CSV_DEFAULT_DATE = '%d/%m/%Y'
DELIMITER = {
    'coma': ',',
    'semicolon': ';',
    'tab': '\t',
    }


class SaleOrderImport(models.TransientModel):
    _name = "sale.order.import.contact"
    _description = "Sale Order Contact import"
    
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company)
    file_to_import = fields.Binary(string='File to Import')
    filename = fields.Char()

    # PIVOT FORMAT
    # [{
    #    'account': '411000',
    #    'analytic': 'ADM',  # analytic account code (100% distribution)
    # OR 'analytic': 'ADM:39.4,SUPP:60.6',  # analytic distribution
    #    'partner': 'R1242',
    #    'name': 'label',  # optional, for account.move.line
    #    'credit': 12.42,
    #    'debit': 0,
    #    'ref': '9804',  # optional
    #    'journal': 'VT',  # journal code
    #    'date': '2017-02-15',  # also accepted in datetime format
    #    'ref: 'X12',
    #    'move_name': 'OD/2022/1242',  # optional, for 'name' of account.move
    #                                  # only used when keep_odoo_move_name = False
    #    'reconcile_ref': 'A1242',  # will be written in import_reconcile
    #                               # and be processed after move line creation
    #    'line': 2,  # Line number for error messages.
    #                # Must be the line number including headers
    # },
    #  2nd line...
    #  3rd line...
    # ]

    def run_import(self):
        self.ensure_one()
        if not self.file_to_import:
            raise UserError(_("You must upload a file to import."))
        fileobj = NamedTemporaryFile('wb+', prefix='odoo-sale_import-', suffix='.xlsx')
        file_bytes = base64.b64decode(self.file_to_import)
        fileobj.write(file_bytes)
        fileobj.seek(0)  # We must start reading from the beginning !
        pivot = self.genericxlsx2pivot(fileobj)
        fileobj.close()
        #orders = self.create_order_from_pivot(pivot)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_quotations_with_onboarding")
        return action

    def clean_strip_pivot(self, pivot):
        for l in pivot:
            for key, value in l.items():
                if value:
                    if isinstance(value, str):
                        l[key] = value.strip() or False
                else:
                    l[key] = False

    def genericxlsx2pivot(self, fileobj):
        wb = openpyxl.load_workbook(fileobj.name, read_only=True)
        partner_obj = self.env['res.partner']
        sh = wb.active
        
        res = []
        i = 0
        for row in sh.rows:
            vals = {}
            i += 1
            if i == 1:
                continue
            if len(row) < 4:
                continue
            if not [item for item in row if item.value]:
                # skip empty line
                continue
            logger.info(row[1].value)
            partner_id = partner_obj.search([('ref', '=', row[0].value)], limit=1)
            if not partner_id:
                partner_id = partner_obj.create({
                    'name': row[1].value,
                    'city': row[4].value,
                    'street': row[2].value,
                    'zip': row[3].value,
                    'ref': row[0].value,
                    'phone': row[7].value,
                    'email': row[6].value,
                    'company_id': self.env.company.id,
                })
            if partner_id:
                partner_id.write({
                    'city': row[4].value,
                    'street': row[2].value,
                    'zip': row[3].value,
                    'phone': row[7].value,
                    'email': row[6].value,
                })
        return res

    
    def create_order_from_pivot(self, pivot):
        order = self.env['sale.order']
        company_id = self.company_id.id
        errors = {'other': []}
        ids = order.with_context(import_file=True).create(pivot)
        return ids