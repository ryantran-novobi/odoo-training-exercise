from odoo import models, fields
import logging
import dateutil.parser
logger = logging.getLogger(__name__)


class DeliveryOrder(models.Model):
    _name = 'stock.picking.sent.email'
    _inherit = 'stock.picking'
    _description = "Delivery Orders Done Sent Email"

    def _cron_automatic_sent_email(self):
        logger.info('Running Automatic Sent Email To Done Delivery Order')
        for record in self.filtered(lambda r: dateutil.parser.parse(r.date_done).date() == fields.Date.today()):
            email_template = self.env.ref('novobi_sales_b2b.mail_template')
            email_template.send_mail(record.id, force_send=True)
