from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
#from openerp import netsvc

class appointment_wizard(osv.osv_memory):
    
    _name = 'appointment.wizard'
    _description = "This is form for view of tender"
    
    _columns = {
            'phy_id':fields.many2one("medical.physician",'Name Of Physician', required=True),
           # 'doctor' : fields.many2one ('res.partner','Physician', domain=[('is_doctor', '=', "1")], help="Physician's Name"),
            'a_date': fields.date('Appointment Date', required=True, select=1), 
           } 
    
    def show_record(self, cr, uid, ids, context=None):
        
        v=[]
        sum=0
        q = self.browse(cr,uid,ids)
        print "&&&&&&&&&&&&&&&&&&&&&&&          i m in"
        for q1 in q:
           print "&&&&&&&&&&&&&&&&&&&&&&&",q1.phy_id.id
#            z=self.pool.get('medical.physician').browse(cr, uid, q1.phy_id.id)
#            print "zzzzzzzzzzzzzzzzzzzzz",z
           rec= self.pool.get('medical.appointment').search(cr,uid,[('doctor','=',q1.phy_id.id),('state','=','confirmed')]) 
          
           obj = self.pool.get('medical.appointment')
           res = obj.browse(cr, uid, rec)
           for r in res:
             print "&&&&&&&&&&&&&&&&&&&&&&&"
             b_day = datetime.strptime(str(r.appointment_sdate), '%Y-%m-%d %H:%M:%S')
             if ((str(b_day.date())== q1.a_date)):
                v.append (r.id ) 
                
        return{'type':'ir.actions.act_window',
               'name':'Appointments',
               
               'res_model':'medical.appointment',
               'view_type':'form',
               'view_mode':'tree,form',
               'context': context,
               'domain':[('id','in',v) ,],}  
           
           
           
appointment_wizard()   
              