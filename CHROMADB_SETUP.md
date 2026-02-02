# ChromaDB Integration Guide

## Overview

ChromaDB has been successfully integrated into your Django application. ChromaDB is a vector database that works alongside Django's SQLite database to provide semantic search capabilities for contact messages.

## Architecture

- **Primary Database**: SQLite (Django's default) - stores structured data (users, contact messages)
- **Vector Database**: ChromaDB - stores contact messages as vectors for semantic search

## Features

1. **Automatic Sync**: Contact messages are automatically saved to ChromaDB when created
2. **Semantic Search**: Search contact messages using natural language queries
3. **Dashboard Integration**: View ChromaDB connection status on the dashboard
4. **Search Page**: Dedicated search interface for querying messages

## Configuration

ChromaDB is configured in `myproject/settings.py`:
- `CHROMA_DB_PATH`: Location where ChromaDB data is stored (default: `chroma_db/` directory)
- `CHROMA_COLLECTION_NAME`: Name of the collection (default: `main_collection`)

## Usage

### Testing the Connection

Run the test command to verify ChromaDB is working:
```bash
python manage.py test_chromadb
```

### Using ChromaDB in Code

```python
from main.chromadb_service import ChromaDBService

# Add documents
ChromaDBService.add_documents(
    documents=["Your text here"],
    ids=["unique_id"],
    metadatas=[{"key": "value"}]
)

# Query documents
results = ChromaDBService.query(
    query_texts=["search query"],
    n_results=10,
    include=['documents', 'metadatas', 'distances']
)

# Get all documents
all_docs = ChromaDBService.get_all()

# Delete documents
ChromaDBService.delete(ids=["id_to_delete"])
```

### Accessing Search Feature

1. Log in to your account
2. Go to Dashboard
3. Click "Search Messages" button
4. Enter your search query
5. View semantic search results

## How It Works

1. When a contact message is submitted:
   - It's saved to SQLite (Django database)
   - It's automatically synced to ChromaDB as a vector
   - Metadata (name, email, timestamp) is stored with the vector

2. When searching:
   - Your query is converted to a vector
   - ChromaDB finds similar vectors (semantic similarity)
   - Results are ranked by relevance

## Files Created/Modified

- `main/chromadb_service.py` - ChromaDB service class
- `main/models.py` - Added `chroma_id` field and auto-sync signal
- `main/views.py` - Added search view and dashboard ChromaDB stats
- `main/urls.py` - Added search URL route
- `main/templates/main/dashboard.html` - Added ChromaDB status card
- `main/templates/main/search.html` - Search interface
- `main/management/commands/test_chromadb.py` - Test command
- `myproject/settings.py` - ChromaDB configuration
- `requirements.txt` - Added chromadb package

## Database Location

ChromaDB data is stored in: `chroma_db/` directory (in your project root)

## Notes

- ChromaDB works alongside Django's database, not as a replacement
- Contact messages are stored in both databases for different purposes:
  - SQLite: Structured queries, admin panel, relationships
  - ChromaDB: Semantic search, similarity matching
- The `chroma_id` field in ContactMessage links Django records to ChromaDB documents
