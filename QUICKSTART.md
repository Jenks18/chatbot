# 🚀 Quick Start Guide - ToxicoGPT

## Prerequisites
- **Docker Desktop** installed and running
- **8GB+ RAM** available
- **10GB+ disk space** for AI models

## Step 1: Initial Setup

1. **Copy environment configuration:**
```bash
cd /Users/iannjenga/Desktop/chatbot
cp .env.example .env
```

2. **Start all services:**
```bash
./start.sh
```

This will:
- Build Docker containers
- Start PostgreSQL database
- Launch backend API
- Launch frontend
- Start Ollama model server

## Step 2: Download AI Model

**Important:** The system won't work until you download an AI model.

```bash
./setup-model.sh
```

This downloads the Llama 3 8B model (~4.7GB). Choose your model:
- `llama3:8b` - Recommended, balanced performance (default)
- `mistral` - Faster, lighter weight
- `meditron` - Specialized for medical/toxicology content

To use a different model:
```bash
docker exec -it toxicology-model ollama pull mistral
```

Then update `.env`:
```
MODEL_NAME=mistral
```

## Step 3: Access the Application

Once the model is downloaded:

🌐 **Chat Interface:** http://localhost:3000
- Main toxicology chatbot interface
- Ask questions about drug toxicity, chemical safety, etc.

📊 **Admin Dashboard:** http://localhost:3000/admin
- View all chat interactions
- See analytics and statistics
- Search through conversations

📚 **API Documentation:** http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly
- View request/response schemas

## Usage Examples

Try asking ToxicoGPT:
- "What are the toxic effects of acetaminophen overdose?"
- "Explain the mechanism of lead poisoning"
- "What is the antidote for organophosphate toxicity?"
- "How does carbon monoxide cause toxicity?"
- "What are the symptoms of cyanide poisoning?"

## Managing the System

### View logs:
```bash
docker-compose logs -f
```

### View specific service logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f model_server
```

### Restart a service:
```bash
docker-compose restart backend
```

### Stop everything:
```bash
./stop.sh
```

### Stop and remove all data:
```bash
./stop.sh --clean
```

## Troubleshooting

### "Model not found" error
```bash
# Check if model is downloaded
docker exec -it toxicology-model ollama list

# Download if missing
./setup-model.sh
```

### Frontend won't load
```bash
# Wait 30 seconds for services to initialize
# Check if backend is ready
curl http://localhost:8000/health
```

### Database connection error
```bash
# Restart all services
docker-compose restart
```

### Port already in use
Edit `.env` and change:
```
BACKEND_PORT=8001  # Instead of 8000
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Next Steps

### Add Custom Toxicology Knowledge (RAG)

1. Add your documents to `data/papers/`:
```bash
# Add PDF, TXT, or MD files
cp my_toxicology_notes.txt data/papers/
```

2. Index the documents:
```bash
cd backend
python ../scripts/index_documents.py
```

3. Enable RAG in `.env`:
```
ENABLE_RAG=true
```

4. Restart backend:
```bash
docker-compose restart backend
```

### Customize the System Prompt

Edit `backend/services/model_service.py` to change the toxicology expertise focus.

### Change Model Settings

Edit `backend/services/model_service.py`:
```python
"options": {
    "temperature": 0.7,  # Lower = more focused, Higher = more creative
    "top_p": 0.9,
    "max_tokens": 1000  # Maximum response length
}
```

## Production Deployment

**Before deploying to production:**

1. **Change passwords in `.env`:**
```
POSTGRES_PASSWORD=your_secure_password_here
ADMIN_PASSWORD=your_admin_password_here
```

2. **Set up SSL/HTTPS** with nginx or Caddy

3. **Set allowed origins:**
```
CORS_ORIGINS=https://yourdomain.com
```

4. **Enable firewall rules**

5. **Set up backups:**
```bash
# Backup database
docker exec toxicology-db pg_dump -U toxgpt_user toxicology_gpt > backup.sql
```

## Getting Help

- Check logs: `docker-compose logs`
- View API docs: http://localhost:8000/docs
- Check health: http://localhost:8000/health
- See DEVELOPMENT.md for advanced configuration

---

**Enjoy using ToxicoGPT!** 🧬
