# backend/form_mapper.py
# Complete Form Mapper Implementation
# Place at: backend/form_mapper.py

from difflib import SequenceMatcher

class FieldMapper:
    """
    Intelligent field mapping that matches extracted entities to form fields
    """
    
    def __init__(self):
        self.field_aliases = {
            'name': ['applicant_name', 'applicantname', 'full_name', 'fullname', 'person_name', 'name', 'applicant'],
            'dob': ['date_of_birth', 'dateofbirth', 'birth_date', 'birthdate', 'dob', 'birth', 'birthday'],
            'gender': ['gender', 'sex', 'male_female', 'gender_type'],
            'aadhar': ['aadhar', 'aadhaar', 'aadhar_number', 'aadhaarnumber', 'aadhaar_number', 'uid'],
            'pan': ['pan', 'pan_number', 'pannumber', 'pan_num'],
            'address': ['address', 'residential_address', 'residentialaddress', 'location', 'home_address'],
            'father_name': ['father_name', 'fathername', 'fathers_name', 'father'],
            'mother_name': ['mother_name', 'mothername', 'mothers_name', 'mother']
        }
    
    def normalize_key(self, key):
        """Normalize field key for comparison"""
        return str(key).lower().replace('_', '').replace(' ', '')
    
    def similarity_ratio(self, str1, str2):
        """Calculate similarity between two strings (0-1 scale)"""
        str1_norm = self.normalize_key(str1)
        str2_norm = self.normalize_key(str2)
        return SequenceMatcher(None, str1_norm, str2_norm).ratio()
    
    def find_best_match(self, search_key, candidates):
        """Find best matching field from candidates"""
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            similarity = self.similarity_ratio(search_key, candidate)
            score = int(similarity * 100)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match, best_score
    
    def get_standard_key(self, field_source):
        """Get standard key for a field source"""
        field_source_norm = self.normalize_key(field_source)
        
        for standard_key, aliases in self.field_aliases.items():
            for alias in aliases:
                if self.normalize_key(alias) == field_source_norm:
                    return standard_key
        
        return field_source


class FormMapper:
    """
    Main form mapper - maps extracted entities to form fields
    """
    
    def __init__(self):
        self.field_mapper = FieldMapper()
    
    def auto_fill_form(self, extracted_entities, form_template):
        """
        Auto-fill form with extracted entities
        
        Args:
            extracted_entities: Dict of extracted data (e.g., {'name': 'John', 'dob': '01-01-1990'})
            form_template: Form template with field definitions
        
        Returns:
            Dict with filled fields and summary statistics
        """
        filled_fields = []
        mapping_stats = {
            'auto_filled': 0,
            'manual_required': 0,
            'optional_empty': 0,
            'confidence_avg': 0
        }
        confidence_scores = []
        
        # Process each form field
        for form_field in form_template['fields']:
            field_id = form_field['fieldId']
            field_label = form_field['fieldLabel']
            required = form_field.get('required', False)
            data_source = form_field.get('dataSource')
            
            field_value = None
            confidence = 0
            matched_source = None
            
            # Strategy 1: Direct match with dataSource
            if data_source and data_source in extracted_entities:
                field_value = extracted_entities[data_source]
                confidence = 95
                matched_source = data_source
            
            # Strategy 2: Fuzzy match using aliases
            if not field_value and data_source:
                for entity_key, entity_value in extracted_entities.items():
                    similarity = self.field_mapper.similarity_ratio(data_source, entity_key)
                    score = int(similarity * 100)
                    
                    if score > 80 and not field_value:
                        field_value = entity_value
                        confidence = max(score - 10, 70)
                        matched_source = entity_key
            
            # Strategy 3: Match by field ID
            if not field_value:
                best_match, score = self.field_mapper.find_best_match(field_id, extracted_entities.keys())
                if score > 75:
                    field_value = extracted_entities[best_match]
                    confidence = max(score - 15, 60)
                    matched_source = best_match
            
            # Update statistics
            if field_value:
                mapping_stats['auto_filled'] += 1
                confidence_scores.append(confidence)
            elif required:
                mapping_stats['manual_required'] += 1
            else:
                mapping_stats['optional_empty'] += 1
            
            # Build field result
            filled_fields.append({
                'fieldId': field_id,
                'fieldLabel': field_label,
                'fieldType': form_field.get('fieldType', 'text'),
                'value': field_value or '',
                'filled': bool(field_value),
                'required': required,
                'options': form_field.get('options', []),
                'confidence': confidence,
                'matchedSource': matched_source
            })
        
        # Calculate average confidence
        if confidence_scores:
            mapping_stats['confidence_avg'] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        return {
            'fields': filled_fields,
            'summary': mapping_stats
        }
    
    def get_mapping_report(self, filled_fields):
        """
        Generate a mapping report showing what was matched and confidence
        """
        report = {
            'high_confidence': [],
            'medium_confidence': [],
            'low_confidence': [],
            'unmatched': []
        }
        
        for field in filled_fields:
            if not field['filled']:
                if field['required']:
                    report['unmatched'].append({
                        'fieldId': field['fieldId'],
                        'fieldLabel': field['fieldLabel'],
                        'reason': 'Required field - no match found'
                    })
            elif field['confidence'] >= 90:
                report['high_confidence'].append({
                    'fieldId': field['fieldId'],
                    'fieldLabel': field['fieldLabel'],
                    'value': field['value'],
                    'confidence': field['confidence'],
                    'matchedSource': field['matchedSource']
                })
            elif field['confidence'] >= 70:
                report['medium_confidence'].append({
                    'fieldId': field['fieldId'],
                    'fieldLabel': field['fieldLabel'],
                    'value': field['value'],
                    'confidence': field['confidence'],
                    'matchedSource': field['matchedSource']
                })
            else:
                report['low_confidence'].append({
                    'fieldId': field['fieldId'],
                    'fieldLabel': field['fieldLabel'],
                    'value': field['value'],
                    'confidence': field['confidence'],
                    'matchedSource': field['matchedSource']
                })
        
        return report