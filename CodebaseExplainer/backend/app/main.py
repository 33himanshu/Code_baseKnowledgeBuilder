from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from datetime import timedelta
from .services.tutorial_generator import TutorialGenerator
from .services.github_service import GitHubService
from .services.llm_service import LLMService

load_dotenv()

app = FastAPI(
    title="Codebase Explainer API",
    description="API for generating beginner-friendly tutorials from codebases",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
tutorial_generator = TutorialGenerator()
github_service = GitHubService()
llm_service = LLMService()

# Models
class TutorialRequest(BaseModel):
    repo_url: str
    language: str = "english"
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    max_file_size: Optional[int] = 100000

class TutorialResponse(BaseModel):
    status: str
    chapters: List[Dict]
    diagrams: List[Dict]
    code_snippets: List[Dict]
    generated_at: str

@app.post("/api/generate-tutorial", response_model=TutorialResponse)
async def generate_tutorial(request: TutorialRequest):
    try:
        # Validate repository access
        if not github_service.validate_repo(request.repo_url):
            raise HTTPException(status_code=400, detail="Invalid repository URL")

        # Generate tutorial
        tutorial = await tutorial_generator.generate(
            repo_url=request.repo_url,
            language=request.language,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            max_file_size=request.max_file_size
        )

        return tutorial

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
