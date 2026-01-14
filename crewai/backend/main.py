import asyncio
import json
import os
import queue
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from crew_service import CrewService

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

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

    uvicorn.run(app, host='127.0.0.1', port=8000)
