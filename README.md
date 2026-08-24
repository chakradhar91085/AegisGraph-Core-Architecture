# AegisGraph

**AegisGraph** is an advanced AI-powered Toxicity Detection & Moderation System prototyping secure, behavioral-aware Retrieval-Augmented Generation (RAG).

The core problem AegisGraph solves is the security vulnerability of standard RAG pipelines. Traditional RAG systems allow users to blindly query the underlying database via semantic search, making them highly susceptible to data exfiltration, probing, and unauthorized reconnaissance. AegisGraph introduces a continuous behavioral security layer that monitors semantic drift, temporal frequency, entity focus, and graph footprint to calculate a compounding **EWMA Risk Score**. As risk increases, an **Adaptive Policy Engine** dynamically limits the model's access to the graph (restricting context limits and graph depth) and can ultimately block malicious exploration before data is leaked.

## High-Level Architecture
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts (Passive Visualization Layer)
- **Backend**: FastAPI, Pydantic (Orchestrator & Security Engine)
- **Graph Database**: Neo4j (Data Storage & Cypher Execution)
- **Retrieval Engine**: SentenceTransformers (`all-MiniLM-L6-v2`) for intent/entity classification
- **Language Model**: Ollama (`qwen3:8b` or equivalent)

## Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Neo4j Desktop / Server** running with the Enron dataset ingested.
- **Ollama** installed and running locally with the target model (e.g., `ollama run qwen3:8b`).

### 1. Database & LLM Preparation
1. Ensure your Neo4j database is active on `bolt://localhost:7687`.
2. Ensure Ollama is running on `http://localhost:11434`.

### 2. Backend Setup
Navigate to the `backend` directory:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Or `source venv/bin/activate` on Unix
pip install -r requirements.txt
```
Ensure your `.env` file matches `.env.example` with your Neo4j credentials:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```
Start the backend server:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000/api/v1`.

### 3. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
Access the AegisGraph demonstration dashboard at `http://localhost:5173`.

## Demonstration & Documentation
AegisGraph is heavily documented by phase. 
- To conduct a project review or demonstration, refer directly to `backend/docs/Phase7B_Final_Demonstration_and_Project_Readiness.md` for curated demonstration scenarios and a readiness checklist.
- Detailed architecture, design decisions, and evaluation results can be found in the `backend/docs` folder.
