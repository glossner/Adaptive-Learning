# Adaptive Learning 3D

A re-envisioned adaptive learning system using a 3D Godot interface and a LangGraph-based Multi-Agent backend.

## Architecture

- **Frontend**: Godot 4.5+ (3D Library Interface)
- **Backend**: Python (FastAPI + LangGraph)

## Prerequisites

- Godot 4.5+
- Python 3.10+
- OpenAI API Key

## Setup & Running

### 1. Backend

1. Navigate to the root directory.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set your API Key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
4. Run the server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   Server will run at `http://127.0.0.1:8000`.

### 2. Frontend (Godot)

1. Open Godot Engine.
2. Import the project located in `godot_project/`.
3. Open `scenes/Library.tscn` and press Play (F5).
4. Enter a topic in the UI (e.g., "History of Rome") and click "Start Learning".
5. Chat with the agents!

## Features

- **3D Library Environment**: Visual metaphor for selecting topics.
- **Adaptive Agents**:
    - **Supervisor**: Routes requests.
    - **Teacher**: Explains concepts.
    - **ProblemGenerator**: Creates practice.
    - **Verifier**: Checks answers.
- **Persisted State**: Session memory via LangGraph.