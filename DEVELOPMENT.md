# ToxicoGPT Development Guide

## Local Development (Without Docker)

### Backend Development

1. **Set up Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up PostgreSQL:**
```bash
# Using Homebrew on macOS
brew install postgresql
brew services start postgresql

# Create database
createdb toxicology_gpt
psql toxicology_gpt < db/init.sql
```

3. **Configure environment:**
```bash
cp ../.env.example ../.env
# Edit .env with local database credentials
```

4. **Run backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run development server:**
```bash
npm run dev
```

3. **Access at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

### Model Server Setup (Local)

**Option 1: Ollama (macOS/Linux)**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Download model
ollama pull llama3:8b
```

**Option 2: Docker (All platforms)**
```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3:8b
```

## Adding Custom Toxicology Documents (RAG)

1. **Add documents to data folder:**
```bash
mkdir -p data/papers
# Add PDF, TXT, or MD files to this folder
```

2. **Create indexing script:**
```python
# scripts/index_documents.py
from langchain.document_loaders import DirectoryLoader, TextLoader
from backend.services.rag_service import rag_service

# Load documents
loader = DirectoryLoader('data/papers', glob="**/*.txt")
documents = loader.load()

# Extract text
texts = [doc.page_content for doc in documents]
metadatas = [{"source": doc.metadata["source"]} for doc in documents]

# Index documents
rag_service.add_documents(texts, metadatas)
print(f"Indexed {len(texts)} documents")
```

3. **Run indexing:**
```bash
cd backend
python ../scripts/index_documents.py
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
Use the Swagger UI at http://localhost:8000/docs

## Deployment

### Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set `CORS_ORIGINS` to your domain
- [ ] Enable HTTPS with reverse proxy (nginx/Caddy)
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Monitor with Prometheus/Grafana
- [ ] Set up log rotation

### Deploy to Cloud

**AWS EC2:**
```bash
# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Clone repo
git clone <your-repo>
cd chatbot

# Start services
./start.sh
```

**DigitalOcean/Linode:**
Similar process, use Docker Machine or manual setup

### Using Different Models

Edit `.env`:
```bash
# For medical/toxicology specialization
MODEL_NAME=meditron

# For faster responses
MODEL_NAME=mistral

# For better accuracy
MODEL_NAME=llama3:70b  # Requires more RAM/GPU
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database not ready: wait 30 seconds and retry
# - Port conflict: change BACKEND_PORT in .env
```

### Model server errors
```bash
# Check model is downloaded
docker exec -it toxicology-model ollama list

# Redownload if needed
docker exec -it toxicology-model ollama pull llama3:8b
```

### Frontend build errors
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

### Database connection issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose up -d backend
```

## Performance Optimization

### For faster model inference:
1. Use GPU (NVIDIA only):
   ```yaml
   # docker-compose.yml - add to model_server service
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

2. Use smaller models (mistral, llama3:8b)
3. Adjust model parameters in `backend/services/model_service.py`

### For database performance:
- Add indexes to frequently queried columns
- Use connection pooling
- Regular VACUUM operations

## Monitoring

### Health checks:
```bash
curl http://localhost:8000/health
```

### Database stats:
```sql
-- Connect to database
psql toxicology_gpt

-- View query counts
SELECT COUNT(*) FROM chat_logs;
SELECT COUNT(DISTINCT session_id) FROM chat_logs;
```

### Docker stats:
```bash
docker stats
```
