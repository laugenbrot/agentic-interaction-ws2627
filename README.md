# agentic-interaction-ws2627

Agent for the course Agentic Interaction (WS 26/27, Ulm University).
Answers questions about a mock calendar by calling a tool: model → tool → model.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repository root (not committed):

```
OPENAI_BASE_URL=https://api.groq.com/openai/v1
MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=your-key
DATA_BASE_URL=https://jhbelz.github.io/agentic-interaction-data/v1
```

Environment variables override the `.env` values.

## Run

```bash
python -m agent "Was steht am 29.10.2026 im Kalender?"
```

The answer goes to standard output, exit code 0. Each run writes a JSONL log
file into `logs/` (not committed).
