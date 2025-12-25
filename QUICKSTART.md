# Quick Start Guide

Get up and running with the UPSC Current Affairs Syncer in 5 minutes!

## 🚀 Quick Steps

### 1. Install Dependencies (1 minute)

```bash
cd syncer
pip install -r requirements.txt
```

### 2. Start Database (30 seconds)

```bash
docker-compose up -d postgres
```

Wait for PostgreSQL to be healthy (check with `docker ps`).

### 3. Test the Scraper (Optional - 30 seconds)

```bash
python scripts/test_sanskriti.py
```

### 4. Run First Sync (2-3 minutes)

```bash
# Sync last 7 days
python scripts/sync_sanskriti.py --days 7
```

### 5. Verify Data (30 seconds)

```bash
docker exec upsc-postgres psql -U upsc_db_admin -d upsc_postgres -c "SELECT COUNT(*) FROM ca_articles;"
```

## ✅ You're Done!

Check the full README.md for:
- Complete documentation
- Database queries
- Troubleshooting
- Adding new sources

## 📊 Next Steps

### Sync More Data

```bash
# Sync 1 month
python scripts/sync_sanskriti.py --days 30

# Sync 2 months
python scripts/sync_sanskriti.py --days 60
```

### Query Articles

```bash
# Connect to database
docker exec -it upsc-postgres psql -U upsc_db_admin -d upsc_postgres

# Run queries (see README.md for examples)
```

### Check Logs

```bash
# Logs are in:
cd logs
ls
# Or on Windows:
dir logs
```

## ⚠️ Common Issues

**Docker not running?**
```bash
# Start Docker Desktop first, then:
docker-compose up -d postgres
```

**Import errors?**
```bash
# Make sure you're in the syncer directory:
cd syncer
pip install -r requirements.txt
```

**Port 5432 in use?**
```bash
# Stop existing PostgreSQL:
docker stop upsc-postgres
# Then start fresh:
docker-compose up -d postgres
```

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Estimated times:**
- Setup: 2 minutes
- First sync (7 days): 2 minutes
- Full sync (30 days): 5 minutes

