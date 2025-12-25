# UPSC Current Affairs Syncer

A comprehensive data syncer that fetches current affairs articles from various sources and stores them in a structured format in PostgreSQL.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Querying Articles](#querying-articles)
- [Adding New Sources](#adding-new-sources)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project fetches current affairs articles from educational websites (starting with Sanskriti IAS) and stores them in a standardized JSON format in PostgreSQL. The articles include:
- Structured content sections
- Prelims/Mains metadata tags
- FAQs
- Images
- Publication dates

## 📁 Project Structure

```
syncer/
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   └── postgres.py          # PostgreSQL database operations
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py              # Base source class
│   │   └── sanskriti.py         # Sanskriti IAS scraper
│   └── models/
│       ├── __init__.py
│       └── article.py           # Article data model
├── scripts/
│   ├── sync_sanskriti.py        # Main sync script
│   └── test_sanskriti.py        # Test script
├── logs/                         # Log files (auto-created)
├── docs/
│   ├── article_schema.json      # JSON schema definition
│   ├── article_example.json     # Example article
│   └── SCHEMA_SIMPLIFIED.md     # Schema documentation
├── docker-compose.yml           # Docker services configuration
├── Dockerfile                   # Docker image for syncer
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## ✅ Prerequisites

1. **Docker Desktop** (for running PostgreSQL)
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure Docker is running before starting

2. **Python 3.8+**
   - Check version: `python --version`

3. **Git** (optional, for cloning)

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd syncer
pip install -r requirements.txt
```

### Step 2: Start PostgreSQL Database

The project uses Docker Compose to run PostgreSQL. You have two options:

#### Option A: Start only PostgreSQL (Recommended for development)

```bash
docker-compose up -d postgres
```

#### Option B: Start all services (PostgreSQL + Qdrant + Syncer)

```bash
docker-compose up -d
```

**Verify PostgreSQL is running:**

```bash
docker ps
```

You should see `upsc-postgres` in the list with status "Up" and "(healthy)".

**Database Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `upsc_postgres`
- User: `upsc_db_admin`
- Password: `upsc_sanjeet@1729`

### Step 3: Test the Scraper (Optional but Recommended)

Before running a full sync, test that the scraper is working:

```bash
python scripts/test_sanskriti.py
```

This will fetch articles from the last 2 days and show you the structure.

### Step 4: Run the Syncer

Sync articles from Sanskriti IAS:

```bash
# Sync last 30 days (1 month)
python scripts/sync_sanskriti.py --days 30

# Or sync last 7 days (1 week)
python scripts/sync_sanskriti.py --days 7
```

The sync will:
1. Connect to PostgreSQL
2. Initialize the database schema (if needed)
3. Fetch articles day by day
4. Store them in the `ca_articles` table
5. Skip duplicates automatically
6. Show progress and summary

**Logs are saved to:** `logs/sanskriti_sync_YYYYMMDD_HHMMSS.log`

## 📖 Usage

### Running the Syncer

```bash
# Basic usage - sync last 30 days
python scripts/sync_sanskriti.py

# Specify custom number of days
python scripts/sync_sanskriti.py --days 60

# Get help
python scripts/sync_sanskriti.py --help
```

### Monitoring Progress

The syncer logs to both console and a log file. Watch for:
- ✓ Articles fetched per day
- ✓ Successfully inserted count
- ✓ Duplicates skipped
- ✓ Any errors

### Stopping the Database

```bash
# Stop PostgreSQL but keep data
docker-compose stop postgres

# Stop and remove containers (data persists in volumes)
docker-compose down

# Stop and remove everything including data (⚠️ WARNING: This deletes all articles!)
docker-compose down -v
```

## 🗄️ Database Schema

### Table: `ca_articles`

```sql
CREATE TABLE ca_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    published_date DATE NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    article JSONB NOT NULL,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT now()
);
```

### Article JSON Structure

```json
{
  "title": "Article Title",
  "source": "Sanskriti IAS",
  "metadata": {
    "prelims": "Topics for Prelims",
    "mains": "GS Papers + Topics",
    "tags": []
  },
  "content": [
    {
      "heading": "Section Name",
      "subheading": null,
      "content": "Text with \\n for newlines and • for bullets"
    }
  ],
  "faqs": [
    {
      "question": "Question text?",
      "answer": "Answer text."
    }
  ],
  "images": [
    {
      "url": "https://...",
      "alt": "Alt text",
      "caption": "Caption"
    }
  ],
  "extracted_at": "2025-12-25T19:30:00.000000"
}
```

See `docs/article_schema.json` for the complete JSON schema.

## 🔍 Querying Articles

### Using Docker CLI

```bash
# Connect to PostgreSQL
docker exec -it upsc-postgres psql -U upsc_db_admin -d upsc_postgres

# Once connected, run queries:
```

### Example Queries

**1. Count all articles:**
```sql
SELECT COUNT(*) FROM ca_articles;
```

**2. Count articles by source:**
```sql
SELECT 
    article->>'source' as source,
    COUNT(*) as total
FROM ca_articles
GROUP BY article->>'source';
```

**3. Articles by date:**
```sql
SELECT 
    published_date,
    COUNT(*) as articles
FROM ca_articles
GROUP BY published_date
ORDER BY published_date DESC
LIMIT 10;
```

**4. Search by title:**
```sql
SELECT 
    article->>'title' as title,
    published_date,
    source_url
FROM ca_articles
WHERE article->>'title' ILIKE '%ISRO%'
ORDER BY published_date DESC;
```

**5. Articles with FAQs:**
```sql
SELECT 
    article->>'title' as title,
    jsonb_array_length((article->'faqs')::jsonb) as faq_count,
    published_date
FROM ca_articles
WHERE jsonb_array_length((article->'faqs')::jsonb) > 0
ORDER BY published_date DESC;
```

**6. Filter by Prelims topic:**
```sql
SELECT 
    article->>'title' as title,
    article->'metadata'->>'prelims' as prelims_topic
FROM ca_articles
WHERE article->'metadata'->>'prelims' ILIKE '%Space Technology%';
```

**7. Get recent articles:**
```sql
SELECT 
    article->>'title' as title,
    article->>'source' as source,
    published_date
FROM ca_articles
ORDER BY published_date DESC
LIMIT 10;
```

**8. Articles with most content sections:**
```sql
SELECT 
    article->>'title' as title,
    jsonb_array_length((article->'content')::jsonb) as sections,
    published_date
FROM ca_articles
ORDER BY sections DESC
LIMIT 10;
```

## 🔧 Adding New Sources

To add a new source (e.g., Drishti IAS, Vision IAS):

1. **Create source module:** `app/sources/your_source.py`
   ```python
   class YourSource:
       def __init__(self):
           self.source_name = "Your Source"
       
       def fetch_articles(self, days_back):
           # Implement fetching logic
           pass
   ```

2. **Create sync script:** `scripts/sync_your_source.py`
   - Copy `scripts/sync_sanskriti.py`
   - Update to use your source class

3. **Follow the JSON schema:** Output articles in the standardized format

4. **Test it:** Create a test script similar to `scripts/test_sanskriti.py`

## ❗ Troubleshooting

### Docker Issues

**Problem:** `docker-compose` command not found
```bash
# Try:
docker compose up -d postgres
# (without the hyphen)
```

**Problem:** Port 5432 already in use
```bash
# Stop any existing PostgreSQL instances
docker ps
docker stop upsc-postgres

# Or change the port in docker-compose.yml
```

**Problem:** Container name conflict
```bash
# Remove existing container
docker rm upsc-postgres

# Then start again
docker-compose up -d postgres
```

### Database Connection Issues

**Problem:** Connection refused
```bash
# Check if PostgreSQL is running
docker ps

# Check if it's healthy
docker logs upsc-postgres

# Wait for health check
docker-compose ps
```

**Problem:** Authentication failed
- Check credentials in `app/db/postgres.py`
- Verify they match `docker-compose.yml`

### Syncer Issues

**Problem:** No articles fetched
- Check your internet connection
- Verify the website URL is accessible
- Check logs in `logs/` folder

**Problem:** Import errors
```bash
# Make sure you're in the syncer directory
cd syncer

# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Current Status

✅ **Sanskriti IAS Source:** Fully implemented and tested
- ✅ Fetches articles from date-based URLs
- ✅ Extracts all content sections
- ✅ Parses metadata (Prelims/Mains tags)
- ✅ Captures FAQs and images
- ✅ Handles 30+ days of data

📝 **To Be Implemented:**
- Drishti IAS source
- Vision IAS source
- Next IAS source
- PMF IAS source
- And others from `docs/syncer_sources.md`

## 📝 Notes

- The syncer is polite: It waits 1 second between requests to avoid overloading servers
- Duplicate articles are automatically skipped (based on source_url)
- All data is stored in JSONB format for flexible querying
- Logs are timestamped and saved for each run
- The database schema is automatically created on first run

## 📄 License

See LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please:
1. Test your changes thoroughly
2. Follow the existing code structure
3. Update documentation
4. Add tests for new sources

---

For questions or issues, check the logs in the `logs/` folder or review the error messages in the console output.
