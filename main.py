from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
import zipfile
import os
import openai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
AI_PROXY_API_KEY = os.getenv("AI_PROXY_API_KEY")

if not AI_PROXY_API_KEY:
    raise RuntimeError("⚠ Missing AI Proxy API Key. Set it in the .env file.")

app = FastAPI()

# Define API request model
class QuestionRequest(BaseModel):
    question: str

@app.post("/api/")
async def answer_question(
    question: str = Form(...), 
    file: UploadFile = None  # File is optional
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="❌ Question cannot be empty.")

    # Handle file upload (if provided)
    if file:
        file_path = f"sample_data/{file.filename}"
        os.makedirs("sample_data", exist_ok=True)  # Ensure directory exists

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # If it's a ZIP file, extract it
        if file.filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall("sample_data")

    try:
        # AI Proxy API Call (GPT-4o-Mini)
        response = openai.ChatCompletion.create(
            api_key=AI_PROXY_API_KEY,  # Use AI Proxy key
            model="gpt-4o-mini",  # Ensure AI Proxy supports this model
            messages=[{"role": "user", "content": question}]
        )

        answer = response["choices"][0]["message"]["content"]

        return {
            "question": question,
            "answer": answer,
            "filename": file.filename if file else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"⚠ Unexpected Error: {str(e)}")
