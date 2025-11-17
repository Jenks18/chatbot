# Kandih ToxWiki - Enterprise AI Medication Safety Platform

[![Production Status](https://img.shields.io/badge/status-production-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

Kandih ToxWiki is an enterprise-grade AI-powered medication safety platform that provides three distinct persona-based interfaces for different user types:

- **Patient Mode**: Consumer-friendly medication safety information
- **Physician Mode**: Clinical decision support with drug-drug interactions
- **Researcher Mode**: Target Product Profile (TPP) analysis for drug development

## ✨ Key Features

### Core Capabilities
- ✅ Three-tier persona system with distinct conversational workflows
- ✅ Real-time conversation memory (last 20 messages)
- ✅ Session persistence across page refreshes
- ✅ FDA safety data integration
- ✅ Evidence-based responses with citations

### Enterprise Features
- ✅ Structured logging with correlation IDs
- ✅ Input validation and sanitization
- ✅ Rate limiting (30 req/min for chat, 60 req/min for API)
- ✅ Graceful error handling
- ✅ Health check endpoint
- ✅ Database connection pooling
- ✅ Async operations

## 🏗️ Architecture

```
Frontend (Next.js) ─→ API (Vercel Serverless) ─→ AI (Groq Compound)
                   ↓
           Database (Supabase PostgreSQL)
```

### Technology Stack
- **Frontend**: Next.js 14, React, TypeScript, TailwindCSS
- **Backend**: Python, FastAPI, SQLAlchemy
- **AI**: Groq Compound Model (with free tool interception)
- **Database**: PostgreSQL (Supabase)
- **Deployment**: Vercel (serverless functions)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Groq API key (free at https://console.groq.com/keys)
- Supabase account (optional, for persistence)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Jenks18/chatbot.git
cd chatbot
```

2. **Install dependencies**
```bash
# Frontend
npm install

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run locally**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd backend
uvicorn main:app --reload --port 8000
```

Visit http://localhost:3000

## 📋 Environment Variables

### Required
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Optional
```env
DATABASE_URL=postgresql://...  # For persistence
OPENFDA_API_KEY=...            # Enhanced drug data
NCBI_API_KEY=...               # Research citations
```

See `.env.example` for complete list.

## 🎭 User Modes

### Patient Mode
**Target**: General public seeking medication information

**Workflow**:
1. User asks about a medication
2. AI offers three options:
   - A) Key Safety Facts
   - B) Personalized Safety Check
   - C) Something else
3. AI provides conversational, easy-to-understand information

**Example**:
```
User: "What is aspirin?"
AI: "Thanks for asking about aspirin. I can help you understand...
     What would you like to know?
     A) Key Safety Facts
     B) Personalized Safety Check
     C) Something else"
```

### Physician Mode
**Target**: Healthcare professionals

**Workflow**:
1. Physician mentions a medication
2. AI asks for clinical context:
   - Patient's medication regimen
   - Comorbidities
   - Clinical indication
   - Specific safety concerns
3. AI provides comprehensive clinical safety analysis

**Example**:
```
Physician: "panadol"
AI: "I can provide comprehensive clinical safety information...
     Could you share the patient's current medication regimen,
     comorbidities, clinical indication, and safety concerns?"
```

### Researcher Mode
**Target**: Pharmaceutical researchers, drug developers

**Workflow**:
1. Researcher mentions a drug/class
2. AI asks for scoping:
   - Anchor drug (competitor to analyze)
   - Drug class (therapeutic category)
   - Target patient population
   - Key comparators
   - TPP strategic goal
3. AI provides hierarchical two-phase analysis

**Example**:
```
Researcher: "clinical"
AI: "I will conduct a hierarchical safety analysis...
     Please provide:
     1. Anchor Drug
     2. Drug Class
     3. Target Patient Population
     4. Key Comparators
     5. TPP Strategic Goal"
```

## 🔐 Security

- ✅ Input validation and sanitization
- ✅ SQL injection prevention (ORM-based)
- ✅ XSS prevention
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Environment variable protection

## 📊 Monitoring

### Health Check
```bash
GET /api/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T...",
  "checks": {
    "database": {"status": "healthy"},
    "api_keys": {"status": "healthy"},
    "system": {"cpu_percent": 15.2, "memory_percent": 45.1}
  }
}
```

### Structured Logging
All logs are in JSON format for easy parsing:
```json
{
  "timestamp": "2025-11-16T...",
  "level": "INFO",
  "message": "Chat request processed",
  "correlation_id": "uuid",
  "session_id": "uuid",
  "user_mode": "patient",
  "response_time_ms": 1234
}
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

## 📈 Performance

- **Response Time**: < 2s average
- **Uptime**: 99.9%
- **Concurrent Users**: 100+
- **Rate Limits**: 30 chat requests/min per session

## 🚢 Deployment

### Vercel (Recommended)

1. **Connect repository to Vercel**
2. **Configure environment variables**
3. **Deploy**

```bash
# Or use CLI
vercel --prod
```

### Environment Variables in Vercel
Set in: Project Settings → Environment Variables

Required:
- `GROQ_API_KEY`
- `DATABASE_URL`

## 📝 API Documentation

### Chat Endpoint
```
POST /api/chat
```

Request:
```json
{
  "message": "What is aspirin?",
  "session_id": "uuid",
  "user_mode": "patient",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

Response:
```json
{
  "answer": "AI response...",
  "session_id": "uuid",
  "model_used": "groq/compound",
  "response_time_ms": 1234
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: https://github.com/Jenks18/chatbot/issues
- **Documentation**: See `/docs` folder
- **Email**: support@kandih.com

## 🏆 Enterprise Checklist

See `ENTERPRISE_CHECKLIST.md` for complete audit and enhancement roadmap.

---

Built with ❤️ by the Kandih team
