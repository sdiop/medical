# -*- coding: utf-8 -*-

import time
import datetime
from openerp.report import report_sxw
from openerp.osv import osv

class appointments_recipt_report(report_sxw.rml_parse):
        _name = 'report.appointments.recipt'
        def __init__(self, cr, uid, name, context):
            super(appointments_recipt_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
            })

report_sxw.report_sxw('report.appointments.recipt', 'medical.appointment', 'addons/medical/report/appointments_recipt.rml', parser=appointments_recipt_report, header=False )


