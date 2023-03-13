import json

from odoo import models, fields, api
import okcoinv5
from okcoinv5 import Account, Spot
import qrcode
import base64
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
    lightning_invoice_amount = fields.Char()
    lightning_invoice = fields.Char()
    lightning_deposit_status= fields.Char()
    qr_generated = fields.Char()
    deposit_qr = fields.Image()
    fund_transfer_id = fields.Char()

    def Testing(self):
        clik = okcoinv5.__file__
        self.test = str(clik)

    def Balance(self):
        balance = acc.get_asset_valuation(currency='USD')
        self.balance = json.dumps(balance.json)


    def Lightning_invoice(self):
        record_search = self.env['okcoin.model'].search([('name','=',self.name)])
        lightning_deposit_amount = record_search.mapped('lightning_invoice_amount')[0]
        lightning_deposit_invoice = acc.lightning_deposit(amount=lightning_deposit_amount)
        lightning_deposit_invoice_json = lightning_deposit_invoice.json
        self.lightning_invoice = lightning_deposit_invoice_json.get('data')[0].get('invoice')

    def Lightning_invoice_qr(self):
        record_search = self.env['okcoin.model'].search([('name','=',self.name)])
        record_lightning_invoice = record_search.mapped('lightning_invoice')[0]
        qrmessage = 'lightning:' + record_lightning_invoice
        encoded_qrmessage = qrmessage.encode()
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
        QRcode.add_data(qrmessage)
        QRimg = QRcode.make_image(fill_color="Black", back_color="white").convert('RGB')
        #QRimg_bytes = QRimg.tobytes("hex", "rgb")
        #encoded_qr = base64.b64encode(QRimg_bytes).decode('utf-8')
        output_file = '/opt/odoo16/addons/okcoin/static/src/img/QR.png'
        QRimg.save(output_file)
        self.qr_generated = 'QR created - ' + record_lightning_invoice

    def Lightning_invoice_qr_display(self):
        test = open('/opt/odoo16/addons/okcoin/static/src/img/QR.png', 'rb')
        btest = test.read()
        self.deposit_qr = base64.b64encode(btest)

    def Lightning_deposit_status(self):
        record_search = self.env['okcoin.model'].search([('name', '=', self.name)])
        lightning_invoice = record_search.mapped('lightning_invoice')[0]
        deposit_history = acc.get_deposit_history(currency='BTC')
        deposit_history_json = deposit_history.json
        deposits = deposit_history_json.get('data')
        for deposit in deposits:
            deposit_address = deposit.get('to')
            if deposit_address == lightning_invoice:
                self.lightning_deposit_status = 'payment found'
                deposit_state = deposit.get('state')
                if deposit_state == '2':
                    self.lightning_deposit_status = 'payment found and confirmed:' + lightning_invoice
                else:
                    print('payment found but not confirmed')
                break
            else:
                self.lightning_deposit_status = 'payment not found: something went wrong'

    def Account_transfer(self):
        record_search = self.env['okcoin.model'].search([('name', '=', self.name)])
        #lightning_deposit_amount = record_search.mapped('lightning_invoice_amount')[0]  amt=lightning_deposit_amount
        fund_transfer = acc.get_funds_transfer(ccy='BTC', amt=.00001, origin='6', destination='18')
        fund_transfer_json = fund_transfer.json
        try:
            fund_transfer_data = fund_transfer_json.get('data')[0].get('transId')
            self.fund_transfer_id = 'An account transfer has been initiated: ' + fund_transfer_data
        except:
            self.fund_transfer_id = 'An account transfer error was encountered: ' + json.dumps(fund_transfer_json)
