# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
#    Author: [Teckzilla Software Solutions]  <[sales@teckzilla.net]>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import UserError
from openerp.addons.base_module_shipping.models.miscellaneous import Address
import shippingservice
import cStringIO
from base64 import b64decode
from base64 import b64encode
import Image
import StringIO
import binascii
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen import canvas
import base64
import os

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    def _get_shipping_type(self):
        '''
        This function is used to Get Add UPS in Shipping type drop down id this module is installed
        parameters: 
            No Parameters
        '''
        res = super(stock_picking, self)._get_shipping_type()
        res.append(('UPS','UPS'))
        return res

    def _get_packaging_type_ups(self):
        return [
            ('00','Unknown'),
            ('01','Letter'),
            ('02','Package'),
            ('03','Tube'),
            ('04','Pack'),
            ('21','Express Box'),
            ('24','25Kg Box'),
            ('25','10Kg Box'),
            ('30','Pallet'),
            ('2a','Small Express Box'),
            ('2b','Medium Express Box'),
            ('2c','Large Express Box'),
        ]


    def _get_service_type_ups(self):
        return [
             ('01','Next Day Air'),
            ('02','Second Day Air'),
            ('03','Ground'),
            ('07','Worldwide Express'),
            ('08','Worldwide Expedited'),
            ('11','Standard'),
            ('12','Three-Day Select'),
            ('13','Next Day Air Saver'),
            ('14','Next Day Air Early AM'),
            ('54','Worldwide Express Plus'),
            ('59','Second Day Air AM'),
            ('65','Saver'),
            ('86','Express Saver'),
        ]
    
    pickup_type_ups = fields.Selection([
            ('01','Daily Pickup'),
            ('03','Customer Counter'),
            ('06','One Time Pickup'),
            ('07','On Call Air'),
            ('11','Suggested Retail Rates'),
            ('19','Letter Center'),
            ('20','Air Service Center'),
        ], string='Pickup Type')
    shipping_type = fields.Selection(_get_shipping_type,'Shipping Type')
    service_type_ups = fields.Selection(_get_service_type_ups, string='Service Type', size=100)
    packaging_type_ups = fields.Selection(_get_packaging_type_ups, string='Packaging Type', size=100)
    
stock_picking() 

class shipping_response(models.Model):
    _inherit = 'shipping.response'
    
    @api.multi
    def generate_ups_tracking_no(self, picking_id):
        '''
        This function is used to Generated UPS Shipping Label in Delivery order
        parameters: 
            picking_id : (int) stock picking ID,(delivery order ID)
        '''
        context = dict(self._context or {})
        ups_obj = self.env['shipping.ups']
        sale_obj = self.env['sale.order']
        sale_id = sale_obj.search([('name', '=', picking_id.origin)])
        ups_info = self.env['shipping.ups'].get_ups_info()
        ups_attachment_pool = self.env['ir.attachment']
        stockpicking_obj = self.env['stock.picking']
        ss = sale_obj.browse(sale_id.id)
        ups_data = ups_obj.search([])
        if not len(ups_data):
            raise UserError(_("UPS Configuration Not Defined"))
        payment_type = ups_data.payment_method
        type_code = ups_data.credit_card_type
        credit_number = ups_data.credit_card_number
        expiration = ups_data.card_expiration
        shipper_number = ups_data.shipper_no
        if payment_type == 'credit_card':
            payment = """<PaymentInformation>
                        <Prepaid>
                        <BillShipper>
                             <CreditCard>
                                 <Type>%s</Type>
                                 <Number>%s</Number>
                                 <ExpirationDate>%s</ExpirationDate>
                             </CreditCard>
                        </BillShipper>
                    </Prepaid>
                 </PaymentInformation>"""% (type_code,credit_number,expiration)
        if payment_type == 'account_number':
            payment = """<PaymentInformation>
                    <Prepaid>
                    <BillShipper>
                         <AccountNumber>%s</AccountNumber>
                    </BillShipper>
                </Prepaid>
             </PaymentInformation>"""% (shipper_number)
        
        
        pickup_type_ups = picking_id.pickup_type_ups
        service_type_ups = picking_id.service_type_ups
        packaging_type_ups = picking_id.packaging_type_ups

        reference = ''
        reference_code = ''
        count = 1
        for move_line in picking_id.move_lines:
            reference_code += '('+str(int(move_line.product_qty))+')'
            if move_line.product_id.default_code:
                reference_code +=  str(move_line.product_id.default_code)
                reference += '''<ReferenceNumber>
                                       <Code>%s</Code>
                                       <Value>%s</Value></ReferenceNumber>''' % (count,reference_code)
                reference_code = ''
                
                break
                count += 1
        reference += '''<ReferenceNumber>
                                       <Code>%s</Code>
                                       <Value>%s</Value></ReferenceNumber>''' % (count,ups_data.config_shipping_address_id.name)
        reference = ''
        weight = picking_id.weight_package
        if not weight:
            raise osv.except_osv(_('Error'), _('Package Weight Invalid!'))

        ### Shipper
        shipper_address = ups_data.config_shipping_address_id
        if not shipper_address:
            raise osv.except_osv(_('Error'), _('Shipping Address not defined!'),)
        shipper = Address(shipper_address.name or shipper_address.name, shipper_address.street, shipper_address.street2 or '', shipper_address.city, shipper_address.state_id.code or '', shipper_address.zip, shipper_address.country_id.code, shipper_address.phone or '', shipper_address.email, shipper_address.name)

        ### Recipient
        cust_address = picking_id.partner_id
        receipient = Address(picking_id.name or picking_id.name, cust_address.street, cust_address.street2 or '', cust_address.city, cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code, cust_address.phone or '', cust_address.email, cust_address.name)
#        try:
        ups = shippingservice.UPSShipmentConfirmRequest(ups_info, pickup_type_ups, service_type_ups, packaging_type_ups, weight, shipper, receipient,reference,payment)
        ups_response = ups.send()
        ups = shippingservice.UPSShipmentAcceptRequest(ups_info, ups_response.shipment_digest)
        ups_response = ups.send()
#        except Exception, e:
#            raise Exception('UPS Error!!: %s' % e)
        im_barcode = cStringIO.StringIO(b64decode(ups_response.graphic_image)) # constructs a StringIO holding the image
        img_barcode = Image.open(im_barcode)
        output = StringIO.StringIO()
        img=img_barcode.rotate(-90)
        img.save(output, format='PNG')
        data = binascii.b2a_base64(output.getvalue())
        f = open('/tmp/test.png', 'wb')
        f.write(output.getvalue())
        f.close()
        c = canvas.Canvas("/tmp/picking_list.pdf")
        c.setPageSize((400, 650))
        c.drawImage('/tmp/test.png',10,10,380,630)
        c.save()
        
        f = open('/tmp/picking_list.pdf', 'rb')
        ups_data_attach = {
            'name': 'PackingList.pdf', 
            'datas': base64.b64encode(f.read()),
            'description': 'Packing List',
            'res_name': picking_id.name,
            'res_model': 'stock.picking',
            'res_id': picking_id.id,
        }
        f.close()
        ups_attach_id = ups_attachment_pool.search([('res_id','=',picking_id.id),('res_name','=',picking_id.name)])
        if not ups_attach_id:
            ups_attach_id = ups_attachment_pool.create(ups_data_attach)
            os.remove('/tmp/test.png')
            os.remove('/tmp/picking_list.pdf')
        else:
            ups_attach_result = ups_attach_id[0].write(ups_data_attach)
            ups_attach_id = ups_attach_id[0]
            
        update=picking_id.write({'carrier_tracking_ref':ups_response.tracking_number, 'shipping_rate':ups_response.rate, 'shipping_label':binascii.b2a_base64(str(b64decode(ups_response.graphic_image),))})
        ss.write({'client_order_ref':ups_response.tracking_number})
        context['track_success'] = True
        context['tracking_no'] = ups_response.tracking_number
        return True
    
    
    
