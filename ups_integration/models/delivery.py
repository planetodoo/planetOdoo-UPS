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

   
class delivery_carrier(models.Model):
    _inherit = "delivery.carrier"
    
    is_ups = fields.Boolean('Is UPS', help="If the field is set to True, it will consider it as UPS service type.")
    
delivery_carrier()

class product_category_shipping(models.Model):
    _inherit = "product.category.shipping"
    
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
    service_type_ups = fields.Selection(_get_service_type_ups, string='Service Type UPS')
    packaging_type_ups = fields.Selection(_get_packaging_type_ups, string='Packaging Type UPS')
    
    

product_category_shipping()

class product_product_shipping(models.Model):
    _inherit = "product.product.shipping"
    
    
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
        
    service_type_ups = fields.Selection(_get_service_type_ups, string='Service Type UPS')
    packaging_type_ups = fields.Selection(_get_packaging_type_ups, string='Packaging Type UPS')
    
product_product_shipping()


