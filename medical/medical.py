# coding=utf-8

#    Copyright (C) 2008-2010  Luis Falcon

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import openerp
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools import ustr
from openerp.tools.translate import _

class medical_domiciliary_unit(osv.osv):
	_name = "medical.domiciliary.unit"
	_description = "Domiciliary Unit"
	
	_columns = {
	'name' : fields.char ('Code', required=True),
	'desc' : fields.char ('Desc'),
	'address_street' : fields.char ('Street'),
	'address_street_number' : fields.integer('Number'),
	'address_street_bis' : fields.char ('Apartment',),
	'address_district' : fields.char ('District', help="Neighborhood, Village, Barrio...."),
	'address_municipality' : fields.char ('Municipality', help="Municipality, Township, county .."),
    'address_city' : fields.char ('City'),
    'address_zip' : fields.char ('Zip Code'),
    'address_country': fields.many2one('res.country', 'Country',help='Country'),
    'state_id': fields.many2one("res.country.state", 'Province',),
    'operational_sector' :fields.many2one ('medical.operational_sector','Operational Sector'),
    'picture' : fields.binary('Picture'),
    'latitude' : fields.char ('Latitude'),
    'longitude' : fields.char ('Longitude'),
    'urladdr' : fields.char('OSM Map',help="Locates the DU on the Open Street Map by default"),
    # Infrastructure
    'dwelling' : fields.selection([
        (None, ''),
        ('single_house', 'Single / Detached House'),
        ('apartment', 'Apartment'),
        ('townhouse', 'Townhouse'),
        ('factory', 'Factory'),
        ('building', 'Building'),
        ('mobilehome', 'Mobile House'),
        ], 'Type', sort=False),

    'materials' : fields.selection([
        (None, ''),
        ('concrete', 'Concrete'),
        ('adobe', 'Adobe'),
        ('wood', 'Wood'),
        ('mud', 'Mud / Straw'),
        ('stone', 'Stone'),
        ], 'Material', sort=False),

    'roof_type' : fields.selection([
        (None, ''),
        ('concrete', 'Concrete'),
        ('adobe', 'Adobe'),
        ('wood', 'Wood'),
        ('mud', 'Mud'),
        ('thatch', 'Thatched'),
        ('stone', 'Stone'),
        ], 'Roof', sort=False),

    'total_surface' : fields.integer('Surface', help="Surface in sq. meters"),
    'bedrooms' : fields.integer('Bedrooms'),
    'bathrooms' : fields.integer('Bathrooms'),

    'housing' : fields.selection([
        (None, ''),
        ('0', 'Shanty, deficient sanitary conditions'),
        ('1', 'Small, crowded but with good sanitary conditions'),
        ('2', 'Comfortable and good sanitary conditions'),
        ('3', 'Roomy and excellent sanitary conditions'),
        ('4', 'Luxury and excellent sanitary conditions'),
        ], 'Conditions',
        help="Housing and sanitary living conditions", sort=False),

    'sewers' : fields.boolean('Sanitary Sewers'),
    'water' : fields.boolean('Running Water'),
    'trash' : fields.boolean('Trash recollection'),
    'electricity' : fields.boolean('Electrical supply'),
    'gas' : fields.boolean('Gas supply'),
    'telephone' : fields.boolean('Telephone'),
    'television' : fields.boolean('Television'),
    'internet' : fields.boolean('Internet'),
    'members_ids' : fields.one2many('res.partner', 'du_id', 'Members', readonly=True),
   
	}
	
	_sql_constraints = [
                ('name_uniq', 'UNIQUE(name)','The Domiciliary Unit must be unique !'),
                ]
medical_domiciliary_unit()

class insurance_plan(osv.osv):
	_name = "medical.insurance.plan"
	
	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res
	
	_columns = {
    'name' : fields.many2one('product.product', 'Plan', required=True,
        domain=[('type', '=', 'service'), ('is_insurance_plan', '=', True)],help='Insurance company plan'),
    'company' : fields.many2one('res.partner','Insurance Company',domain=[('is_insurance_company', '=', "1")],required=True, ),
    'is_default' : fields.boolean('Default plan',help='Check if this is the default plan when assigning this insurance company to a patient'),
    'notes' : fields.text('Extra info'),
    }

insurance_plan()

class insurance (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['number','company'], context)
		res = []
		for record in reads:
			name = record['number']
			if record['company']:
				name = record['company'][1] + ': ' +name
			res.append((record['id'], name))
		return res

	_name = "medical.insurance"
	_columns = {
		'name' : fields.many2one ('res.partner','Owner'), 
		'number' : fields.char ('Number', size=64,required=True),
		'company' : fields.many2one ('res.partner','Insurance Company',domain=[('is_insurance_company', '=', "1")],required=True,),
		'member_since' : fields.date ('Member since'),
		'member_exp' : fields.date ('Expiration date'),
		'category' : fields.char ('Category', size=64, help="Insurance company plan / category"),
		'type' : fields.selection([('state','State'),('labour_union','Labour Union / Syndical'),('private','Private'),], 'Insurance Type'),
		'notes' : fields.text ('Extra Info'),
		'plan_id' : fields.many2one('medical.insurance.plan', 'Plan',help='Insurance company plan'),
		}
	
insurance ()

class partner_patient (osv.osv):
	_name = "res.partner"
	_inherit = "res.partner"
	_columns = {
		'date' : fields.date('Partner since',help="Date of activation of the partner or patient"),
		'alias' : fields.char('alias', size=64),
		'ref': fields.char('ID Number', size=64),
        'is_person' : fields.boolean('Person', help="Check if the partner is a person."),
        'is_patient' : fields.boolean('Patient', help="Check if the partner is a patient"),
        'is_doctor' : fields.boolean('Doctor', help="Check if the partner is a doctor"),
		'is_institution' : fields.boolean ('Institution', help="Check if the partner is a Medical Center"),
		'is_insurance_company' : fields.boolean('Insurance Company', help="Check if the partner is a Insurance Company"),
        'is_pharmacy' : fields.boolean('Pharmacy', help="Check if the partner is a Pharmacy"),
		'lastname' : fields.char('Last Name', size=128, help="Last Name"),
		'insurance' : fields.one2many ('medical.insurance','company',"Insurance"),	
		'user_id1': fields.many2one('res.users', 'Internal User', help='In Medical is the user (doctor, nurse) that logins into OpenERP that will relate to the patient or family. When the partner is a doctor or a health proffesional, it will be the user that maps the doctor\'s partner name. It must be present.'),
		'du_id' : fields.many2one ('medical.domiciliary.unit','Domiciliary Unit'), 
	}
        _sql_constraints = [
                ('ref_uniq', 'unique (ref)', 'The partner or patient code must be unique')
 		]

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name', 'lastname'], context)
		res = []
		for record in reads:
			name = record['name']
			if record['lastname']:
				name = record['lastname'] + ', '+name
			res.append((record['id'], name))
		return res
	
# 	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
#         	args2 = args[:]
#         	if name:
#             		args += [('name', operator, name)]
#             		args2 += [('lastname', operator, name)]
#         	ids = self.search(cr, uid, args, limit=limit)
#         	ids += self.search(cr, uid, args2, limit=limit)
#         	res = self.name_get(cr, uid, ids, context)
#         	return res

partner_patient ()

class product_medical (osv.osv):
	_name = "product.product"
	_inherit = "product.product"
	_columns = {
                'is_medicament' : fields.boolean('Medicament', help="Check if the product is a medicament"),
                'is_vaccine' : fields.boolean('Vaccine', help="Check if the product is a vaccine"),
                'is_bed' : fields.boolean('Bed', help="Check if the product is a bed on the medical center"),
                'is_insurance_plan' : fields.boolean('Insurance Plan',help='Check if the product is an insurance plan'),
				'is_medical_supply' : fields.boolean('Medical Supply',help='Check if the product is a medical supply'),
	}
product_medical ()

class partner_patient_address (osv.osv):
	_name = "res.partner"
	_inherit = "res.partner"
	_columns = {
		'relationship' : fields.char('Relationship', size=64, help="Include the relationship with the patient - friend, co-worker, brother, ...- "),
		'relative_id' : fields.many2one('res.partner','Relative Partner ID', domain=[('is_patient', '=', True)], help="If the relative is also a patient, please include it here"),
	}
partner_patient_address ()

class procedure_code (osv.osv):
	_description = "Medical Procedure"
	_name = "medical.procedure"
	_columns = {
		'name': fields.char ('Code', size=128, required=True),
		'description' : fields.char ('Long Text', size=256),
		}

	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        	args2 = args[:]
        	if name:
            		args += [('name', operator, name)]
            		args2 += [('description', operator, name)]
        	ids = self.search(cr, uid, args, limit=limit)
        	ids += self.search(cr, uid, args2, limit=limit)
        	res = self.name_get(cr, uid, ids, context)
        	return res

procedure_code ()

class pathology_category(osv.osv):
        def name_get(self, cr, uid, ids, context={}):
                if not len(ids):
                        return []
                reads = self.read(cr, uid, ids, ['name','parent_id'], context)
                res = []
                for record in reads:
                        name = record['name']
                        if record['parent_id']:
                                name = record['parent_id'][1]+' / '+name
                        res.append((record['id'], name))
                return res

        def _name_get_fnc(self, cr, uid, ids, prop, foo, faa):
                res = self.name_get(cr, uid, ids)
                return dict(res)
        def _check_recursion(self, cr, uid, ids):
                level = 100
                while len(ids):
                        cr.execute('select distinct parent_id from medical_pathology_category where id in ('+','.join(map(str,ids))+')')
                        ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                        if not level:
                                return False
                        level -= 1
                return True

        _description='Disease Categories'
        _name = 'medical.pathology.category'
        _columns = {
                'name': fields.char('Category Name', required=True, size=128),
                'parent_id': fields.many2one('medical.pathology.category', 'Parent Category', select=True),
                'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
                'child_ids': fields.one2many('medical.pathology.category', 'parent_id', 'Children Category'),
                'active' : fields.boolean('Active'),
        }
        _constraints = [
                (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
        ]
        _defaults = {
                'active' : lambda *a: 1,
        }
        _order = 'parent_id,id'

pathology_category()

class pathology (osv.osv):
	_name = "medical.pathology"
	_description = "Diseases"
	_columns = {
		'name' : fields.char ('Name',required=True, size=128, help="Disease name"),
		'code' : fields.char ('Code', size=32,required=True, help="Specific Code for the Disease (eg, ICD-10, SNOMED...)"),
		'category' : fields.many2one('medical.pathology.category','Disease Category'),
		'chromosome' : fields.char ('Affected Chromosome', size=128, help="chromosome number"),
		'protein' : fields.char ('Protein involved', size=128, help="Name of the protein(s) affected"),
		'gene' : fields.char ('Gene', size=128, help="Name of the gene(s) affected"),
		'info' : fields.text ('Extra Info'),
		'line_ids' : fields.one2many('medical.pathology.group.member', 'name',
        'Groups', help='Specify the groups this pathology belongs. Some'
        ' automated processes act upon the code of the group'),
	}

        _sql_constraints = [
                ('code_uniq', 'unique (code)', 'The disease code must be unique')]

	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        	args2 = args[:]
        	if name:
            		args += [('name', operator, name)]
            		args2 += [('code', operator, name)]
        	ids = self.search(cr, uid, args, limit=limit)
        	ids += self.search(cr, uid, args2, limit=limit)
        	res = self.name_get(cr, uid, ids, context)
        	return res

pathology ()

class pathology_group(osv.osv):
        _description='Pathology Group'
        _name = 'medical.pathology.group'
        _columns = {
                'name': fields.char('Name',size=128, required=True, translate=True,help='Group name'),
    			'code' : fields.char('Code',size=128, required=True,
       						help='for example MDG6 code will contain the Millennium Development'
        	    			' Goals # 6 diseases : Tuberculosis, Malaria and HIV/AIDS'),
    			'desc' : fields.char('Short Description',size=128,required=True),
       			'info' : fields.text('Detailed information'),
        }

pathology_group()

class pathology_group_member(osv.osv):
        _description='Pathology Group Member'
        _name = 'medical.pathology.group.member'
        _columns = {
                'name' : fields.many2one('medical.pathology','Disease',readonly=True),
                'disease_group' : fields.many2one('medical.pathology.group','Group',required=True),
        }

pathology_group_member()

class medicament_category(osv.osv):
        def name_get(self, cr, uid, ids, context={}):
                if not len(ids):
                        return []
                reads = self.read(cr, uid, ids, ['name','parent_id'], context)
                res = []
                for record in reads:
                        name = record['name']
                        if record['parent_id']:
                                name = record['parent_id'][1]+' / '+name
                        res.append((record['id'], name))
                return res

        def _name_get_fnc(self, cr, uid, ids, prop, foo, faa):
                res = self.name_get(cr, uid, ids)
                return dict(res)
               
        def _check_recursion(self, cr, uid, ids):
                level = 100
                while len(ids):
                        cr.execute('select distinct parent_id from medical_pathology_category where id in ('+','.join(map(str,ids))+')')
                        ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                        if not level:
                                return False
                        level -= 1
                return True

        _description='Medicament Categories'
        _name = 'medicament.category'
        _columns = {
                'name': fields.char('Category Name', required=True, size=128),
                'parent_id': fields.many2one('medicament.category', 'Parent Category', select=True),
                'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
                'child_ids': fields.one2many('medicament.category', 'parent_id', 'Children Category'),
        }
        _constraints = [
                (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
        ]
        _order = 'parent_id,id'

medicament_category()

class medicament (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.medicament"
	_columns = {
		'name' : fields.many2one ('product.product','Name',required=True, domain=[('is_medicament', '=', "1")],help="Commercial Name"),
		'category' : fields.many2one('medicament.category', 'Category'),
		'active_component' : fields.char ('Active component', size=128, help="Active Component"),
		'therapeutic_action' : fields.char ('Therapeutic effect', size=128, help="Therapeutic action"),
		'composition' : fields.text ('Composition',help="Components"),
		'indications' : fields.text ('Indication',help="Indications"),
		'dosage' : fields.text ('Dosage Instructions',help="Dosage / Indications"),
		'overdosage' : fields.text ('Overdosage',help="Overdosage"),
		'pregnancy_warning' : fields.boolean ('Pregnancy Warning', help="Check when the drug can not be taken during pregnancy or lactancy"),
		'pregnancy' : fields.text ('Pregnancy and Lactancy',help="Warnings for Pregnant Women"),
		'presentation' : fields.text ('Presentation',help="Packaging"),
		'adverse_reaction' : fields.text ('Adverse Reactions'),
		'storage' : fields.text ('Storage Conditions'),
		'price' : fields.related ('name','lst_price',type='float',string='Price'),
		'qty_available' : fields.related ('name','qty_available',type='float',string='Quantity Available'),
		'notes' : fields.text ('Extra Info'),
		'pregnancy_category' : fields.selection([
						        ('A', 'A'),
						        ('B', 'B'),
						        ('C', 'C'),
						        ('D', 'D'),
						        ('X', 'X'),
						        ('N', 'N'),
						        ], 'Pregnancy Category',
						        help='** FDA Pregancy Categories ***\n'
						        'CATEGORY A :Adequate and well-controlled human studies have failed'
						        ' to demonstrate a risk to the fetus in the first trimester of'
						        ' pregnancy (and there is no evidence of risk in later'
						        ' trimesters).\n\n'
						        'CATEGORY B : Animal reproduction studies have failed todemonstrate a'
						        ' risk to the fetus and there are no adequate and well-controlled'
						        ' studies in pregnant women OR Animal studies have shown an adverse'
						        ' effect, but adequate and well-controlled studies in pregnant women'
						        ' have failed to demonstrate a risk to the fetus in any'
						        ' trimester.\n\n'
						        'CATEGORY C : Animal reproduction studies have shown an adverse'
						        ' effect on the fetus and there are no adequate and well-controlled'
						        ' studies in humans, but potential benefits may warrant use of the'
						        ' drug in pregnant women despite potential risks. \n\n '
						        'CATEGORY D : There is positive evidence of human fetal  risk based'
						        ' on adverse reaction data from investigational or marketing'
						        ' experience or studies in humans, but potential benefits may warrant'
						        ' use of the drug in pregnant women despite potential risks.\n\n'
						        'CATEGORY X : Studies in animals or humans have demonstrated fetal'
						        ' abnormalities and/or there is positive evidence of human fetal risk'
						        ' based on adverse reaction data from investigational or marketing'
						        ' experience, and the risks involved in use of the drug in pregnant'
						        ' women clearly outweigh potential benefits.\n\n'
						        'CATEGORY N : Not yet classified'),
		}

medicament ()

class operational_area (osv.osv):
	_name = "medical.operational_area"
	_columns = {
		'name' :fields.char ('Name', size=128,required=True, help="Operational Area of the city or region"),
		'operational_sector' : fields.one2many('medical.operational_sector','operational_area', 'Operational Sector', readonly=True),
		'info' :fields.text ('Extra Information'),
		}

        _sql_constraints = [
                ('code_uniq', 'unique (name)', 'The Operational Area code name must be unique')]

operational_area ()

class operational_sector (osv.osv):
	_name = "medical.operational_sector"
	_columns = {
		'name' :fields.char ('Name', size=128,required=True, help="Region included in an operational area"),
		'operational_area' :fields.many2one ('medical.operational_area','Operational Area'),
		'info' :fields.text ('Extra Information'),
		}

        _sql_constraints = [
                ('code_uniq', 'unique (name,operational_area)', 'The Operational Sector code and OP Area combination must be unique')]

operational_sector ()

class family_code (osv.osv):
	
	
	_name = "medical.family_code"
	_columns = {
		'name': fields.many2one('res.partner','Name', required=True,help="Family code within an operational sector"),
		'operational_sector' :fields.many2one ('medical.operational_sector','Operational Sector'),
		'members_ids' : fields.many2many ('res.partner', 'family_members_rel','family_id','members_id', 'Members',domain=[('is_person', '=', "1")]),
		
		'info' :fields.text ('Extra Information'),
		}
	_sql_constraints = [('code_uniq', 'unique (name)', 'The Family code name must be unique')]
family_code ()

class speciality (osv.osv):
	_name = "medical.speciality"
	_columns = {
		'name' :fields.char ('Description', size=128, required=True,help="ie, Addiction Psychiatry"),
		'code' : fields.char ('Code', size=128, help="ie, ADP"),
	}
        _sql_constraints = [
                ('code_uniq', 'unique (name)', 'The Medical Specialty code must be unique')]

speciality ()

class physician (osv.osv):
	_name = "medical.physician"
	_description = "Information about the doctor"
	_columns = {
		'name' : fields.many2one ('res.partner','Physician',required=True, domain=[('is_doctor', '=', "1"),('is_person', '=', "1")], help="Physician's Name, from the partner list"),
		'institution' : fields.many2one ('res.partner','Institution',domain=[('is_institution', '=', "1")],help="Institution where she/he works"),
		'code' : fields.char ('ID', size=128, help="MD License ID"),
		'speciality' : fields.many2one ('medical.speciality','Specialty',required=True, help="Specialty Code"),
		'info' : fields.text ('Extra info'),

		'user_id':fields.related('name','user_id',type='many2one',relation='res.users',string='Physician User',store=True),

		}

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

physician ()

class ethnic_group (osv.osv):
	_name ="medical.ethnicity"
	_columns = {
		'name' : fields.char ('Ethnic group',size=128,required=True),
		'code' : fields.char ('Code',size=64),
		}
	_sql_constraints = [
        ('ethnic_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]
ethnic_group ()

class occupation (osv.osv):
	_name = "medical.occupation"
	_description = "Occupation / Job"
	_columns = {
		'name' : fields.char ('Occupation', size=128,required=True),
		'code' : fields.char ('Code', size=64),
		}
	_sql_constraints = [
        ('occupation_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]
occupation ()

class medical_dose (osv.osv):
	_name = "medical.dose.unit"
	_columns = {
		'name' : fields.char ('Unit',size=32,required=True,),
		'desc' : fields.char ('Description',size=64),
		}
	_sql_constraints = [
        ('dose_name_uniq', 'unique(name)', 'The Unit must be unique !'),
    ]
medical_dose ()

class medical_drug_route (osv.osv):
	_name = "medical.drug.route"
	_columns = {
		'name' : fields.char ('Route',size=64, required=True),
		'code' : fields.char ('Code',size=32),
		}
	_sql_constraints = [
        ('route_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]
medical_drug_route ()

class medical_drug_form (osv.osv):
	_name = "medical.drug.form"
	_columns = {
		'name' : fields.char ('Form',size=64, required=True,),
		'code' : fields.char ('Code',size=32),
		}
	_sql_constraints = [
        ('drug_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]
medical_drug_form ()

# PATIENT GENERAL INFORMATION 
	
class patient_data (osv.osv):

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		def _name_get(d):
			name = d.get('name','')
			id = d.get('patient_id',False)
			if id:
				name = '[%s] %s' % (id,name[1])
			return (d['id'], name)
		result = map(_name_get, self.read(cr, user, ids, ['name','patient_id'], context))
		return result

	def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
		if not args:
			args=[]
		if not context:
			context={}
		if name:
			ids = self.search(cr, user, [('patient_id','=',name)]+ args, limit=limit, context=context)
			if not len(ids):
				ids += self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
		else:
			ids = self.search(cr, user, args, limit=limit, context=context)
		result = self.name_get(cr, user, ids, context)
		return result    

# Automatically assign the family code

	def onchange_partnerid (self, cr, uid, ids, partner):
		family_code_id = ""
		if partner:
 			cr.execute ('select family_id from family_members_rel where members_id=%s limit 1',(partner,))
			try:
				family_code_id = str(cr.fetchone()[0])
			except:
				family_code_id = ""
			
		v = {'family_code':family_code_id}
		
		return {'value': v}	
	
# Get the patient age in the following format : "YEARS MONTHS DAYS"
# It will calculate the age of the patient while the patient is alive. When the patient dies, it will show the age at time of death.
		
	def _patient_age(self, cr, uid, ids, name, arg, context={}):
		def compute_age_from_dates (patient_dob,patient_deceased,patient_dod):
			now=datetime.now()
			if (patient_dob):
				dob=datetime.strptime(patient_dob,'%Y-%m-%d')
				if patient_deceased :
					dod=datetime.strptime(patient_dod,'%Y-%m-%d %H:%M:%S')
					delta=relativedelta (dod, dob)
					deceased=" (deceased)"
				else:
					delta=relativedelta (now, dob)
					deceased=''
				years_months_days = str(delta.years) +"y "+ str(delta.months) +"m "+ str(delta.days)+"d" + deceased
			else:
				years_months_days = "No DoB !"
			 
			return years_months_days
		result={}
	        for patient_data in self.browse(cr, uid, ids, context=context):
	            result[patient_data.id] = compute_age_from_dates (patient_data.dob,patient_data.deceased,patient_data.dod)
	        return result

	_name = "medical.patient"
	_description = "Patient related information"
	_columns = {
        'name' : fields.many2one('res.partner','Patient', required="1", domain=[('is_patient', '=', True), ('is_person', '=', True)], help="Patient Name"),
        'patient_id': fields.char('ID', size=64, required=True, select=True, help="Patient Identifier provided by the Health Center. Is not the patient id from the partner form"),	
		'lastname' : fields.related ('name','lastname',type='char',string='Lastname'), 
		'family_code' : fields.many2one ('medical.family_code','Family',help="Family Code"),
		'identifier' : fields.related ('name','ref',type='char',string='SSN', help="Social Security Number or National ID"),
		'current_insurance': fields.many2one ('medical.insurance',"Insurance", domain="[('name','=',name)]",help="Insurance information. You may choose from the different insurances belonging to the patient"),
		'current_address': fields.many2one ('res.partner', "Address", help="Contact information. You may choose from the different contacts and addresses this patient has"),
		'primary_care_doctor': fields.many2one('medical.physician','Primary Care Doctor', help="Current primary care / family doctor"),

		'photo' : fields.binary ('Picture'),
		'dob' : fields.date ('Date of Birth'),
		'age' : fields.function(_patient_age, method=True, type='char', size=32, string='Patient Age',help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
		'sex' : fields.selection([('m','Male'),('f','Female'),], 'Sex', select=True),
		'marital_status' : fields.selection([('s','Single'),('m','Married'),('w','Widowed'),('d','Divorced'),('x','Separated'),], 'Marital Status'),
		'blood_type' : fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O'),], 'Blood Type'),
		'rh' : fields.selection([('+','+'),('-','-'),], 'Rh'),
		'user_id':fields.related('name','user_id',type='many2one',relation='res.users',string='Doctor',help="Physician that logs in the local Medical system (HIS), on the health center. It doesn't necesarily has do be the same as the Primary Care doctor",store=True),
		'ethnic_group' : fields.many2one ('medical.ethnicity','Ethnic group'),
		'vaccinations': fields.one2many ('medical.vaccination','name',"Vaccinations"),
		'medications' : fields.one2many('medical.patient.medication','name','Medications'),
		'prescriptions': fields.one2many ('medical.prescription.order','name',"Prescriptions"),
		'diseases' : fields.one2many ('medical.patient.disease', 'name', 'Diseases'),
		'critical_info' : fields.text ('Important disease, allergy or procedures information',help="Write any important information on the patient's disease, surgeries, allergies, ..."),
		'evaluation_ids' : fields.one2many ('medical.patient.evaluation','name','Evaluation'),
# 		'admissions_ids' : fields.one2many ('medical.patient.admission','name','Admission / Discharge'),
		'general_info' : fields.text ('General Information',help="General information about the patient"),
		'deceased' : fields.boolean ('Deceased',help="Mark if the patient has died"),
		'dod' : fields.datetime ('Date of Death'),
		'cod' : fields.many2one ('medical.pathology', 'Cause of Death'),
		'apt-id' : fields.many2many ('medical.appointment','pat_apt_rel','patient','apid',),
        'childbearing_age' : fields.function(_patient_age, method=True, type='char', size=32, string='Potential for Childbearing'),

	}

	_defaults={
		'patient_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'medical.patient'),
		}

	_sql_constraints = [
                ('name_uniq', 'unique (name)', 'The Patient already exists')]
        	
patient_data ()

def doctor_get(obj, cr, uid, context):
    """
    to get manager name as default value
    """
    ids = obj.pool.get('res.partner').search(cr, uid, [('user_id', '=', uid),('is_doctor', '=', True)])
    print ids,"ids------------------------------------------------"
    if ids:
        boss = obj.pool.get('medical.physician').search(cr, uid, [('name', 'in',ids )] )
        print boss,"boss-------------------------"
        if boss:
            return boss[0]
    return False

class appointment (osv.osv):
	_name = "medical.appointment"
	_columns = {
		'doctor' : fields.many2one ('medical.physician','Physician',  help="Physician's Name"),
		'name' : fields.char ('Appointment ID',size=64, readonly=True,),
		'patient' : fields.many2one ('medical.patient','Patient', help="Patient Name",required=True,),
		'appointment_sdate' : fields.datetime ('Appointment Start',required=True,),
		'appointment_edate' : fields.datetime ('Appointment End',required=True,),
		'institution' : fields.many2one ('res.partner','Health Center', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'speciality' : fields.many2one ('medical.speciality','Speciality',),
		'urgency' : fields.selection([('a','Normal'),('b','Urgent'),('c','Medical Emergency'),], 'Urgency Level'),
		'comments' : fields.text ('Comments'),

		'user_id':fields.related('doctor','user_id',type='many2one',relation='res.users',string='Physician',store=True),

		'patient_status': fields.selection([('ambulatory','Ambulatory'),('outpatient','Outpatient'),('inpatient','Inpatient'),], 'Patient status'),
		'inv_id':fields.many2one ('account.invoice', 'Invoice',readonly =True),
 		'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Cancel')], 'State',readonly="1")
   }
	_sql_constraints = [
       ('date_check', "CHECK (appointment_sdate <= appointment_edate)", "Appointment Start Date must be before Appointment End Date !"),
   ]
	_order = "appointment_sdate desc"

	_defaults = {
		'state':'draft',
		#'name':'0',
        'urgency': lambda *a: 'a',
		'appointment_sdate': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'patient_status': lambda *a: 'ambulatory',
 		'doctor' : doctor_get,
    }
	
	def done(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'done'}, context=context)
		return True 
	 
	def cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'cancel'}, context=context)	
		return True
					 
       
	def confirm(self, cr, uid, ids, context=None):
		appro = self.browse(cr,uid,ids,context=None)
		self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
		for app in appro:
			print "a1a1a1aaa1a1111aa11",app.id
			history_id = self.pool.get('medical.appointment').search(cr,uid,[('id','!=',app.id)])
			print "hhhhhhhhhhh",history_id
			a1=self.browse(cr,uid,history_id,context=None)
			for a in a1:
				if a.doctor==app.doctor:
				 print "----------------------",app.appointment_sdate
				 if a.appointment_sdate<=app.appointment_sdate and app.appointment_edate <=a.appointment_edate:
					raise  osv.except_osv(_('UserError'), _('Appointment Overlapping'))
				
				 if a.appointment_sdate<=app.appointment_sdate and a.appointment_edate>=app.appointment_sdate :
					raise  osv.except_osv(_('UserError'), _('Appointment Overlapping'))
				
				 if a.appointment_sdate<=app.appointment_edate and a.appointment_edate>=app.appointment_edate :
					raise  osv.except_osv(_('UserError'), _('Appointment Overlapping'))
				
				 if a.appointment_sdate>=app.appointment_sdate and a.appointment_edate<=app.appointment_edate :
					raise  osv.except_osv(_('UserError'), _('Appointment Overlapping'))
				
				 if app.appointment_sdate>=app.appointment_edate:
					raise  osv.except_osv(_('UserError'), _('Start of Appointment Date is greater than End of Appointment Date'))
	
		return True
	
	def onchange_doctor(self, cr, uid, ids, doctor,context = None ):
	    v={}
	    if doctor:
	    	reg_pat1 =self.pool.get('medical.physician').browse(cr,uid,doctor)

	    	v['speciality'] = reg_pat1.speciality.id

	    return {'value': v}  
		   
	def onchange_patient(self, cr, uid, ids, patient,patient_status,context = None ):
	    v={}
	    if patient_status == 'inpatient':
	      reg_pat =self.pool.get('medical.inpatient.registration').search(cr, uid, [('patient.id','=',patient)])[0]
	      reg_pat1 =self.pool.get('medical.inpatient.registration').browse(cr,uid,reg_pat)
	      v['inpatient_registration_code'] = reg_pat1.name
	    else:
	    	v['inpatient_registration_code'] = ""
	    return {'value': v}  
		   
	def onchange_patient_status(self, cr, uid, ids, patient_status,context = None ):
		l1=[]
		l2=[]
		
		prid =self.pool.get('medical.patient').search(cr, uid, [])
		if patient_status == 'inpatient':
				reg_pat =self.pool.get('medical.inpatient.registration').search(cr, uid, [('state','=','hospitalized')])
				reg_pat1 =self.pool.get('medical.inpatient.registration').browse(cr,uid,reg_pat)
				
				for r in reg_pat1:
				    l1.append(r.patient.id)
		elif patient_status == 'outpatient':
				reg_pat =self.pool.get('medical.inpatient.registration').search(cr, uid, [('state','!=','hospitalized')])
				reg_pat1 =self.pool.get('medical.inpatient.registration').browse(cr,uid,reg_pat)
				reg =self.pool.get('medical.inpatient.registration').search(cr, uid, [('state','=','hospitalized')])
				
				for r in reg_pat1:
				   l1.append(r.patient.id)
				   
				reg_pat3 =self.pool.get('medical.patient').search(cr, uid, [('id','not in',reg)])
				for rr in reg_pat3:
				   l1.append(rr)
		else:    
			   for r in prid:
			     l1.append(r)
		return {'domain':{'patient':[('id','in',l1)]}} 
     	   
 	def create(self, cr, uid, vals, context=None):
             if vals.get('name','0')=='0':
             	vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment') or '0'
             id =super(appointment, self).create(cr, uid, vals, context=context)
             cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'],id))
             return id
appointment ()

# PATIENT DISESASES INFORMATION

class patient_disease_info (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'pathology'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.patient.disease"
	_description = "Disease info"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID',readonly=True),
		'pathology' : fields.many2one ('medical.pathology','Disease',required=True, help="Disease"),
		'disease_severity' : fields.selection ([('1_mi','Mild'),('2_mo','Moderate'),('3_sv','Severe'),], 'Severity', select=True),	
		'is_on_treatment' : fields.boolean ('Currently on Treatment'),
		'is_infectious' : fields.boolean ('Infectious Disease',help="Check if the patient has an infectious / transmissible disease"),		
		'short_comment' : fields.char ('Remarks', size=128,help="Brief, one-line remark of the disease. Longer description will go on the Extra info field"),
		'doctor' : fields.many2one('medical.physician','Physician', help="Physician who treated or diagnosed the patient"),
		'diagnosed_date': fields.date ('Date of Diagnosis'),
		'healed_date' : fields.date ('Healed'),
		'is_active' : fields.boolean ('Active disease'),
		'age': fields.integer ('Age when diagnosed',help='Patient age at the moment of the diagnosis. Can be estimative'),
		'pregnancy_warning': fields.boolean ('Pregnancy warning'),
		'weeks_of_pregnancy' : fields.integer ('Contracted in pregnancy week #'),
		'is_allergy' : fields.boolean ('Allergic Disease'),
		'allergy_type' : fields.selection ([('da','Drug Allergy'),('fa','Food Allergy'),('ma','Misc Allergy'),('mc','Misc Contraindication'),], 'Allergy type', select=True),
		'pcs_code' : fields.many2one ('medical.procedure','Code', help="Procedure code, for example, ICD-10-PCS Code 7-character string"),
		'treatment_description' : fields.char ('Treatment Description',size=128),
		'date_start_treatment' : fields.date ('Start of treatment'),
		'date_stop_treatment' : fields.date ('End of treatment'),
		'status' : fields.selection ([('c','chronic'),('s','status quo'),('h','healed'),('i','improving'),('w','worsening'),], 'Status of the disease',),
		'extra_info' : fields.text ('Extra Info'),
		}

	_order = 'is_active desc, disease_severity desc, is_infectious desc, is_allergy desc, diagnosed_date desc'

	_sql_constraints = [
       ('validate_disease_period', "CHECK (diagnosed_date < healed_date )", "DIAGNOSED Date must be before HEALED Date !"),
       ('end_treatment_date_before_start', "CHECK (date_start_treatment < date_stop_treatment )", "Treatment start Date must be before Treatment end Date !")
   ]
	
	_defaults = {
		'is_active': lambda *a : True,
                }

patient_disease_info ()

# MEDICATION DOSAGE 
class medication_dosage (osv.osv):
	_name = "medical.medication.dosage"
	_description = "Medicament Common Dosage combinations"
	_columns = {
		'name': fields.char ('Frequency', size=256, help='Common frequency name',required=True,),
		'code': fields.char ('Code', size=64, help='Dosage Code, such as SNOMED, 229798009 = 3 times per day'),
		'abbreviation' : fields.char  ('Abbreviation', size=64, help='Dosage abbreviation, such as tid in the US or tds in the UK'),
		}
	_sql_constraints = [
                ('name_uniq', 'unique (name)', 'The Unit already exists')]

medication_dosage ()

# MEDICATION TEMPLATE
# TEMPLATE USED IN MEDICATION AND PRESCRIPTION ORDERS

class medication_template (osv.osv):

	_name = "medical.medication.template"
	_description = "Template for medication"
	_columns = {
		'medicament' : fields.many2one ('medical.medicament','Medicament',help="Prescribed Medicament",required=True,),
		'indication' : fields.many2one ('medical.pathology','Indication', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic."),
		'dose' : fields.float ('Dose',help="Amount of medication (eg, 250 mg ) each time the patient takes it"),
		'dose_unit' : fields.many2one ('medical.dose.unit','dose unit', help="Unit of measure for the medication to be taken"),
		'route' : fields.many2one ('medical.drug.route','Administration Route',help="HL7 or other standard drug administration route code."),
		'form' : fields.many2one ('medical.drug.form','Form',help="Drug form, such as tablet or gel"),
		'qty' : fields.integer ('x',help="Quantity of units (eg, 2 capsules) of the medicament"),
		'common_dosage' : fields.many2one ('medical.medication.dosage','Frequency',help="Common / standard dosage frequency for this medicament"),
		'frequency' : fields.integer ('Frequency', help="Time in between doses the patient must wait (ie, for 1 pill each 8 hours, put here 8 and select 'hours' in the unit field"),
		'frequency_unit' : fields.selection ([
			('seconds','seconds'),
			('minutes','minutes'),
			('hours','hours'),
			('days','days'),
			('weeks','weeks'),
			('wr','when required'),
			], 'unit', select=True),
		'admin_times' : fields.char  ('Admin hours', size=128, help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18'),
		'duration' : fields.integer ('Treatment duration',help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately"),
		'duration_period' : fields.selection([('minutes','minutes'),('hours','hours'),('days','days'),('months','months'),('years','years'),
											('indefinite','indefinite'),], 'Treatment period',help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately"),
		'start_treatment' : fields.datetime ('Start of treatment'),
		'end_treatment' : fields.datetime ('End of treatment'),
		}
	
	_sql_constraints = [
        ('dates_check', "CHECK (start_treatment < end_treatment)", "Treatment Star Date must be before Treatment End Date !"),
        ]
	
medication_template ()		

# PATIENT MEDICATION TREATMENT
class patient_medication (osv.osv):

	_name = "medical.patient.medication"
	_inherits = {'medical.medication.template': 'template'}
	_description = "Patient Medication"
	_columns = {
		'template' : fields.many2one ('medical.medication.template','Template ID',required=True,select=True,ondelete="cascade"),
		'name' : fields.many2one ('medical.patient','Patient ID',readonly=True),
		'doctor' : fields.many2one('medical.physician','Physician', help="Physician who prescribed the medicament"),
		'is_active' : fields.boolean('Active',help="Check this option if the patient is currently taking the medication"),
		'discontinued' :  fields.boolean('Discontinued'),
		'course_completed' : fields.boolean('Course Completed'),
		'discontinued_reason' : fields.char ('Reason for discontinuation', size=128, help="Short description for discontinuing the treatment"),
		'adverse_reaction' : fields.text ('Adverse Reactions',help="Specific side effects or adverse reactions that the patient experienced"),
		'notes' : fields.text ('Extra Info'),
		'patient_id' : fields.many2one('medical.patient','Patient'),		
		}
	_defaults = {
		'is_active': lambda *a : True,
		'start_treatment': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'frequency_unit': lambda *a: 'hours',
        'duration_period': lambda *a: 'days',
        'qty': lambda *a: 1,                                                              
                }
	
	def onchange_course_completed(self, cr, uid, ids, course_completed, discontinued,is_active,context = None ):
		c={}
		if course_completed == True:
			print "in onchange_course_completed========================="
			c = {'is_active':False, 'discontinued':False}
		elif is_active == False and discontinued == False and course_completed == False:
			c = {'is_active':True,}
						  			
		return {'value': c}	
	
	def onchange_discontinued(self, cr, uid, ids, discontinued,is_active,course_completed ):
		a={}
		if discontinued == True:
			print "in onchange_discontinued =====================>"
			a = {'is_active':False, 'course_completed':False}
		elif is_active == False and discontinued == False and course_completed == False:
			a = {'is_active':True,}
		return {'value': a}	
	
	def onchange_is_active(self, cr, uid, ids, is_active, course_completed, discontinued,context = None ):
		b={}
		if is_active == True:
			print "in onchange_discontinued =====================>"
			b = {'discontinued':False, 'course_completed':False}
		elif is_active == False and discontinued == False and course_completed == False:
			b = {'course_completed':True,}
		return {'value': b}
			   								
patient_medication ()

# PATIENT EVALUATION

class patient_evaluation (osv.osv):

# Kludge to get patient ID when using one2many fields.
# 	def onchange_evaluation_date (self, cr, uid, ids,name):
# 		if not name:
# 			return {'value': {'name': patient}}

	_name = "medical.patient.evaluation"
	_description = "evaluation"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID'),
        'evaluation_date' : fields.many2one ('medical.appointment','Appointment Date',help="Enter or select the date / ID of the appointment related to this evaluation"),
		'evaluation_start' : fields.datetime ('Start of Evaluation',required=True),
		'evaluation_endtime' : fields.datetime ('End of Evaluation',required=True),
		'next_evaluation' : fields.many2one ('medical.appointment','Next Appointment'),
		'user_id' : fields.many2one ('res.users','Last Changed by', readonly=True),
		'doctor' : fields.many2one('medical.physician','Doctor', readonly=True), 
		'speciality' : fields.many2one ('medical.speciality','Specialty', ),
		'information_source' : fields.char ('Source', size=128,help='Source of Information, eg : Self, relative, friend ...'),
		'reliable_info' : fields.boolean ('Reliable', help="Uncheck this option if the information provided by the source seems not reliable"),
		'derived_from' : fields.many2one('medical.physician','Derived from Doctor',readonly=True, help="Physician who escalated / derived the case"), 
		'derived_to' : fields.many2one('medical.physician','Derived to Doctor', help="Physician to whom escalate / derive the case"), 
		'evaluation_type' : fields.selection([('a','Ambulatory'),('e','Emergency'),('i','Inpatient'),('pa','Pre-arraganged appointment'),
                                			('pc','Periodic control'),('p','Phone call'),('t','Telemedicine'),], 'Evaluation Type'),
		'chief_complaint' : fields.char ('Chief Complaint', size=128,help='Chief Complaint'),
		'present_illness' : fields.text ('Present Illness'),
		'evaluation_summary' : fields.text ('Evaluation Summary'),
		'urgency' : fields.selection([
        (None, ''),
        ('a', 'Normal'),
        ('b', 'Urgent'),
        ('c', 'Medical Emergency'),
        ], 'Urgency', sort=False),
		'visit_type' : fields.selection([
        (None, ''),
        ('new', 'New health condition'),
        ('followup', 'Followup'),
        ('chronic', 'Chronic condition checkup'),
        ('well_child', 'Well Child visit'),
        ('well_woman', 'Well Woman visit'),
        ('well_man', 'Well Man visit'),
        ], 'Visit', sort=False),
		
		'hip' : fields.float('Hip', help="Hip circumference in centimeters, eg 100'"),
		'whr' : fields.float('WHR', help="Waist to hip ratio"),
		
		
		'glycemia' : fields.float('Glycemia', help="Last blood glucose level. Can be approximative."),
		'hba1c' : fields.float('Glycated Hemoglobin', help="Last Glycated Hb level. Can be approximative."),
		'cholesterol_total' : fields.integer ('Last Cholesterol',help="Last cholesterol reading. Can be approximative"),
		'hdl' : fields.integer ('Last HDL',help="Last HDL Cholesterol reading. Can be approximative"),
		'ldl' : fields.integer ('Last LDL',help="Last LDL Cholesterol reading. Can be approximative"),
		'tag' : fields.integer ('Last TAGs',help="Triacylglycerols (triglicerides) level. Can be approximative"),
		'systolic' : fields.integer('Systolic Pressure'),
		'diastolic' : fields.integer('Diastolic Pressure'),
		'bpm' : fields.integer ('Heart Rate',help="Heart rate expressed in beats per minute"),
		'respiratory_rate' : fields.integer ('Respiratory Rate',help="Respiratory rate expressed in breaths per minute"),
		'osat' : fields.integer ('Oxygen Saturation',help="Oxygen Saturation (arterial)."),
		'malnutrition' : fields.boolean ('Malnutrition', help="Check this box if the patient show signs of malnutrition. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Moderate protein-energy malnutrition, E44.0 in ICD-10 encoding"),
		'dehydration' : fields.boolean ('Dehydration', help="Check this box if the patient show signs of dehydration. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Volume Depletion, E86 in ICD-10 encoding"),
		'temperature' : fields.float('Temperature (celsius)'),
		'weight' : fields.float('Weight (kg)'),
		'height' : fields.float('Height (cm)'),
		'bmi' : fields.float('Body Mass Index'),
		'head_circumference' : fields.float('Head Circumference',help="Head circumference"),		
		'abdominal_circ' : fields.float('Abdominal Circumference'),
# 		'edema' : fields.boolean ('Edema', help="Please also encode the correspondent disease on the patient disease history. For example,  R60.1 in ICD-10 encoding"),
# 		'petechiae' : fields.boolean ('Petechiae'),
# 		'hematoma' : fields.boolean ('Hematomas'),
# 		'cyanosis' : fields.boolean ('Cyanosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  R23.0 in ICD-10 encoding"),
# 		'acropachy' : fields.boolean ('Acropachy', help="Check if the patient shows acropachy / clubbing"),		
# 		'nystagmus' : fields.boolean ('Nystagmus', help="If not associated to a disease, please encode it on the patient disease history. For example,  H55 in ICD-10 encoding"),
# 		'miosis' : fields.boolean ('Miosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding" ),
# 		'mydriasis' : fields.boolean ('Mydriasis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding"),
# 		'cough' : fields.boolean ('Cough', help="If not associated to a disease, please encode it on the patient disease history."),
# 		'palpebral_ptosis' : fields.boolean ('Palpebral Ptosis', help="If not associated to a disease, please encode it on the patient disease history"),
# 		'arritmia' : fields.boolean ('Arritmias', help="If not associated to a disease, please encode it on the patient disease history"),		
# 		'heart_murmurs' : fields.boolean ('Heart Murmurs'),
# 		'heart_extra_sounds' : fields.boolean ('Heart Extra Sounds', help="If not associated to a disease, please encode it on the patient disease history"),		
# 		'jugular_engorgement' : fields.boolean ('Tremor', help="If not associated to a disease, please encode it on the patient disease history"),
# 		'ascites' : fields.boolean ('Ascites', help="If not associated to a disease, please encode it on the patient disease history"),	
# 		'lung_adventitious_sounds' : fields.boolean ('Lung Adventitious sounds', help="Crackles, wheezes, ronchus.."),
# 		'bronchophony' : fields.boolean ('Bronchophony'),
# 		'increased_fremitus' : fields.boolean ('Increased Fremitus'),
# 		'decreased_fremitus' : fields.boolean ('Decreased Fremitus'),							
# 		'jaundice' : fields.boolean ('Jaundice', help="If not associated to a disease, please encode it on the patient disease history"),		
# 		'lynphadenitis' : fields.boolean ('Linphadenitis', help="If not associated to a disease, please encode it on the patient disease history"),
# 		'breast_lump' : fields.boolean ('Breast Lumps'),
# 		'breast_asymmetry' : fields.boolean ('Breast Asymmetry'),
# 		'nipple_inversion' : fields.boolean ('Nipple Inversion'),
# 		'nipple_discharge' : fields.boolean ('Nipple Discharge'),
# 		'peau_dorange' : fields.boolean ('Peau d orange',help="Check if the patient has prominent pores in the skin of the breast" ),				
# 		'gynecomastia' : fields.boolean ('Gynecomastia'),
# 		'masses' : fields.boolean ('Masses', help="Check when there are findings of masses / tumors / lumps"),
# 		'hypotonia' : fields.boolean ('Hypotonia', help="Please also encode the correspondent disease on the patient disease history."),
# 		'hypertonia' : fields.boolean ('Hypertonia', help="Please also encode the correspondent disease on the patient disease history."),
# 		'pressure_ulcers' : fields.boolean ('Pressure Ulcers', help="Check when Decubitus / Pressure ulcers are present"),		
# 		'goiter' : fields.boolean ('Goiter'),		
# 		'alopecia' : fields.boolean ('Alopecia', help="Check when alopecia - including androgenic - is present"),		
# 		'xerosis' : fields.boolean ('Xerosis'),				
# 		'erithema' : fields.boolean ('Erithema', help="Please also encode the correspondent disease on the patient disease history."),
		'loc_eyes' : fields.selection([('1', 'Does not Open Eyes'),
								        ('2', 'Opens eyes in response to painful stimuli'),
								        ('3', 'Opens eyes in response to voice'),
								        ('4', 'Opens eyes spontaneously'),
								        ], 'Glasgow - Eyes', sort=False),
		'loc_verbal' : fields.selection([('1', 'Makes no sounds'),
								        ('2', 'Incomprehensible sounds'),
								        ('3', 'Utters inappropriate words'),
								        ('4', 'Confused, disoriented'),
								        ('5', 'Oriented, converses normally'),
								        ], 'Glasgow - Verbal', sort=False),
		'loc_motor' : fields.selection([('1', 'Makes no movement'),
								        ('2', 'Extension to painful stimuli - decerebrate response -'),
								        ('3', 'Abnormal flexion to painful stimuli (decorticate response)'),
								        ('4', 'Flexion / Withdrawal to painful stimuli'),
								        ('5', 'Localizes painful stimuli'),
								        ('6', 'Obeys commands'),
								        ], 'Glasgow - Motor', sort=False),
		'loc' : fields.integer('Level of Consciousness', help="Level of Consciousness - on Glasgow Coma Scale :  1=coma - 15=normal"),
# 		'loc_eyes' : fields.integer('Level of Consciousness - Eyes', help="Eyes Response - Glasgow Coma Scale - 1 to 4"),
# 		'loc_verbal' : fields.integer('Level of Consciousness - Verbal', help="Verbal Response - Glasgow Coma Scale - 1 to 5"),
# 		'loc_motor' : fields.integer('Level of Consciousness - Motor', help="Motor Response - Glasgow Coma Scale - 1 to 6"),		
		'violent' : fields.boolean ('Violent Behaviour', help="Check this box if the patient is agressive or violent at the moment"),
		'mood' : fields.selection([('n','Normal'),('s','Sad'),('f','Fear'),('r','Rage'),('h','Happy'),('d','Disgust'),('e','Euphoria'),('fl','Flat'),], 'Mood'),
		'orientation' : fields.boolean ('Orientation', help="Check this box if the patient is disoriented in time and/or space"),
		'memory' : fields.boolean ('Memory', help="Check this box if the patient has problems in short or long term memory"),
		'knowledge_current_events' : fields.boolean ('Knowledge of Current Events', help="Check this box if the patient can not respond to public notorious events"),
		'judgment' : fields.boolean ('Jugdment', help="Check this box if the patient can not interpret basic scenario solutions"),
		'abstraction' : fields.boolean ('Abstraction', help="Check this box if the patient presents abnormalities in abstract reasoning"),
		'vocabulary' : fields.boolean ('Vocabulary', help="Check this box if the patient lacks basic intelectual capacity, when she/he can not describe elementary objects"),
		'calculation_ability' : fields.boolean ('Calculation Ability',help="Check this box if the patient can not do simple arithmetic problems"),
		'object_recognition' : fields.boolean ('Object Recognition', help="Check this box if the patient suffers from any sort of gnosia disorders, such as agnosia, prosopagnosia ..."),
		'praxis' : fields.boolean ('Praxis', help="Check this box if the patient is unable to make voluntary movements"),
		'diagnosis' : fields.many2one ('medical.pathology','Presumptive Diagnosis', help="Presumptive Diagnosis"),
		'info_diagnosis' : fields.text('Presumptive Diagnosis: Extra Info'),
		'directions' : fields.text('Plan'),
		'actions' : fields.one2many('medical.directions', 'name', 'Actions'),
		'secondary_conditions' : fields.one2many('medical.secondary_condition', 'name', 'Secondary Conditions',help='Other, Secondary conditions found on the patient'),
		'diagnostic_hypothesis' : fields.one2many('medical.diagnostic_hypothesis', 'name', 'Hypotheses / DDx',help='Other Diagnostic Hypotheses / Differential Diagnosis (DDx)'),
		'signs_and_symptoms' : fields.one2many('medical.signs_and_symptoms', 'name', 'Signs and Symptoms',help='Enter the Signs and Symptoms for the patient in this evaluation.'),
# 		'symptom_pain' : fields.boolean ('Pain'),
# 		'symptom_pain_intensity' : fields.integer ('Pain intensity', help="Pain intensity from 0 (no pain) to 10 (worst possible pain)"),
# 		'symptom_arthralgia' : fields.boolean ('Arthralgia'),
# 		'symptom_myalgia' : fields.boolean ('Myalgia'),
# 		'symptom_abdominal_pain' : fields.boolean ('Abdominal Pain'),
# 		'symptom_cervical_pain' : fields.boolean ('Cervical Pain'),
# 		'symptom_thoracic_pain' : fields.boolean ('Thoracic Pain'),
# 		'symptom_lumbar_pain' : fields.boolean ('Lumbar Pain'),		
# 		'symptom_pelvic_pain' : fields.boolean ('Pelvic Pain'),
# 		'symptom_headache' : fields.boolean ('Headache'),
# 		'symptom_odynophagia' : fields.boolean ('Odynophagia'),
# 		'symptom_sore_throat' : fields.boolean ('Sore throat'),
# 		'symptom_otalgia' : fields.boolean ('Otalgia'),
# 		'symptom_tinnitus' : fields.boolean ('Tinnitus'),
# 		'symptom_ear_discharge' : fields.boolean ('Ear Discharge'),		
# 		'symptom_hoarseness' : fields.boolean ('Hoarseness'),		
# 		'symptom_chest_pain' : fields.boolean ('Chest Pain'),
# 		'symptom_chest_pain_excercise' : fields.boolean ('Chest Pain on excercise only'),
# 		'symptom_orthostatic_hypotension' : fields.boolean ('Orthostatic hypotension', help="If not associated to a disease,please encode it on the patient disease history. For example,  I95.1 in ICD-10 encoding"),		
# 		'symptom_astenia' : fields.boolean ('Astenia'),
# 		'symptom_anorexia' : fields.boolean ('Anorexia'),
# 		'symptom_weight_change' : fields.boolean ('Sudden weight change'),
# 		'symptom_abdominal_distension' : fields.boolean ('Abdominal Distension'),
# 		'symptom_hemoptysis' : fields.boolean ('Hemoptysis'),
# 		'symptom_hematemesis' : fields.boolean ('Hematemesis'),
# 		'symptom_epistaxis' : fields.boolean ('Epistaxis'),
# 		'symptom_gingival_bleeding' : fields.boolean ('Gingival Bleeding'),		
# 		'symptom_rinorrhea' : fields.boolean ('Rinorrhea'),						
# 		'symptom_nausea' : fields.boolean ('Nausea'),
# 		'symptom_vomiting' : fields.boolean ('Vomiting'),				
# 		'symptom_dysphagia' : fields.boolean ('Dysphagia'),		
# 		'symptom_polydipsia' : fields.boolean ('Polydipsia'),
# 		'symptom_polyphagia' : fields.boolean ('Polyphagia'),
# 		'symptom_polyuria' : fields.boolean ('Polyuria'),
# 		'symptom_nocturia' : fields.boolean ('Nocturia'),
# 		'symptom_vesical_tenesmus' : fields.boolean ('Vesical Tenesmus'),
# 		'symptom_pollakiuria' : fields.boolean ('Pollakiuiria'),
# 		'symptom_dysuria' : fields.boolean ('Dysuria'),		
# 		'symptom_stress' : fields.boolean ('Stressed-out'),
# 		'symptom_mood_swings' : fields.boolean ('Mood Swings'),		
# 		'symptom_pruritus' : fields.boolean ('Pruritus'),
# 		'symptom_insomnia' : fields.boolean ('Insomnia'),
# 		'symptom_disturb_sleep' : fields.boolean ('Disturbed Sleep'),		
# 		'symptom_dyspnea' : fields.boolean ('Dyspnea'),
# 		'symptom_orthopnea' : fields.boolean ('Orthopnea'),		
# 		'symptom_amnesia' : fields.boolean ('Amnesia'),
# 		'symptom_paresthesia' : fields.boolean ('Paresthesia'),		
# 		'symptom_paralysis' : fields.boolean ('Paralysis'),
# 		'symptom_syncope' : fields.boolean ('Syncope'),
# 		'symptom_dizziness' : fields.boolean ('Dizziness'),
# 		'symptom_vertigo' : fields.boolean ('Vertigo'),				
# 		'symptom_eye_glasses' : fields.boolean ('Eye glasses',help="Eye glasses or contact lenses"),
# 		'symptom_blurry_vision' : fields.boolean ('Blurry vision'),
# 		'symptom_diplopia' : fields.boolean ('Diplopia'),
# 		'symptom_photophobia' : fields.boolean ('Photophobia'),
# 		'symptom_dysmenorrhea' : fields.boolean ('Dysmenorrhea'),
# 		'symptom_amenorrhea' : fields.boolean ('Amenorrhea'),
# 		'symptom_metrorrhagia' : fields.boolean ('Metrorrhagia'),
# 		'symptom_menorrhagia' : fields.boolean ('Menorrhagia'),
# 		'symptom_vaginal_discharge' : fields.boolean ('Vaginal Discharge'),		
# 		'symptom_urethral_discharge' : fields.boolean ('Urethral Discharge'),		
# 		'symptom_diarrhea' : fields.boolean ('Diarrhea'),
# 		'symptom_constipation' : fields.boolean ('Constipation'),
# 		'symptom_rectal_tenesmus' : fields.boolean ('Rectal Tenesmus'),
# 		'symptom_melena' : fields.boolean ('Melena'),
# 		'symptom_proctorrhagia' : fields.boolean ('Proctorrhagia'),		
# 		'symptom_xerostomia' : fields.boolean ('Xerostomia'),
# 		'symptom_sexual_dysfunction' : fields.boolean ('Sexual Dysfunction'),
# 		'notes' : fields.text ('Notes'),
	}

	_defaults = {
        'loc_eyes': lambda *a: '4',
        'loc_verbal': lambda *a: '5',
        'loc_motor': lambda *a: '6',
		'evaluation_type': lambda *a: 'pa',
		'information_source': lambda *a: 'Self',
		'user_id': lambda obj, cr, uid, context: uid,
		'name': lambda self, cr, uid, c: c.get('name', False),
		'doctor' : doctor_get,
		'reliable_info': lambda *a: True,
		'evaluation_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        }

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'evaluation_start'
		res = [(r['id'], r[rec_name]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res
	
	def onchange_height_weight (self, cr, uid, ids, height, weight):
		if height:
			v = {'bmi':weight/((height/100)**2)}
		else:
			v = {'bmi':0}

		return {'value': v}	
	
	def on_change_with_whr(self, cr, uid, ids, abdominal_circ, hip):
			v = {}
			waist = abdominal_circ
			hip = hip
			if (hip > 0):
				whr = waist / hip
				v = {'whr':whr}
			else:
				v = {'whr':0}
			return {'value': v}
	        
        	
				
	def onchange_loc (self, cr, uid, ids, loc_motor, loc_eyes, loc_verbal):
		if not loc_motor:
			loc_motor = 0
		if not loc_eyes:
			loc_eyes = 0
		if not loc_verbal:
			loc_verbal = 0
		v = {'loc':int(loc_motor) + int(loc_eyes) + int(loc_verbal)}
		return {'value': v}	

patient_evaluation ()

# PATIENT DIRECTIONS (to be used also in surgeries if using standards like ICD10-PCS)

class directions (osv.osv):
	_name = "medical.directions"
	_columns = {
		'name' : fields.many2one ('medical.patient.evaluation','Evaluation', readonly=True),
		'procedure' : fields.many2one ('medical.procedure', 'Procedure',required=True),
		'comments' : fields.char ('Comments', size=128),
		}

directions ()

# PATIENT DIRECTIONS (to be used also in surgeries if using standards like ICD10-PCS)

class medical_secondary_condition (osv.osv):
	_name = "medical.secondary_condition"
	_columns = {
		'name' : fields.many2one ('medical.patient.evaluation','Evaluation', readonly=True),
		'procedure' : fields.many2one ('medical.pathology', 'Pathology',required=True),
		'comments' : fields.char ('Comments', size=128),
		}

medical_secondary_condition ()

class medical_diagnostic_hypothesis (osv.osv):
	_name = "medical.diagnostic_hypothesis"
	_columns = {
		'name' : fields.many2one ('medical.patient.evaluation','Evaluation', readonly=True),
		'procedure' : fields.many2one ('medical.pathology', 'Pathology',required=True),
		'comments' : fields.char ('Comments', size=128),
		}

medical_diagnostic_hypothesis ()

class medical_signs_and_symptoms (osv.osv):
	_name = "medical.signs_and_symptoms"
	_columns = {
		'name' : fields.many2one ('medical.patient.evaluation','Evaluation', readonly=True),
		'sign_or_symptom' : fields.selection ((('sign', 'Sign'),('symptom', 'Symptom')),'Subjective / Objective', required=True),
		'clinical' : fields.many2one ('medical.pathology', 'Sign or Symptom',required=True),
		'comments' : fields.char ('Comments', size=128),
		}

medical_signs_and_symptoms ()

# PRESCRIPTION ORDER

class patient_prescription_order (osv.osv):

	_name = "medical.prescription.order"
	_description = "prescription order"

		
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID',required=True,),
		'prescription_id' : fields.char ('Prescription ID', size=128, help='Type in the ID of this prescription'),
		'prescription_date' : fields.datetime ('Prescription Date'),
		'user_id' : fields.many2one ('res.users','Log In User', readonly=True),
		'pharmacy' : fields.many2one ('res.partner', 'Pharmacy',domain=[('is_pharmacy', '=', True)]),
		'prescription_line' : fields.one2many ('medical.prescription.line', 'name', 'Prescription line'),
# 		'physician_id' : fields.many2one ('res.partner','Physician',  help="Physician's Name, from the partner list"),
		'notes' : fields.text ('Prescription Notes'),
		'pid1' : fields.many2one ('medical.appointment', 'Appointment', ),
		'doctor' : fields.many2one ('medical.physician','Prescribing Doctor',  help="Physician's Name"),
		}

	_defaults = {
        'prescription_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'user_id': lambda obj, cr, uid, context: uid,
		'doctor' : doctor_get,		
	#	'prescription_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'medical.prescription'),
                }
	_sql_constraints = [
                ('pid1', 'unique (pid1)', 'Prescription must be unique per Appointment')]
	
 	
	 
	
 	def create(self, cr, uid, vals, context=None):
             vals['prescription_id'] = self.pool.get('ir.sequence').get(cr, uid, 'medical.prescription') or '0'
             id =super(patient_prescription_order, self).create(cr, uid, vals, context=context)
             return id
           
	def onchange_name(self, cr, uid, ids, name,context = None ):
		l1=[]
		prid =self.pool.get('medical.prescription.order').search(cr, uid, [])
		prid1 =self.pool.get('medical.prescription.order').browse(cr,uid,prid)
		for p in prid1:
			l1.append(p.pid1.id)
		return {'domain':{'pid1':[('id','not in',l1)]}} 	
		
patient_prescription_order ()

		
# PRESCRIPTION LINE
class prescription_line (osv.osv):

	_name = "medical.prescription.line"
	_description = "Basic prescription object"
	_inherits = {'medical.medication.template': 'template'}
	_columns = {
		'template' : fields.many2one ('medical.medication.template','Template ID',required=True,select=True,ondelete="cascade"),
		'name' : fields.many2one ('medical.prescription.order','Prescription ID'),	
		'review' : fields.datetime ('Review'),
		'quantity' : fields.integer ('Quantity'),
		'refills' : fields.integer ('Refills #'),
		'allow_substitution' : fields.boolean('Allow substitution'),  
		'short_comment' : fields.char ('Comment', size=128, help='Short comment on the specific drug'),
		'prnt' : fields.boolean ('Print', help='Check this box to print this line of the prescription.'),
		}
	_defaults = {
        'qty': lambda *a: 1,
        'duration_period': lambda *a: 'days',
        'frequency_unit': lambda *a: 'hours',
        'quantity' : lambda *a: 1,
        'prnt': lambda *a: True,                               
        }
		
prescription_line ()



# PATIENT VACCINATION INFORMATION

class vaccination (osv.osv):
	def _check_vaccine_expiration_date(self,cr,uid,ids):
		vaccine=self.browse(cr,uid,ids[0])
		if vaccine:
			if vaccine.vaccine_expiration_date < vaccine.date:
				return False
		return True

	def onchange_vaccination_expiration_date(self, cr, uid, ids, vaccine_date, vaccination_expiration_date):
		if vaccination_expiration_date and vaccine_date:
			if vaccination_expiration_date < vaccine_date:
				v = {'vaccine_expiration_date':''}
				exp_message = "EXPIRED VACCINE !! "+ vaccination_expiration_date + "\nPlease Dispose it !!"
				return {'value': v,'warning':{'title':'warning','message': exp_message}}	
			else:
				return {}
		else:
			return {}
	
	_name = "medical.vaccination"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID', readonly=True),
		'vaccine' : fields.many2one ('product.product','Name', domain=[('is_vaccine', '=', "1")], help="Vaccine Name. Make sure that the vaccine (product) has all the proper information at product level. Information such as provider, supplier code, tracking number, etc.. This information must always be present. If available, please copy / scan the vaccine leaflet and attach it to this record"),
		'vaccine_expiration_date' : fields.date ('Expiration date'),
		'vaccine_lot' : fields.char ('Lot Number',size=128,help="Please check on the vaccine (product) production lot number and tracking number when available !"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center where the patient is being or was vaccinated"),
		'date' : fields.datetime ('Date'),
		'next_dose_date' : fields.datetime ('Next Dose'),
		'dose' : fields.integer ('Dose Number'),
		'observations' : fields.char ('Observations', size=128),
		}
	_defaults = {
        'dose': lambda *a: 1,
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		}

	_constraints = [
        (_check_vaccine_expiration_date, 'WARNING !! EXPIRED VACCINE. PLEASE INFORM THE LOCAL HEALTH AUTHORITIES AND DO NOT USE IT !!', ['vaccine_expiration_date'])
	] 
        _sql_constraints = [
                ('dose_unique', 'unique (name,dose,vaccine)', 'This vaccine dose has been given already to the patient '),
                ('next_dose_date_check', "CHECK (date < next_dose_date)", "The Vaccine first dose date must be before Vaccine next dose Date !"),
                ]


vaccination ()


# HEALTH CENTER / HOSPITAL INFRASTRUCTURE


class hospital_building (osv.osv):
	_name = "medical.hospital.building"
	_columns = {
		'name' : fields.char ('Name', size=128, required=True,help="Name of the building within the institution"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'code' : fields.char ('Code', size=64),
		'extra_info' : fields.text ('Extra Info'),
		}
hospital_building ()

class hospital_unit (osv.osv):
	_name = "medical.hospital.unit"
	_columns = {
		'name' : fields.char ('Name', size=128,required=True, help="Name of the unit, eg Neonatal, Intensive Care, ..."),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'code' : fields.char ('Code', size=64),
		'extra_info' : fields.text ('Extra Info'),
		}
hospital_unit ()

class hospital_ward (osv.osv):
	_name = "medical.hospital.ward"
	_columns = {
		'name' : fields.char ('Name',required=True, size=128, help="Ward / Room code"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'building' : fields.many2one ('medical.hospital.building','Building'),
		'floor' : fields.integer ('Floor Number'),
		'unit' : fields.many2one ('medical.hospital.unit','Unit'),
		'private' : fields.boolean ('Private',help="Check this option for private room"),
		'bio_hazard' : fields.boolean ('Bio Hazard',help="Check this option if there is biological hazard"),
		'number_of_beds' : fields.integer ('Number of beds',help="Number of patients per ward"),
		'telephone' : fields.boolean ('Telephone access'),
		'ac' : fields.boolean ('Air Conditioning'),
		'private_bathroom' : fields.boolean ('Private Bathroom'),
		'guest_sofa' : fields.boolean ('Guest sofa-bed'),
		'tv' : fields.boolean ('Television'),
		'internet' : fields.boolean ('Internet Access'),
		'refrigerator' : fields.boolean ('Refrigetator'),
		'microwave' : fields.boolean ('Microwave'),
		'gender' : fields.selection ((('men','Men Ward'),('women','Women Ward'),('unisex','Unisex')),'Gender', required=True),
		'state': fields.selection((('beds_available','Beds available'),('full','Full'),('na','Not available')),'Status'),
		'extra_info' : fields.text ('Extra Info'),
		}

	_defaults = {
		'gender': lambda *a: 'unisex',
         'number_of_beds': lambda *a: 1,
		}

hospital_ward ()

class hospital_bed (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.hospital.bed"
	_columns = {
		'name' : fields.many2one ('product.product','Bed', domain=[('is_bed', '=', "1")], help="Bed Number"),
		'ward' : fields.many2one ('medical.hospital.ward','Ward',help="Ward or room"),
		'bed_type' : fields.selection((('gatch','Gatch Bed'),('electric','Electric'),('stretcher','Stretcher'),('low','Low Bed'),('low_air_loss','Low Air Loss'),('circo_electric','Circo Electric'),('clinitron','Clinitron')),'Bed Type', required=True),
		'telephone_number' : fields.char ('Telephone Number',size=128, help="Telephone number / Extension"),
		'extra_info' : fields.text ('Extra Info'),
		'state': fields.selection((('free','Free'),('reserved','Reserved'),('occupied','Occupied'),('na','Not available')),'Status',readonly=True),
		}

	_defaults = {
        'bed_type': lambda *a: 'gatch',
        'state': lambda *a: 'free',
		}

hospital_bed ()

class hospital_oprating_room(osv.osv):
	_name = "medical.hospital.oprating.room"
	_columns = {
	    'name' : fields.char('Name',size=128, required=True, help='Name of the Operating Room'),
	    'institution' : fields.many2one('res.partner', 'Institution',domain=[('is_institution', '=', True)], help='Medical Center'),
	    'building' : fields.many2one('medical.hospital.building', 'Building',select=True),
	    'unit' : fields.many2one('medical.hospital.unit', 'Unit'),
	    'extra_info' : fields.text('Extra Info'),
	    }
	_sql_constraints = [
                ('name_uniq', 'unique (name, institution)', 'The Operating Room code must be unique per Health Center.')]

hospital_oprating_room()
