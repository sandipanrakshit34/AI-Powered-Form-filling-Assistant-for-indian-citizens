// FIXED VERSION - Install these packages:
// npm install jspdf html2canvas

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, ChevronRight, CheckCircle, AlertCircle, Loader, Moon, Sun, Download, Edit2, FileText } from 'lucide-react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [extractedDetails, setExtractedDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [availableForms, setAvailableForms] = useState([]);
  const [selectedForm, setSelectedForm] = useState(null);
  const [filledForm, setFilledForm] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState('upload');
  const [editMode, setEditMode] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    fetchForms();
  }, []);

  const fetchForms = async () => {
    try {
      const res = await axios.get('http://localhost:6001/api/forms');
      setAvailableForms(res.data.forms || []);
    } catch (err) {
      console.error('Error fetching forms:', err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadedFileName(e.target.files[0].name);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => setDragActive(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setUploadedFileName(e.dataTransfer.files[0].name);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await axios.post('http://localhost:6001/api/extract', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setExtractedDetails(res.data);
      setSuccessMessage('✓ Document processed successfully!');
      setActiveTab('forms');
      setTimeout(() => setSuccessMessage(''), 4000);
    } catch (err) {
      console.error('Upload error:', err);
      setErrorMessage('❌ Failed to extract details');
      setTimeout(() => setErrorMessage(''), 4000);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSelect = async (formId) => {
    setSelectedForm(formId);
    setFormLoading(true);
    setErrorMessage('');

    try {
      const res = await axios.post('http://localhost:6001/api/auto-fill', {
        extracted_entities: extractedDetails,
        form_id: formId,
      });
      
      if (res.data.filledForm) {
        setFilledForm(res.data.filledForm);
        setSuccessMessage('✓ Form auto-filled successfully!');
        setTimeout(() => setSuccessMessage(''), 3000);
      }
    } catch (err) {
      console.error('Error auto-filling form:', err);
      setErrorMessage('❌ Failed to auto-fill form');
      setFilledForm(null);
      setTimeout(() => setErrorMessage(''), 4000);
    } finally {
      setFormLoading(false);
    }
  };

  const handleFieldEdit = (fieldId, newValue) => {
    if (!filledForm) return;
    const updatedFields = filledForm.fields.map((field) =>
      field.fieldId === fieldId ? { ...field, value: newValue, filled: newValue !== '' } : field
    );
    setFilledForm({ ...filledForm, fields: updatedFields });
  };

  // Download as JSON
  const downloadFormJSON = () => {
    if (!filledForm) return;
    const dataStr = JSON.stringify(filledForm, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `form_${filledForm.formId}_${new Date().getTime()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setSuccessMessage('✓ JSON downloaded successfully!');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  // FIXED: Download as PDF using simple approach
  const downloadFormPDF = async () => {
    if (!filledForm) return;

    try {
      // Dynamically import jsPDF to avoid initialization issues
      const jsPDFModule = await import('jspdf');
      const jsPDF = jsPDFModule.jsPDF;

      // Create PDF
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      let yPosition = 15;
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 10;
      const contentWidth = pageWidth - 2 * margin;

      // Title
      pdf.setFontSize(18);
      pdf.setTextColor(102, 126, 234);
      pdf.text(filledForm.formName || 'Form', margin, yPosition);
      yPosition += 10;

      // Metadata
      pdf.setFontSize(9);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Form ID: ${filledForm.formId}`, margin, yPosition);
      yPosition += 5;

      if (filledForm.department) {
        pdf.text(`Department: ${filledForm.department}`, margin, yPosition);
        yPosition += 5;
      }

      yPosition += 3;

      // Divider
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;

      // Fields
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(10);

      filledForm.fields?.forEach((field) => {
        // Check page break
        if (yPosition > pageHeight - 15) {
          pdf.addPage();
          yPosition = 15;
        }

        // Field label
        pdf.setFont(undefined, 'bold');
        const label = `${field.fieldLabel || field.fieldId}${field.required ? ' *' : ''}:`;
        pdf.text(label, margin, yPosition);
        yPosition += 5;

        // Field value
        pdf.setFont(undefined, 'normal');
        const value = String(field.value || '(Not filled)');
        const wrappedText = pdf.splitTextToSize(value, contentWidth);
        pdf.text(wrappedText, margin, yPosition);
        yPosition += wrappedText.length * 4 + 3;
      });

      // Footer
      yPosition = pageHeight - 10;
      pdf.setFontSize(8);
      pdf.setTextColor(150, 150, 150);
      pdf.text(`Generated: ${new Date().toLocaleString()}`, margin, yPosition);

      // Save
      pdf.save(`form_${filledForm.formId}_${new Date().getTime()}.pdf`);

      setSuccessMessage('✓ PDF downloaded successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('PDF Error:', err);
      setErrorMessage(`❌ PDF Error: ${err.message}`);
      setTimeout(() => setErrorMessage(''), 4000);
    }
  };

  return (
    <div className={`app-wrapper ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="header-icon">📋</div>
            <div className="header-text">
              <h1>AI Form Filling Assistant</h1>
              <p>Automated Government Form Filling</p>
            </div>
          </div>
          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? <Sun size={22} /> : <Moon size={22} />}
          </button>
        </div>
      </header>

      {errorMessage && (
        <div className="message-banner error">
          <AlertCircle size={20} />
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="message-banner success">
          <CheckCircle size={20} />
          <span>{successMessage}</span>
        </div>
      )}

      <div className="app-container">
        <div className="tabs-container">
          <button className={`tab ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
            <Upload size={18} /> Step 1: Upload
          </button>
          <button className={`tab ${activeTab === 'forms' ? 'active' : ''}`} onClick={() => setActiveTab('forms')}>
            <ChevronRight size={18} /> Step 2: Form
          </button>
        </div>

        {activeTab === 'upload' && (
          <section className="upload-section">
            <h2>Upload Your Document</h2>
            <div className={`upload-box ${dragActive ? 'drag-active' : ''}`} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
              <Upload size={48} />
              <h3>Drag & drop your file</h3>
              <p>or</p>
              <label htmlFor="file-input" className="upload-link">click to browse</label>
              <input type="file" accept="image/*,.pdf" onChange={handleFileChange} className="file-input" id="file-input" />
            </div>

            {uploadedFileName && (
              <div className="file-preview-box">
                <CheckCircle size={20} />
                <span>{uploadedFileName}</span>
              </div>
            )}

            <button className="extract-btn" onClick={handleUpload} disabled={!selectedFile || loading}>
              {loading ? <><Loader size={20} className="spinner" /> Processing...</> : <><Upload size={20} /> Extract</>}
            </button>

            {Object.keys(extractedDetails).length > 0 && (
              <div className="extracted-card">
                <h3>✓ Extracted Information</h3>
                <div className="details-grid">
                  {Object.entries(extractedDetails).map(([key, value]) => (
                    <div key={key} className="detail-item">
                      <label>{key.replace(/_/g, ' ').toUpperCase()}</label>
                      <div>{String(value || 'N/A')}</div>
                    </div>
                  ))}
                </div>
                <button className="next-step-btn" onClick={() => setActiveTab('forms')}>
                  Proceed to Forms <ChevronRight size={18} />
                </button>
              </div>
            )}
          </section>
        )}

        {activeTab === 'forms' && (
          <section className="forms-section">
            <h2>Select Government Form</h2>
            {availableForms.length === 0 ? (
              <div className="no-data">
                <AlertCircle size={48} />
                <h3>No Forms Available</h3>
                <p>Ensure backend is running: python app.py</p>
              </div>
            ) : (
              <>
                <div className="forms-grid">
                  {availableForms.map((form) => (
                    <div key={form.formId} className={`form-card ${selectedForm === form.formId ? 'selected' : ''}`} onClick={() => handleFormSelect(form.formId)}>
                      <div className="form-card-icon">📝</div>
                      <h4>{form.formName}</h4>
                      <p className="form-dept">{form.department}</p>
                      <p className="form-desc">{form.description}</p>
                    </div>
                  ))}
                </div>

                {formLoading && (
                  <div className="loading-container">
                    <Loader size={48} className="spinner" />
                    <p>Auto-filling form...</p>
                  </div>
                )}

                {filledForm && !formLoading && (
                  <div className="filled-form-container">
                    <div className="form-preview-header">
                      <h3>📋 {filledForm.formName}</h3>
                      <button className={`edit-toggle ${editMode ? 'editing' : ''}`} onClick={() => setEditMode(!editMode)}>
                        <Edit2 size={18} /> {editMode ? 'Done' : 'Edit'}
                      </button>
                    </div>

                    <div className="form-stats">
                      <div className="stat-card"><div className="stat-number">{filledForm.summary?.auto_filled || 0}</div><div>Auto-Filled</div></div>
                      <div className="stat-card"><div className="stat-number">{filledForm.summary?.manual_required || 0}</div><div>Manual</div></div>
                      <div className="stat-card"><div className="stat-number">{filledForm.summary?.optional_fields || 0}</div><div>Optional</div></div>
                    </div>

                    {filledForm.fields && filledForm.fields.length > 0 ? (
                      <div className="form-fields-container">
                        {filledForm.fields.map((field) => (
                          <div key={field.fieldId} className={`form-field-wrapper ${field.required ? 'required' : ''}`}>
                            <label>{field.fieldLabel}{field.required && <span className="required-star">*</span>}{field.filled && <span className="filled-badge">✓</span>}</label>
                            {field.fieldType === 'select' ? (
                              <select value={field.value || ''} onChange={(e) => handleFieldEdit(field.fieldId, e.target.value)} disabled={!editMode}>
                                <option value="">Select...</option>
                                {field.options?.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                              </select>
                            ) : field.fieldType === 'textarea' ? (
                              <textarea value={field.value || ''} onChange={(e) => handleFieldEdit(field.fieldId, e.target.value)} rows="3" disabled={!editMode} />
                            ) : (
                              <input type={field.fieldType || 'text'} value={field.value || ''} onChange={(e) => handleFieldEdit(field.fieldId, e.target.value)} disabled={!editMode} />
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>No fields available</p>
                    )}

                    <div className="form-actions">
                      <button className="download-btn json-btn" onClick={downloadFormJSON}>
                        <Download size={18} /> Download JSON
                      </button>
                      <button className="download-btn pdf-btn" onClick={downloadFormPDF}>
                        <FileText size={18} /> Download PDF
                      </button>
                      <button className="new-form-btn" onClick={() => { setSelectedForm(null); setFilledForm(null); setSelectedFile(null); setExtractedDetails({}); setActiveTab('upload'); }}>Upload Another</button>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>
        )}
      </div>

      <footer className="app-footer">
        <p>🚀 AI Form Filling Assistant | Phase 1.4</p>
      </footer>
    </div>
  );
}

export default App;
