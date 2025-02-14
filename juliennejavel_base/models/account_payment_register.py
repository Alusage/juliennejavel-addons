from odoo import api,models, fields

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_mode_id = fields.Many2one('account.payment.mode', string='Payment Mode')

    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        if self.payment_mode_id:
            for method in self.available_payment_method_line_ids:
                if method.payment_method_id == self.payment_mode_id.payment_method_id:
                    payment_method_line_id = method
            self.payment_method_line_id = payment_method_line_id

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals['payment_mode_id'] = self.payment_mode_id.id
        return payment_vals