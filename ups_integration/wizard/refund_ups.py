from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp.addons.ups_integration.models import shippingservice
import datetime
import logging
import time
import commands
_logger = logging.getLogger(__name__)


class refund_request(models.TransientModel):
    _inherit = "refund.request"


    @api.multi
    def action_refund_request_ups(self):
        '''
        This function is used to Cancel shipping label based on the carrier type choosen in the deilvery order
        parameters: 
            No Parameters
        '''
        shipping_obj = self.env['shipping.ups']
        stock_obj = self.env['stock.picking']
        attach_object = self.env['ir.attachment']
        active_ids = self._context.get('active_ids')
        shipping_ids = shipping_obj.search([])
        ship_data = shipping_ids[0]
        ups_info = self.env['shipping.ups'].get_ups_info()
        lic = ship_data.access_license_no
        user_id = ship_data.user_id
        passw = ship_data.password
        ups_response = {}
        for stock_data in stock_obj.browse(active_ids):
            shpindentnumber = stock_data.carrier_tracking_ref
            split_car = shpindentnumber.split('\n')
            _logger.error('ssplit_carsplit_carr=>%s', split_car)
            for i_car in split_car:
                if i_car:
                    try:
                        cancel = shippingservice.UPSRefundRequest(ups_info, i_car)
                        ups_response = cancel.send()
                    except Exception, e:
                        _logger.error('Quotes Wizard Exception: %s', e)
                        data_val_1 = stock_data.error_for_faulty
                        if not data_val_1:
                            data_val_1 = " "
                        log_data = stock_data.write({'error_for_faulty': '*' + str(data_val_1) + str(e) + '\n','is_faulty_deliv_order': True})
                        self._cr.commit()
                        pass
                    if ups_response.get('status_code') == '1':
                        stock_data.write({'is_ups_cancel_consign' : True, 'label_printed' : False, 'label_printed_datetime': False, 'label_generated': False} )
                        self._cr.commit()
                        attach_ids = attach_object.search([('res_id', '=', stock_data.id)])
                        if attach_ids:
                            for id_att in attach_ids:
                                id_att.unlink()
        return True
    
    
refund_request()    