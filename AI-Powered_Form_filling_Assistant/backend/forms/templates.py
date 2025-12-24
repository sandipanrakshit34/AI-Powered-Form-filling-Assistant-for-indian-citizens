# backend/forms/templates.py
# Form Templates Database
# Place this file at: backend/forms/templates.py

FORM_TEMPLATES = {
    'birth_certificate': {
        'formId': 'birth_certificate',
        'formName': 'Birth Certificate Application',
        'department': 'Vital Statistics Office',
        'description': 'Application for birth certificate',
        'fields': [
            {'fieldId': 'applicant_name', 'fieldLabel': 'Applicant Full Name', 'fieldType': 'text', 'required': True, 'dataSource': 'name'},
            {'fieldId': 'date_of_birth', 'fieldLabel': 'Date of Birth (DD/MM/YYYY)', 'fieldType': 'date', 'required': True, 'dataSource': 'dob'},
            {'fieldId': 'gender', 'fieldLabel': 'Gender', 'fieldType': 'select', 'required': True, 'dataSource': 'gender', 'options': ['Male', 'Female', 'Other']},
            {'fieldId': 'father_name', 'fieldLabel': "Father's Name", 'fieldType': 'text', 'required': True, 'dataSource': 'father_name'},
            {'fieldId': 'address', 'fieldLabel': 'Address', 'fieldType': 'textarea', 'required': True, 'dataSource': 'address'}
        ]
    },
    'pan_application': {
        'formId': 'pan_application',
        'formName': 'PAN Application Form',
        'department': 'Income Tax Department',
        'description': 'Application for Permanent Account Number',
        'fields': [
            {'fieldId': 'applicant_name', 'fieldLabel': 'Full Name', 'fieldType': 'text', 'required': True, 'dataSource': 'name'},
            {'fieldId': 'date_of_birth', 'fieldLabel': 'Date of Birth (DD/MM/YYYY)', 'fieldType': 'date', 'required': True, 'dataSource': 'dob'},
            {'fieldId': 'gender', 'fieldLabel': 'Gender', 'fieldType': 'select', 'required': True, 'dataSource': 'gender', 'options': ['Male', 'Female', 'Other']},
            {'fieldId': 'pan_number', 'fieldLabel': 'PAN Number', 'fieldType': 'text', 'required': False, 'dataSource': 'pan'},
            {'fieldId': 'address', 'fieldLabel': 'Address', 'fieldType': 'textarea', 'required': True, 'dataSource': 'address'}
        ]
    },
    'aadhaar_update': {
        'formId': 'aadhaar_update',
        'formName': 'Aadhaar Update Form',
        'department': 'UIDAI',
        'description': 'Form for updating Aadhaar details',
        'fields': [
            {'fieldId': 'aadhaar_number', 'fieldLabel': 'Aadhaar Number', 'fieldType': 'text', 'required': True, 'dataSource': 'aadhar'},
            {'fieldId': 'full_name', 'fieldLabel': 'Full Name', 'fieldType': 'text', 'required': True, 'dataSource': 'name'},
            {'fieldId': 'date_of_birth', 'fieldLabel': 'Date of Birth', 'fieldType': 'date', 'required': True, 'dataSource': 'dob'},
            {'fieldId': 'gender', 'fieldLabel': 'Gender', 'fieldType': 'select', 'required': True, 'dataSource': 'gender', 'options': ['Male', 'Female']},
            {'fieldId': 'address', 'fieldLabel': 'Address', 'fieldType': 'textarea', 'required': True, 'dataSource': 'address'}
        ]
    },
    'income_certificate': {
        'formId': 'income_certificate',
        'formName': 'Income Certificate Application',
        'department': 'Revenue Department',
        'description': 'Application for Income Certificate',
        'fields': [
            {'fieldId': 'applicant_name', 'fieldLabel': 'Applicant Name', 'fieldType': 'text', 'required': True, 'dataSource': 'name'},
            {'fieldId': 'father_name', 'fieldLabel': "Father's Name", 'fieldType': 'text', 'required': True, 'dataSource': 'father_name'},
            {'fieldId': 'date_of_birth', 'fieldLabel': 'Date of Birth', 'fieldType': 'date', 'required': True, 'dataSource': 'dob'},
            {'fieldId': 'gender', 'fieldLabel': 'Gender', 'fieldType': 'select', 'required': True, 'dataSource': 'gender', 'options': ['Male', 'Female', 'Other']},
            {'fieldId': 'annual_income', 'fieldLabel': 'Annual Income (in INR)', 'fieldType': 'text', 'required': True},
            {'fieldId': 'address', 'fieldLabel': 'Address', 'fieldType': 'textarea', 'required': True, 'dataSource': 'address'}
        ]
    },
    'caste_certificate': {
        'formId': 'caste_certificate',
        'formName': 'Caste Certificate Application',
        'department': 'Revenue Department',
        'description': 'Application for Caste Certificate',
        'fields': [
            {'fieldId': 'applicant_name', 'fieldLabel': 'Applicant Name', 'fieldType': 'text', 'required': True, 'dataSource': 'name'},
            {'fieldId': 'father_name', 'fieldLabel': "Father's Name", 'fieldType': 'text', 'required': True, 'dataSource': 'father_name'},
            {'fieldId': 'date_of_birth', 'fieldLabel': 'Date of Birth', 'fieldType': 'date', 'required': True, 'dataSource': 'dob'},
            {'fieldId': 'caste_category', 'fieldLabel': 'Caste Category', 'fieldType': 'select', 'required': True, 'options': ['General', 'SC', 'ST', 'OBC']},
            {'fieldId': 'address', 'fieldLabel': 'Address', 'fieldType': 'textarea', 'required': True, 'dataSource': 'address'}
        ]
    }
}

def get_form_template(form_id):
    return FORM_TEMPLATES.get(form_id)

def get_all_forms():
    return [{
        'formId': f_id,
        'formName': f['formName'],
        'department': f['department'],
        'description': f['description']
    } for f_id, f in FORM_TEMPLATES.items()]
