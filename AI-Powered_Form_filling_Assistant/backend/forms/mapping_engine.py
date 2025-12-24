# forms/mapping_engine.py
import json
import os


class FormMapper:
    def __init__(self, templates_dir="./forms/templates"):
        self.templates_dir = templates_dir
        self.templates = self._load_all_templates()

    def _load_all_templates(self):
        """Load all form templates into memory"""
        templates = {}
        for file in os.listdir(self.templates_dir):
            if file.endswith(".json"):
                with open(os.path.join(self.templates_dir, file)) as f:
                    form_data = json.load(f)
                    templates[form_data["formId"]] = form_data
        return templates

    def get_form(self, form_id):
        """Get specific form template"""
        return self.templates.get(form_id)

    def list_forms(self):
        """List all available forms"""
        return [
            {
                "formId": fid,
                "formName": self.templates[fid]["formName"],
                "description": self.templates[fid].get("description", ""),
            }
            for fid in self.templates.keys()
        ]

    def map_extracted_data_to_form(self, extracted_entities, form_id):
        """
        Auto-fill form fields with extracted data

        Args:
            extracted_entities: {name, dob, gender, aadhar, pan, address}
            form_id: birth_certificate, etc.

        Returns:
            Filled form with field values
        """
        form_template = self.get_form(form_id)
        if not form_template:
            return {"error": "Form not found"}

        filled_form = {
            "formId": form_id,
            "formName": form_template["formName"],
            "fields": [],
        }

        for field in form_template["fields"]:
            mapping_source = field.get("mappingSource")
            value = extracted_entities.get(mapping_source) if mapping_source else None

            field_entry = {
                "fieldId": field["fieldId"],
                "fieldLabel": field["fieldLabel"],
                "fieldType": field["fieldType"],
                "value": value,
                "required": field.get("required", False),
                "filled": value is not None,
            }
            filled_form["fields"].append(field_entry)

        return filled_form
