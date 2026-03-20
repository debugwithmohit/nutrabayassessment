from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from groq import Groq
import json
import io
import os
from dotenv import load_dotenv
load_dotenv()

# PDF & DOCX extraction
import pdfplumber
import docx as python_docx

# 🔥 Initialize Groq client (ENV variable recommended)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print(os.getenv("GROQ_API_KEY"))

app = FastAPI(title="AI Resume Screener API", version="2.0.0")

# ── Text extraction helpers ─────────────────────────────

def extract_pdf(data: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def extract_docx(data: bytes) -> str:
    doc = python_docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_pdf(data)
    elif name.endswith(".docx"):
        return extract_docx(data)
    elif name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {filename}")

# ── Routes ─────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("frontend.html", media_type="text/html")


@app.post("/screen")
async def screen_resumes(
    jd: str = Form(...),
    resumes: List[UploadFile] = File(...)
):
    if not jd.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    if not resumes:
        raise HTTPException(status_code=400, detail="At least one resume file is required.")

    candidates = []
    errors = []

    # ✅ Extract resume text
    for upload in resumes:
        raw = await upload.read()
        try:
            text = extract_text(upload.filename, raw)

            if not text.strip():
                errors.append(f"{upload.filename}: no readable text found.")
                continue

            candidates.append({
                "name": upload.filename,
                "text": text[:8000]  # 🔥 limit to avoid token overflow
            })

        except Exception as e:
            errors.append(f"{upload.filename}: {str(e)}")

    if not candidates:
        raise HTTPException(
            status_code=422,
            detail=f"No readable resumes. Errors: {'; '.join(errors)}"
        )

    # ── Prompt ─────────────────────────────────────────

    resume_block = "\n\n".join(
        f"=== CANDIDATE: {c['name']} ===\n{c['text']}"
        for c in candidates
    )

    prompt = f"""
You are an expert technical recruiter.

Analyze resumes against the job description.

Return ONLY valid JSON array (no markdown).

JOB DESCRIPTION:
{jd}

RESUMES:
{resume_block}

Format:
[
  {{
    "name": "filename",
    "score": 0-100,
    "strengths": ["..."],
    "gaps": ["..."],
    "recommendation": "Strong Fit | Moderate Fit | Not Fit"
  }}
]
"""

    # ── Groq API Call ─────────────────────────────────

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=1500,
            top_p=1,
            stream=False  # 🔥 IMPORTANT (easier parsing)
        )

        raw_response = completion.choices[0].message.content.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    # ── Clean JSON ────────────────────────────────────

    clean = raw_response.replace("```json", "").replace("```", "").strip()

    try:
        results = json.loads(clean)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Model returned invalid JSON.\nRaw output:\n{raw_response[:500]}"
        )

    # ── Sort & Rank ──────────────────────────────────

    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    for i, r in enumerate(results):
        r["rank"] = i + 1

    # ── Response ─────────────────────────────────────

    return JSONResponse(
        content={
            "candidates": results,
            "total": len(results),
            "parse_errors": errors
        }
    )


# ── Run server ───────────────────────────────────────

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)