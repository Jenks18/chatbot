# Drug-Drug Interaction Analysis System (DDI-GPT)# 🧬 ToxicoGPT - Toxicology Chatbot System



🧬 **AI-Powered Drug Interaction Analysis Platform**A self-hosted, privacy-first chatbot system specialized in toxicology research and consultation.



Self-hosted system for analyzing drug-drug interactions with comprehensive pharmacological data and safety profiles.## 🚀 Quick Start



## 🚀 Quick Start### Prerequisites

- Docker and Docker Compose

```bash- 8GB+ RAM recommended

# Setup (one command)- Port 3000, 8000, 5432, 11434 available

./setup-local.sh

### Setup

# Start backend

./start-backend.sh1. **Clone and Configure**

```bash

# Start frontend (new terminal)cd /Users/iannjenga/Desktop/chatbot

./start-frontend.shcp .env.example .env

```# Edit .env with your preferences

```

**Access:**

- Chat: http://localhost:30002. **Start All Services**

- Admin: http://localhost:3000/admin```bash

- API Docs: http://localhost:8000/docsdocker-compose up -d

```

## 🌟 Features

3. **Download AI Model** (first time only)

- ✅ Drug-drug interaction analysis```bash

- ✅ Structured data across 15+ categoriesdocker exec -it toxicology-model ollama pull llama3:8b

- ✅ Side-by-side comparison tables# Or use: mistral, meditron, or other models

- ✅ Geographic analytics dashboard```

- ✅ Self-hosted privacy-first design

- ✅ RAG support for medical literature4. **Access the Application**

- **Chat Interface**: http://localhost:3000

## 📋 Requirements- **Admin Dashboard**: http://localhost:3000/admin

- **API Docs**: http://localhost:8000/docs

- Python 3.9+- **Health Check**: http://localhost:8000/health

- Node.js 18+

- PostgreSQL 15+## 📁 Project Structure

- Ollama (for local LLM)

```

## 📚 Documentationchatbot/

├── frontend/          # Next.js chat UI

- [Architecture](./ARCHITECTURE.md) - System design├── backend/           # FastAPI server

- [Data Collection](./DATA_COLLECTION.md) - Privacy details├── data/              # Vector database & documents

- [API Reference](http://localhost:8000/docs) - API documentation├── docker-compose.yml

└── README.md

## ⚠️ Disclaimer```



**Medical Disclaimer:** For informational purposes only. Not a substitute for professional medical advice. Always consult healthcare professionals.## 🔧 Features



## 📄 License- ✅ Real-time chat interface

- ✅ Complete conversation logging

MIT License- ✅ Admin dashboard for query analytics

- ✅ Self-hosted AI model (no external APIs)
- ✅ RAG integration for domain knowledge
- ✅ PostgreSQL for persistent storage
- ✅ Docker-based deployment

## 🧪 Using the Toxicology Assistant

The chatbot is optimized for:
- Drug toxicity queries
- Chemical safety information
- Dose-response analysis
- Toxicological pathways
- Risk assessment guidance

## 📊 Admin Dashboard

View all user interactions at: http://localhost:3000/admin

Default credentials (change in .env):
- Username: `admin`
- Password: `toxgpt_admin_2025`

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📈 Scaling & Deployment

- For production, update passwords in `.env`
- Use reverse proxy (nginx) for SSL
- Consider GPU for faster model inference
- Monitor with Prometheus/Grafana

## 🔒 Security Notes

- Change default passwords before deployment
- Enable HTTPS in production
- Restrict admin dashboard access
- Regular database backups

## 📝 License

MIT License - Free for research and commercial use.
