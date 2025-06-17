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
    _name = "sale.order.import"
    _description = "Sale Order import"
    
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
        orders = self.create_order_from_pivot(pivot)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_quotations_with_onboarding")
        if len(orders) == 1:
            action.update({
                'view_mode': 'form,list',
                'res_id': orders[0].id,
                'view_id': False,
                'views': False,
                })
        else:
            action.update({
                'view_mode': 'kanban,list,form',
                'domain': [('id', 'in', orders.ids)],
                })
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
        order_obj = self.env['sale.order']
        so_template_obj = self.env['sale.order.template']
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
            partner_id = partner_obj.search([('ref', '=', row[1].value)], limit=1)
            if not partner_id:
                partner_id = partner_obj.create({
                    'name': row[3].value,
                    'city': row[4].value,
                    'ref': row[1].value,
                    'company_id': self.env.company.id,
                })
            if partner_id:
                partner_id.write({
                    'city': row[4].value,
                })
                order_id = order_obj.search([('partner_id', '=', partner_id.id)], limit=1)
                
                sale_template_id = so_template_obj.search([('name', 'ilike', 'MAR')], limit=1)
                if row[11].value == 1:
                    sale_template_id = so_template_obj.search([('name', 'ilike', 'OPAH')], limit=1)
                if row[47].value == 6500:
                    sale_template_id = so_template_obj.search([('name', 'ilike', 'Client TZEE')], limit=1)
                    
                if row[47].value == 850:
                    copy_order = order_obj.search([('name', '=', 'S00004')], limit=1)
                    if copy_order:
                        new_id = copy_order.copy()
                        new_id.write({
                            'partner_id': partner_id.id,
                        })
                        sale_template_id = False

                if sale_template_id:
                    vals.update({
                        'partner_id': partner_id.id,
                        'sale_order_template_id': sale_template_id.id,
                        'order_line': [],
                    })
                    vals = order_obj.play_onchanges(vals, ['partner_id'])
                    for line in sale_template_id.sale_order_template_line_ids:
                        vals['order_line'].append((0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom': line.product_uom_id.id,
                            'name': line.name,
                            'display_type': line.display_type,
+                           'sequence': line.sequence,
                        }))
                    logger.info(vals)
                    res.append(vals)
            
        return res

    
    def create_order_from_pivot(self, pivot):
        order = self.env['sale.order']
        company_id = self.company_id.id
        errors = {'other': []}
        ids = order.with_context(import_file=True).create(pivot)
        return ids