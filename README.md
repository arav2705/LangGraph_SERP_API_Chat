# LangGraph Research Agent

A small mini-project that uses a LangGraph-style workflow to turn a user prompt into a search-driven answer.

## What this project does

- Takes a user prompt
- Searches the web using SerpAPI
- Summarizes the search results with an LLM
- Returns a concise answer in a graph-based workflow

## Files

- `main.py` - the agent script
- `requirements.txt` - Python dependencies

## Setup

1. Install Python (if not already installed).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variables:
   - `SERPAPI_API_KEY` — your SerpAPI key
   - `OPENAI_API_KEY` — optional if you want to use OpenAI instead of local Ollama
   - `USE_LOCAL_LLM=false` — optional to force OpenAI usage

Example on Windows:
```powershell
setx SERPAPI_API_KEY "your-serpapi-key"
setx OPENAI_API_KEY "your-openai-key"
```

## Run

```bash
python main.py
```

Then type a prompt like:

> "Research why LangGraph is useful for building autonomous AI agents."

