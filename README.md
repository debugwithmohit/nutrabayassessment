# AI Resume Screener — FastAPI + Groq Backend

A REST API that accepts a job description and resume files (PDF/DOCX/TXT), extracts text, sends them to Groq (LLM), and returns ranked screening results.

---

## Project Structure

```
resume_screener/
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
├── frontend.html     # Drop-in frontend (open in browser)
├── .env              # Environment variables (API key)
└── README.md
```

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set your Groq API key

#### Option A: Using `.env` (Recommended)

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

---

#### Option B: Environment Variable

```bash
# macOS / Linux
export GROQ_API_KEY=gsk-...

# Windows (PowerShell)
$env:GROQ_API_KEY="gsk-..."
```

---

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

Server starts at:
http://127.0.0.1:8000

API documentation:
http://127.0.0.1:8000/docs

---

## API Reference

### POST /screen

Screen one or more resumes against a job description.

Content-Type: multipart/form-data

| Field     | Type            | Required | Description                        |
|-----------|-----------------|----------|------------------------------------|
| jd        | string (form)   | Yes      | Job description text               |
| resumes   | file[] (upload) | Yes      | One or more PDF / DOCX / TXT files |

---

### Response (200 OK)

```json
{
  "candidates": [
    {
      "name": "alice_resume.pdf",
      "rank": 1,
      "score": 87,
      "strengths": ["Strong SQL", "BI Tools experience", "A/B testing"],
      "gaps": ["No Python", "No ML exposure"],
      "recommendation": "Strong Fit"
    }
  ],
  "total": 3,
  "parse_errors": []
}
```

---

### GET /

Health check endpoint:

```json
{
  "status": "ok",
  "message": "AI Resume Screener API is running"
}
```

---

## Using the Frontend

1. Open `frontend.html` in your browser  
2. Set the Backend URL to:
   http://127.0.0.1:8000  
3. Paste a job description  
4. Upload resumes  
5. Click "Screen Candidates"

---

## Testing with curl

```bash
curl -X POST http://127.0.0.1:8000/screen \
  -F "jd=We need a senior data analyst with SQL, Python, and Tableau." \
  -F "resumes=@alice.pdf" \
  -F "resumes=@bob.docx"
```

---

## Supported File Types

| Extension | Parser        |
|----------|--------------|
| .pdf     | pdfplumber   |
| .docx    | python-docx  |
| .txt     | UTF-8 decode |

---

## Common Issues

### Invalid API Key (401)
- Ensure GROQ_API_KEY is set correctly
- Restart terminal after setting environment variables

---

### CORS Error
- Usually occurs when backend crashes
- Check backend logs in terminal
- Ensure FastAPI server is running

---

### API Not Responding
Check:
http://127.0.0.1:8000/docs

---

## Deployment (Quick)

### Using Render

1. Push code to GitHub  
2. Create a new Web Service on Render  
3. Configure:

```
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. Add Environment Variable:

```
GROQ_API_KEY=your_key
```

---

## Tech Stack

- FastAPI
- Groq API
- pdfplumber
- python-docx
- Vanilla JavaScript

---

## Future Improvements

- ATS keyword matching
- Resume summarization
- Candidate comparison charts
- Authentication and dashboard
- Database integration

---

## Author

Mohit Kulshreshtha