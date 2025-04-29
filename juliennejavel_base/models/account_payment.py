import logging
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    sepa_reverted = fields.Boolean(
        string="SEPA Revert",
        help="checked id sepa is reverted.",
        default=False,
    )
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        help="The payment mode associated with this payment.",
    )

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        if self.payment_mode_id:
            for method in self.available_payment_method_line_ids:
                if method.payment_method_id == self.payment_mode_id.payment_method_id:
                    payment_method_line_id = method
            self.payment_method_line_id = payment_method_line_id

    def action_payment_revert(self):
        """This method is called when the payment is returned from the payment
        acquirer. It will update the payment state and create a new move line
        for the payment.
        """
        self.ensure_one()
        for move_line in self.move_id.line_ids:
            invoice_due_dates = []
            
            if move_line.reconciled and move_line.matched_debit_ids.debit_move_id.move_type == 'out_invoice':
                invoice = move_line.matched_debit_ids.debit_move_id.move_id
                _logger.info("Move line type %s", move_line.move_id.move_type)
                invoice_due_dates = invoice.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable').mapped('date_maturity')
                old_move_line = move_line.matched_debit_ids.debit_move_id    
            if move_line.reconciled:
                move_line.remove_move_reconcile()
            if invoice_due_dates:
                max_due_date = max(invoice_due_dates)
                _logger.info("Max due date: %s", max_due_date)
                old_move_line.date_maturity = max_due_date + relativedelta(months=1)

        reversed_move = self.move_id._reverse_moves(default_values_list=[{
            'ref': f"Annulation de: {self.move_id.name} (Refus SEPA)",
        }], cancel=True)
        self.sepa_reverted = True
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


