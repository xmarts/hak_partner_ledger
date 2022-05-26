from odoo import fields,models
class PartnerLedger(models.TransientModel):

    _name = 'partner.ledger'

    start_date = fields.Date(string='From Date', required=True, default=fields.Date.today().replace(day=1))
    end_date = fields.Date(string='To Date', required=True, default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, help='Select Partner for movement')


    def print_report(self):
        data = {'partner_id': self.partner_id.id,'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('hak_partner_ledger.partner_ledger_pdf').report_action(self,data)

class CustomReport(models.AbstractModel):
    _name = "report.hak_partner_ledger.hak_partner_ledger_pdf_report"

    def _get_report_values(self, docids, data=None):
        cr = self._cr
        query = """select sum(l.debit - l.credit) as opening_bal
from account_move_line l
join account_move m on l.move_id = m.id
join account_account a on l.account_id = a.id
where a.reconcile = True
        and l.partner_id = %s and l.date < %s
        """
        cr.execute(query, [data['partner_id'], data['start_date']])
        openbal = cr.dictfetchall()

        cr = self._cr
        query = """
        select m.ref,m.name as doc_no, m.date, m.narration, j.name as journal, p.name as partner_name, 
l.name as line_desc, a.name as gl_account, m.currency_id, l.debit, l.credit
from account_move_line l
join account_move m on l.move_id = m.id
join res_partner p on l.partner_id = p.id
join account_account a on l.account_id = a.id
join account_journal j on m.journal_id = j.id
where a.reconcile = True
        and l.partner_id = %s and (m.date between %s and %s)
        order by m.date
        """
        cr.execute(query, [data['partner_id'], data['start_date'], data['end_date']])
        dat = cr.dictfetchall()
        print(dat)

        return {
            'doc_ids': self.ids,
            'doc_model': 'partner.ledger',
            'openbal': openbal,
            'dat': dat,
            'data': data,
        }