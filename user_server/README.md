# User Server

The User Server provides both a web interface and API for users to ask questions and get answers from the RAG (Retrieval-Augmented Generation) system.

## Features

- **Web Interface**: User-friendly frontend for asking questions
- **File Upload**: Support for PDF file uploads for context
- **RAG System**: Retrieves relevant information from knowledge base
- **Ticket Creation**: Automatically creates support tickets when answers aren't found
- **API Endpoints**: RESTful API for programmatic access

## Running the Server

```bash
# From the project root
source venv/bin/activate
cd user_server
python main.py
```

The server will start on `http://localhost:8000`

## Web Interface

Visit `http://localhost:8000` in your browser to access the web interface.

### Features:
- Ask questions in natural language
- Upload PDF files for additional context
- Get instant answers or support ticket creation
- View sources and relevance scores

## API Endpoints

### Health Check
```
GET /health
```
Returns server health status.

### Ask Question
```
POST /ask
Content-Type: multipart/form-data

Form fields:
- query: The user's question (required)
- file: PDF file (optional)
```

Returns:
- `status: "success"` - Answer found with sources
- `status: "ticket_created"` - No answer found, ticket created

## Example API Usage

```python
import requests

# Ask a question
response = requests.post('http://localhost:8000/ask',
    data={'query': 'How do I reset my password?'}
)

print(response.json())
```

## Configuration

Configure the server through environment variables:
- `GEMINI_API_KEY`: Google Gemini API key
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `PINECONE_INDEX_NAME`: Pinecone index name
- `STAFF_SERVER_URL`: URL of the staff server (default: http://localhost:8001)

## Dependencies

Install requirements:
```bash
pip install -r requirements.txt
```