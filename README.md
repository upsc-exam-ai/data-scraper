# UPSC AI News Syncer

Python-based data ingestion service for current affairs articles.

## Directory Structure

```
syncer/
├── app/
│   ├── db/              # Database connections (PostgreSQL, Qdrant)
│   ├── models/          # Data models (Article)
│   ├── parser/          # Text cleaning utilities
│   ├── sources/         # News source implementations (PIB)
│   ├── sync.py          # Sync orchestration
│   └── main.py          # Entry point
├── requirements.txt
├── Dockerfile
└── README.md
```

## Features

- **Idempotent**: Running multiple times won't create duplicates
- **Source-agnostic**: Easy to add new news sources
- **Dual storage**: PostgreSQL for relational data, Qdrant for vector search
- **Clean architecture**: Modular, testable, extensible

## Current Sources

- **PIB (Press Information Bureau)**: RSS feed from pib.gov.in

## Usage

### Local Development

1. Install dependencies:
```bash
cd syncer
pip install -r requirements.txt
```

2. Set environment variables (optional, defaults to localhost):
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=upsc_postgres
export POSTGRES_USER=upsc_db_admin
export POSTGRES_PASSWORD=upsc_sanjeet@1729
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

3. Run the syncer:
```bash
python -m app.main --days 7
```

4. Test connectivity:
```bash
python -m app.main --test
```

### Docker (Recommended)

Run with docker-compose from the root:
```bash
docker-compose up syncer
```

Or run manually:
```bash
docker-compose run --rm syncer python -m app.main --days 7
```

## Database Schema

### PostgreSQL: `news_articles`

| Column         | Type      | Description                |
|----------------|-----------|----------------------------|
| id             | UUID      | Primary key                |
| source         | TEXT      | Source identifier (e.g., "PIB") |
| title          | TEXT      | Article title              |
| published_date | DATE      | Publication date           |
| url            | TEXT      | Article URL (unique)       |
| raw_text       | TEXT      | Original content           |
| cleaned_text   | TEXT      | Processed content          |
| created_at     | TIMESTAMP | Ingestion timestamp        |

### Qdrant: `current_affairs` Collection

- Vector size: 768
- Distance metric: Cosine
- Payload: source, title, url, published_date

## Adding New Sources

1. Create a new file in `app/sources/` (e.g., `hindu.py`)
2. Extend `NewsSource` base class
3. Implement `fetch_articles()` and `parse_article()`
4. Register in `app/sync.py`

Example:
```python
from .base import NewsSource
from ..models.article import Article

class HinduSource(NewsSource):
    def __init__(self):
        super().__init__("TheHindu")
    
    def fetch_articles(self, days_back: int = 7):
        # Your implementation
        pass
```

## Design Principles

- **Idempotent**: URL-based deduplication
- **Fault-tolerant**: Failed articles don't stop the sync
- **Observable**: Comprehensive logging
- **Testable**: Clear separation of concerns

## Next Steps (Future)

- Add more sources (The Hindu, Indian Express, etc.)
- Real embeddings (OpenAI, Sentence Transformers)
- Event extraction
- Semantic tagging
- Scheduled cron jobs

