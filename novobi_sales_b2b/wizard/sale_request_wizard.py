from odoo import models
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)


class SaleRequestWizard(models.TransientModel):
    _name = 'sale.request.wizard'
    _description = 'Approve a batch of requests'

    def approve_request(self):
        request_ids = self.env.context['request_ids']
        requests = self.env['sale.request'].browse(request_ids)
        if requests.filtered(lambda sr: sr.request_state != 'pending'):
            raise UserError(
                'Only pending requests can be approved directly.')
        for request in requests:
            request.make_approved()
