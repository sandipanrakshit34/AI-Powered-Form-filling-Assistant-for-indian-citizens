# backend/app.py - CORRECTED FOR YOUR FOLDER STRUCTURE
# Replace your current app.py with this

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the forms folder to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_utils import extract_text
from entity_extract import extract_entities_with_ai
from forms.templates import get_form_template, get_all_forms  # Import from YOUR location
from form_mapper import FormMapper  # Use YOUR existing form_mapper

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the form mapper (use existing form_mapper.py)
form_mapper = FormMapper()

# ============================================================================
# API 1: Get all available forms
# ============================================================================
@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get list of all available government forms"""
    try:
        forms = get_all_forms()
        print(f"[✓] Forms loaded: {len(forms)}")
        print(f"[✓] Available forms: {[f['formId'] for f in forms]}")
        return jsonify({'forms': forms})
    except Exception as e:
        print(f"[✗] Error loading forms: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API 2: Extract data from uploaded document
# ============================================================================
@app.route('/api/extract', methods=['POST'])
def extract():
    """Extract entities from uploaded document using OCR + AI"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        print("\n" + "="*60)
        print("[OCR] Processing:", file.filename)
        print("="*60)
        
        # Step 1: Extract text using OCR
        print(f"[OCR] Starting OCR for: {filepath}")
        ocr_text = extract_text(filepath)
        print(f"[OCR] Extracted text length: {len(ocr_text)} characters")
        
        # Step 2: Extract entities using AI
        print("[AI] Extracting entities with Groq...")
        entities = extract_entities_with_ai(ocr_text)
        print(f"[AI] Extracted entities: {entities}")
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(entities)
    
    except Exception as e:
        print(f"[✗] Server Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API 3: Auto-fill form with intelligent mapping
# ============================================================================
@app.route('/api/auto-fill', methods=['POST'])
def auto_fill():
    """Auto-fill a form using intelligent field mapping"""
    try:
        data = request.json
        extracted_entities = data.get('extracted_entities', {})
        form_id = data.get('form_id')
        
        print("\n" + "="*60)
        print("[MAPPING] Auto-filling form:", form_id)
        print("="*60)
        print(f"[MAPPING] Extracted entities: {extracted_entities}")
        
        # Get form template
        form_template = get_form_template(form_id)
        if not form_template:
            return jsonify({'error': f'Form {form_id} not found'}), 404
        
        print(f"[MAPPING] Form template loaded: {form_template['formName']}")
        
        # Use form_mapper to fill form
        mapping_result = form_mapper.auto_fill_form(extracted_entities, form_template)
        
        # Build response
        filled_form = {
            'formId': form_id,
            'formName': form_template['formName'],
            'department': form_template.get('department', ''),
            'description': form_template.get('description', ''),
            'fields': mapping_result.get('fields', []),
            'summary': mapping_result.get('summary', {})
        }
        
        print(f"[MAPPING] Mapping Summary:")
        print(f"  - Auto-filled: {mapping_result.get('summary', {}).get('auto_filled', 0)}")
        print(f"  - Manual required: {mapping_result.get('summary', {}).get('manual_required', 0)}")
        print(f"  - Confidence: {mapping_result.get('summary', {}).get('confidence_avg', 0)}%")
        
        return jsonify({'filledForm': filled_form})
    
    except Exception as e:
        print(f"[✗] Error auto-filling form: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI-Powered Form Filling Assistant - Backend Server")
    print("="*60)
    print("[✓] Flask CORS enabled")
    
    # Load forms on startup
    try:
        forms = get_all_forms()
        print(f"[✓] Forms loaded: {len(forms)}")
        print(f"[✓] Available forms: {[f['formId'] for f in forms]}")
    except Exception as e:
        print(f"[✗] Error loading forms: {e}")
    
    print(f"[✓] Server starting on http://localhost:6001")
    print("="*60 + "\n")
    
    app.run(port=6001, debug=True)