# Microservice: PDF Summarizer for Multi-Tenant

## Overview
A FastAPI microservice that accepts PDF uploads per tenant, summarizes content using AI, and stores results in a tenant-specific MongoDB database. Master tenant registry stored in PostgreSQL.

## Features
- **REST endpoint:** `/upload` (POST, multipart)
- **Multi-tenancy:** Each tenant gets its own MongoDB database
- **AI Summarization:** Uses HuggingFace distilbart-cnn-12-6 model
- **Dockerized:** All dependencies (Python, PostgreSQL, MongoDB) run in containers

## Quick Start

1. **Clone repo and setup directories**
   ```bash
   mkdir -p data/uploads
   ```

2. **Build & run services**
   ```bash
   docker-compose up --build
   ```

3. **API Usage**
   - `POST /upload`
   - Form fields: `tenantName` (string), `file` (PDF file)
   - Example via `curl`:
     ```bash
     curl -F tenantName=acme -F file=@sample.pdf http://localhost:8000/upload
     ```

## Notes
- PDF files stored at `/data/uploads`
- You can extend file storage to S3, GCS, etc.
- Each tenant gets a separate MongoDB DB for summaries & extracted text

## Extending
- Add authentication
- Add UI
- Use other AI models
