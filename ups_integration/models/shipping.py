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

class shipping_ups(models.Model):
    _name = 'shipping.ups'

    def get_ups_info(self):
        '''
        This function is used to Get UPS based Information from UPS setting
        parameters: 
            No Parameters
        '''
        ship_ups_id = self.search([('active','=',True)])
        if not ship_ups_id:
            context = dict(self._context or {})
            ### This is required because when picking is created when saleorder is confirmed and if the default parameter has some error then it should not stop as the order is getting imported from external sites
            if 'error' not in context.keys() or context.get('error',False):
                raise Exception('Active UPS settings not defined')
            else:
                return False
        else:
            ship_ups_id = ship_ups_id[0]
        return ship_ups_id

    name = fields.Char(string='Name', size=64, required=True, translate=True)
    access_license_no = fields.Char(string='Access License Number', size=64, required=True)
    user_id = fields.Char(string='UserID', size=64, required=True)
    password = fields.Char(string='Password', size=64, required=True)
    shipper_no = fields.Char(string='Shipper Number', size=64, required=True)
    payment_method = fields.Selection([('account_number','Account Number'),('credit_card','Credit Card')], string='Payment Method')
    credit_card_type = fields.Char(string='Credit Card Type', size=64)
    credit_card_number = fields.Char(string='Credit Card number', size=64)
    card_expiration = fields.Char(string='Card Expiration', size=64)
    test = fields.Boolean(string='Is test?')
    active = fields.Boolean(string='Active', default=True)
    measurement_ups = fields.Selection([('KGS','KGS'),('LBS','LBS')],'Measurement', default='KGS')
    config_shipping_address_id = fields.Many2one('res.partner', "shipping Address")
        
        
shipping_ups()