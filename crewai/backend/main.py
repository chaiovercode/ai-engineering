import asyncio
import json
import os
import queue
import threading
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from crew_service import CrewService
from database import init_db, get_db
from models import ResearchResult

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize crew service
crew_service = CrewService()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

    # Log LangSmith status
    langsmith_enabled = os.getenv('LANGCHAIN_TRACING_V2', '').lower() == 'true'
    langsmith_project = os.getenv('LANGCHAIN_PROJECT', 'default')
    if langsmith_enabled:
        print(f"✓ LangSmith tracing enabled - Project: {langsmith_project}")
    else:
        print("○ LangSmith tracing disabled")


@app.get('/api/history')
async def get_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get research history"""
    results = db.query(ResearchResult)\
        .order_by(ResearchResult.created_at.desc())\
        .limit(limit)\
        .all()

    return {
        'items': [r.to_dict() for r in results],
        'total': db.query(ResearchResult).count()
    }


@app.get('/api/research/{id}')
async def get_research(id: str, db: Session = Depends(get_db)):
    """Get single research by ID"""
    research = db.query(ResearchResult).filter(ResearchResult.id == id).first()
    if not research:
        raise HTTPException(status_code=404, detail='Research not found')
    return research.to_dict()


@app.delete('/api/research/{id}')
async def delete_research(id: str, db: Session = Depends(get_db)):
    """Delete research by ID"""
    research = db.query(ResearchResult).filter(ResearchResult.id == id).first()
    if not research:
        raise HTTPException(status_code=404, detail='Research not found')

    db.delete(research)
    db.commit()
    return {'success': True}


@app.post('/api/generate')
async def generate_research(request: Request):
    """
    Generate research with real-time streaming via SSE
    """
    data = await request.json()
    input_text = data.get('input', '')
    input_type = data.get('type', 'topic')
    mode = data.get('mode', 'analytical')

    if not input_text:
        return {'error': 'Input is required'}

    async def stream_events():
        # Thread-safe queue for communication
        event_queue = queue.Queue()

        def collect_event(event):
            """Callback from crew_service to collect events"""
            event_queue.put(event)

        def run_crew():
            """Run crew in a thread"""
            try:
                crew_service.generate_research(input_text, input_type, mode, collect_event)
                event_queue.put(None)  # Signal completion
            except Exception as e:
                event_queue.put({
                    'type': 'error',
                    'message': str(e),
                })
                event_queue.put(None)

        # Start crew in background thread
        thread = threading.Thread(target=run_crew, daemon=True)
        thread.start()

        # Stream events from queue
        while True:
            try:
                event = event_queue.get(timeout=1)
                if event is None:
                    break
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.01)
            except queue.Empty:
                # Check if thread is still alive
                if not thread.is_alive():
                    break
                continue

    return StreamingResponse(stream_events(), media_type='text/event-stream')


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8008)
