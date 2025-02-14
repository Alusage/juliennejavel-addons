from odoo import api, models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_mode_id = fields.Many2one(
        'account.payment.mode',
        string='Payment Mode',
        help='The payment mode associated with this payment.'
    )

    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        if self.payment_mode_id:
            for method in self.available_payment_method_line_ids:
                if method.payment_method_id == self.payment_mode_id.payment_method_id:
                    payment_method_line_id = method
            self.payment_method_line_id = payment_method_line_id