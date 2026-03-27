# Project Support System

A Retrieval-Augmented Generation (RAG) based support system with separate user-facing and staff management interfaces.

## Overview

This project provides an intelligent support ticketing system that processes document uploads (PDFs), generates embeddings, and uses LLM capabilities to answer user queries with context-aware responses. The system consists of two main servers:

- **User Server**: Public-facing API for end users to submit queries and upload documents
- **Staff Server**: Administrative interface for staff to manage tickets, review queries, and resolve support issues

## Architecture

```
Project-Support-System/
├── shared/                 # Shared utilities and constants
├── staff_server/          # FastAPI staff administration server
│   ├── templates/         # HTML templates for admin dashboard
│   ├── utils/            # Staff utilities (PDF uploading, ticket management)
│   └── models/           # Database models
├── user_server/          # FastAPI user-facing server
│   ├── templates/        # HTML templates for user interface
│   ├── utils/           # User utilities (embeddings, LLM, file processing)
│   └── models/          # API response models
└── venv/                 # Python virtual environment
```

## Features

- **Document Processing**: Upload and process PDF files
- **Vector Embeddings**: Generate and store embeddings for semantic search (Pinecone)
- **RAG Retrieval**: Retrieve relevant documents based on user queries
- **LLM Integration**: Generate intelligent answers using Google Generative AI
- **Ticket Management**: Create, track, and resolve support tickets
- **Admin Dashboard**: Staff interface for ticket management and query review
- **Multi-user Support**: Handle multiple concurrent users and queries

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite
- **Vector Store**: Pinecone
- **LLM**: Google Generative AI
- **Server**: Uvicorn
- **PDF Processing**: pdfplumber, PyPDF
- **File Validation**: Custom file size and format validation

## Installation

### Prerequisites

- Python 3.8+
- pip or conda
- API keys for:
  - Google Generative AI
  - Pinecone Vector Store

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Project-Support-System
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r staff_server/requirements.txt
   # or
   pip install -r user_server/requirements.txt
   ```

4. **Configure environment variables**
   
   Create `.env` file in the root directory with your API keys and configuration:
   
   ```env
   # Root .env
   DATABASE_URL=sqlite:///./staff_tickets.db
   PINECONE_API_KEY=your_pinecone_api_key
   GOOGLE_API_KEY=your_google_api_key
   STAFF_PORT=8001
   USER_PORT=8000
   STAFF_SERVER_URL=http://localhost:8001
   DEBUG=True
   ```
   
   The `.env` file will be automatically loaded by both servers.

5. **Initialize databases**
   ```bash
   # Run each server's main.py to initialize database on startup
   ```

## Running the Application

### Start User Server
```bash
cd user_server
python -m uvicorn main:app --reload --port 8000
```

### Start Staff Server
```bash
cd staff_server
python -m uvicorn main:app --reload --port 8001
```

The applications will be available at:
- User Server: http://localhost:8000
- Staff Server: http://localhost:8001

## API Endpoints

### User Server

- `GET /` - User interface homepage
- `POST /ask` - Submit a query and get an answer
- `POST /upload` - Upload documents
- `GET /health` - Health check endpoint

### Staff Server

- `GET /` - Staff dashboard
- `GET /dashboard` - View ticket statistics
- `POST /upload-pdf` - Upload PDF for knowledge base
- `GET /tickets` - List all tickets
- `POST /tickets/{id}/resolve` - Resolve a ticket

## Project Structure

### `shared/`
- `constants.py` - Shared constants (allowed extensions, max file sizes)
- `__init__.py` - Package initialization

### `staff_server/`
- `main.py` - FastAPI application entry point
- `config.py` - Configuration settings
- `database.py` - Database setup and session management
- `models.py` - Ticket database models
- `requirements.txt` - Dependencies
- `utils/`
  - `pdf_uploader.py` - PDF processing and upload logic
  - `embeddings.py` - Embedding generation
  - `ticket_manager.py` - Ticket CRUD operations

### `user_server/`
- `main.py` - FastAPI application entry point
- `config.py` - Configuration settings
- `database.py` - Database and query logging
- `models.py` - API response models
- `requirements.txt` - Dependencies
- `utils/`
  - `embeddings.py` - Query embedding generation
  - `llm.py` - LLM integration for answer generation
  - `vector_store.py` - Pinecone vector store operations
  - `file_processor.py` - File validation and processing
  - `ticket_client.py` - Communication with staff server
  - `chunking.py` - Document chunking utilities

## Configuration

Edit the configuration files in each server directory:
- `config.py` - Server settings, database configuration, API keys
- `.env` - Environment variables (recommended for sensitive data)

## Development

### Project Conventions
- Use type hints for better IDE support and type checking
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Keep utilities modular and reusable

### Testing

Run tests for each server:
```bash
cd user_server
pytest tests/

cd ../staff_server
pytest tests/
```

## Troubleshooting

### Common Issues

1. **Database Lock Error**: Close other instances of the application using the same database
2. **Pinecone Connection Fails**: Verify your API key and internet connection
3. **PDF Processing Fails**: Ensure the PDF is valid and under the maximum file size limit
4. **Missing Dependencies**: Run `pip install -r requirements.txt` in the respective server directory

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'Add your feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue in the repository.

## Deployment

### Production Deployment

1. Use a production database (PostgreSQL recommended)
2. Set `DEBUG=False` in config
3. Use a production ASGI server (Gunicorn with Uvicorn workers)
4. Configure CORS appropriately
5. Use environment variables for all sensitive data
6. Enable HTTPS/SSL

Example production run:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
