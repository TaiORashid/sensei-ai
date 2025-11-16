"""
FastAPI server for the Agent Backend.

This provides REST API endpoints for the Next.js frontend to interact
with the agent system.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from orchestrator import AgentOrchestrator
import asyncio

app = FastAPI(title="Sensei Agent Backend", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()


class ProcessRequest(BaseModel):
    """Request model for processing options"""
    num_quiz_questions: int = 10


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sensei Agent Backend",
        "version": "1.0.0"
    }


@app.post("/api/process-document")
async def process_document(
    file: UploadFile = File(...),
    num_quiz_questions: int = 10
):
    """
    Process a PDF document through all agents.
    
    Returns:
        Complete analysis including structure, highlights, explanations, and quiz
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process the document
        results = await orchestrator.process_document(
            pdf_path=tmp_path,
            num_quiz_questions=num_quiz_questions
        )
        
        return {
            "success": True,
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/structure")
async def get_structure(file: UploadFile = File(...)):
    """Get only the document structure"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        results = await orchestrator.process_single_feature(
            pdf_path=tmp_path,
            feature="structure"
        )
        return {"success": True, "data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/highlights")
async def get_highlights(file: UploadFile = File(...)):
    """Get document highlights"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        results = await orchestrator.process_single_feature(
            pdf_path=tmp_path,
            feature="highlights"
        )
        return {"success": True, "data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/explanations")
async def get_explanations(file: UploadFile = File(...)):
    """Get document explanations"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        results = await orchestrator.process_single_feature(
            pdf_path=tmp_path,
            feature="explanations"
        )
        return {"success": True, "data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/quiz")
async def get_quiz(
    file: UploadFile = File(...),
    num_questions: int = 10
):
    """Generate quiz questions"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        results = await orchestrator.process_single_feature(
            pdf_path=tmp_path,
            feature="quiz",
            num_questions=num_questions
        )
        return {"success": True, "data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
