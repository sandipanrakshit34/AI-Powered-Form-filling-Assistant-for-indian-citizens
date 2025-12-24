# AI-Powered Form Filling Assistant for Indian Citizen Services

## 📌 Problem Statement 3  
**AI-Powered Form Filling Assistant for Indian Citizen Services**

Citizens in India frequently need to fill multiple government service forms at Seva Kendras for certificates, licenses, and welfare schemes. This process is largely manual, repetitive, time-consuming, and prone to errors. Applicants often have to re-enter the same personal details across different forms, leading to inefficiency and user frustration.

This project aims to build an **AI-powered system** that automatically extracts relevant information from uploaded identity documents (such as Aadhaar, PAN, Voter ID, etc.) and intelligently auto-fills government service forms, significantly reducing manual effort and errors.

### Core Objectives
- Automate form filling using AI and OCR  
- Reduce processing time and human errors  
- Improve accessibility and efficiency at Seva Kendras  

---

## 🚀 What We Have Built

We developed a **full-stack web application** that:
- Accepts identity documents in **PDF or image format**
- Extracts key personal details using **OCR + AI**
- Automatically maps extracted data to government form fields
- Allows users to **review and edit** before final submission
- Exports completed forms as **PDF or JSON**
- Processes data securely without permanent storage

The system follows a modular, privacy-first, and scalable architecture suitable for real-world deployment.

---

## ✨ Features

- 📄 **Document Upload** (PDF / JPG / PNG)
- 🔍 **OCR-based Text Extraction** (multi-language support)
- 🤖 **AI-powered Entity Extraction** (Name, DOB, Address, ID numbers, etc.)
- 🧠 **Intelligent Form Mapping** using fuzzy matching
- ✍️ **User Review & Edit** before export
- 📥 **Download Filled Forms** (PDF & JSON)
- 🌐 **Web-based Interface**
- 🔐 **Privacy-first Design** (no data persistence)

---

## 🛠️ Technologies Used

### Frontend
- React.js (Vite)
- HTML, CSS, JavaScript
- Axios (API communication)

### Backend
- Python
- Flask (REST API)
- Flask-CORS

### AI & OCR
- EasyOCR (multi-language OCR)
- Groq API (LLaMA-3.3-70B model)
- PyMuPDF, Pillow, OpenCV

### Output & Utilities
- PDF generation
- JSON export
- Regex-based validation
- Fuzzy string matching


---

## ⚙️ How to Run the Project (Local Setup)

### 🔹 Backend Setup

```bash
cd backend
```
#### Create and activate virtual environment
```
python -m venv venv
venv\Scripts\activate
```
#### Install dependencies
```
pip install -r requirements.txt
```
#### Configure environment variables
#### Create a .env file:
```
GROQ_API_KEY=your_groq_api_key_here
```
#### Start backend server
```
python app.py
```
#### Backend will start at:
```
http://localhost:6001
```
### 🔹 Frontend Setup
```
cd form-extractor-vite
```
#### Install dependencies
```
npm install
```
#### Start development server
```
npm run dev
```
#### Frontend will be available at:
```
http://localhost:5173
```

## 🌐 Deployment Overview

- Backend can be deployed using Gunicorn or similar WSGI servers
- Frontend can be built using npm run build and hosted on any static server
- Designed and tested on Intel-based hardware
- Supports local as well as server-based deployment

## 📊 Performance Targets Achieved

- Entity Extraction Accuracy: ~95%
- Average Processing Time: 2–4 seconds per document
- Auto-fill Success Rate: 60–85%
- Stateless, secure, and privacy-compliant design

## 🔮 Future Enhancements

- Handwritten text recognition
- Full voice-based form filling
- Integration with DigiLocker and Government APIs
- Mobile application support
- Expanded regional language support

---

## 👨‍💻 Developed By

- **Sandipan Rakshit**
- **Chinmoy Das**
- **Sourangshu Kundu**

---

## 🎓 Mentored By

- **Mr. Puspen Lahiri**  
  Assistant Professor  
  **MCKV Institute of Engineering**

---

## 🎓 Academic & Internship Details

- Developed in fulfillment of Summer Internship
- MCKV Institute of Engineering
- In collaboration with Intel® (Intel Unnati Industrial Training Program)

