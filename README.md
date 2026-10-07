# Job-Hunter# Job Hunter

Personal job monitoring and matching system.

The system collects jobs, applies cheap deterministic filters,
ranks candidates locally, evaluates only the strongest candidates
with an LLM, and sends relevant matches to Telegram.

## Architecture

Job sources
    ↓
Normalization
    ↓
Cheap filters
    ↓
Local scoring
    ↓
LLM matching
    ↓
Telegram notification

## Current status

The current version uses mock job data.

Real job sources will be added later.

## Requirements

- Python 3.12+
- OpenAI API key
- Telegram bot
- GitHub account for scheduled execution

## Local setup

Create a virtual environment:

```bash
python -m venv .venv