import json

from odoo import models, fields, api
import okcoinv5
from okcoinv5 import Account, Spot
import okcoin
import sysconfig

acc = Account('/home/odoo16/Downloads/auth.config')
sp = Spot('/home/odoo16/Downloads/auth.config')


class OkcoinModel(models.Model):
    _name = 'okcoin.model'
    _description = 'Table of API connection info'

    name = fields.Char()
    api_key = fields.Char()
    secret = fields.Char()
    password = fields.Char()
    maker_taker = fields.Selection([('taker', 'Taker'), ('maker', 'Maker'), ('smart', 'Smart')], string='Maker, Taker, or Smart Orders')
    convert_percent = fields.Integer()
    over_percent = fields.Integer()
    test = fields.Char()
    balance = fields.Char()
    linvoice_amount = fields.Char()
    lightning_invoice=fields.Char()

    def Testing(self):
        clik = okcoinv5.__file__
        self.test = str(clik)

    def Balance(self):
        balance = acc.get_asset_valuation(currency='USD')
        self.balance = json.dumps(balance.json)

    def Lightning_invoice(self):
        model_create = self.env['okcoin.model']
        content_list = model_create._fields['linvoice_amount'].get
        self.lightning_invoice = str(content_list)
        #hjhkjh
        #lightning = acc.lightning_deposit(amount=self.amount_create)
        #self.lightning_invoice = json.dumps(lightning.json)