"""
Story Generator Backend API
FastAPI server for the AI-powered story generation service.
"""

import os
import datetime
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Import story generation functions
from stories import (
    research_story_concept,
    generate_story_from_plan,
    create_story_series,
    get_trending_topics,
    OUTPUT_DIR as STORIES_OUTPUT_DIR
)
import stories

# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="Story Generator API",
    description="AI-powered visual story creation for social media",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory setup
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BACKEND_DIR, "generated_stories")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure stories module to use our output dir
stories.OUTPUT_DIR = OUTPUT_DIR

# Serve generated images
app.mount("/images", StaticFiles(directory=OUTPUT_DIR), name="images")


# =============================================================================
# REQUEST MODELS
# =============================================================================

class StoryRequest(BaseModel):
    topic: str
    num_slides: int = 5
    aesthetic: str = ""


class TextToSlidesRequest(BaseModel):
    text: str
    topic: str = "Custom Content"
    num_slides: int = 5
    aesthetic: str = ""


class GenerateFromPlanRequest(BaseModel):
    plan: dict


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_story_folder(topic: str) -> tuple[str, str]:
    """Creates a unique folder for story output. Returns (folder_name, full_path)."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)[:20].strip()
    folder_name = f"{safe_topic}_{timestamp}"
    full_path = os.path.join(OUTPUT_DIR, folder_name)
    return folder_name, full_path


def files_to_urls(file_paths: list, folder_name: str) -> list:
    """Converts file paths to serving URLs."""
    return [
        f"http://localhost:8000/images/{folder_name}/{os.path.basename(f)}"
        for f in file_paths
    ]


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Story Generator API"}


@app.get("/trending_topics")
async def trending_topics(categories: str):
    """
    Get trending topic suggestions for one or more categories.
    Pass multiple categories comma-separated: ?categories=india,movies
    Categories: tech, ai, india, world, politics, sports, movies, business, finance, science
    """
    valid_categories = ["tech", "ai", "india", "world", "politics", "sports", "movies", "business", "finance", "science"]

    # Parse comma-separated categories
    category_list = [c.strip().lower() for c in categories.split(',') if c.strip()]

    if not category_list:
        raise HTTPException(status_code=400, detail="At least one category is required")

    for cat in category_list:
        if cat not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category '{cat}'. Choose from: {', '.join(valid_categories)}")

    try:
        topics = get_trending_topics(category_list)
        return {"categories": category_list, "topics": topics}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan_story")
async def plan_story(request: StoryRequest):
    """
    Phase 1: Research topic and create story plan.
    Returns plan for user review before image generation.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    if not 1 <= request.num_slides <= 10:
        raise HTTPException(status_code=400, detail="Slides must be between 1-10")

    try:
        plan = research_story_concept(
            topic=request.topic,
            num_slides=request.num_slides,
            user_aesthetic=request.aesthetic or None
        )

        if not plan:
            raise HTTPException(status_code=500, detail="Failed to research topic")

        return {"plan": plan}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan_from_text")
async def plan_from_text(request: TextToSlidesRequest):
    """
    Create story plan from user-provided text (no web research).
    Uses Gemini to extract key facts and create slides from pasted content.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text content is required")
    if not 1 <= request.num_slides <= 10:
        raise HTTPException(status_code=400, detail="Slides must be between 1-10")

    try:
        from stories import create_slides_from_text

        plan = create_slides_from_text(
            text=request.text,
            topic=request.topic or "Custom Content",
            num_slides=request.num_slides,
            user_aesthetic=request.aesthetic or None
        )

        if not plan:
            raise HTTPException(status_code=500, detail="Failed to create slides from text")

        return {"plan": plan}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_from_plan")
async def generate_from_plan(request: GenerateFromPlanRequest):
    """
    Phase 2: Generate images from approved plan.
    Returns URLs to generated images.
    """
    if not request.plan or 'topic' not in request.plan:
        raise HTTPException(status_code=400, detail="Valid plan is required")

    try:
        folder_name, output_path = create_story_folder(request.plan['topic'])
        generated_files = generate_story_from_plan(request.plan, output_dir=output_path)

        return {"images": files_to_urls(generated_files, folder_name)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Deprecated monolithic endpoint
@app.post("/generate")
async def generate_story(request: StoryRequest):
    """
    Single-call endpoint: Research and generate in one request.
    Combines both phases for simpler integration.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    if not 1 <= request.num_slides <= 10:
        raise HTTPException(status_code=400, detail="Slides must be between 1-10")

    try:
        folder_name, output_path = create_story_folder(request.topic)

        generated_files = create_story_series(
            topic=request.topic,
            num_slides=request.num_slides,
            user_aesthetic=request.aesthetic or None,
            output_dir=output_path
        )

        return {"images": files_to_urls(generated_files, folder_name)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n🚀 Starting Story Generator API...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
