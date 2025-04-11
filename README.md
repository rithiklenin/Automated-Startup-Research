# Automated Startup Research

A tool for automating the collection, storage, and analysis of startup information from online sources.

## Setup

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Automated-Startup-Research.git
   cd Automated-Startup-Research
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Reset the database with sample data (optional):
   ```bash
   python reset_db.py
   ```

### Running the Application

Start the API server:
```bash
python -m main
```

The server will run on `http://localhost:8000`.

## API Usage Examples

### Research New Startups

```bash
curl -X POST "http://localhost:8000/api/research" \
     -H "Content-Type: application/json" \
     -d '{"startups": ["Apple Inc.", "Microsoft Corporation"]}'
```

> **Note:** For best results, use full company names (e.g., "Apple Inc." instead of just "Apple")

### Get All Startups

```bash
curl -X GET "http://localhost:8000/api/startups"
```

### Get a Specific Startup

```bash
curl -X GET "http://localhost:8000/api/startups/apple-inc."
```

### Use Chat API

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Which startups are in the technology industry?"}'
```

## Key Features

- Collects data from Wikipedia and other online sources
- Stores startup information in a local SQLite database
- Supports natural language queries about the collected data
- API-first design for easy integration with other tools