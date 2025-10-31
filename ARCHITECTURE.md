# ToxicoGPT Application Architecture

**Version:** 1.0  
**Date:** October 27, 2025  
**Stack:** FastAPI + Next.js + PostgreSQL + Ollama

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Directory Structure](#directory-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Schema](#database-schema)
7. [Data Flow](#data-flow)
8. [API Endpoints](#api-endpoints)
9. [Key Features](#key-features)
10. [Current Weaknesses & Improvement Opportunities](#current-weaknesses--improvement-opportunities)

---

## System Overview

ToxicoGPT is a self-hosted, production-ready AI chatbot system specialized in toxicology and life sciences. It combines a Python FastAPI backend with a Next.js React frontend, using local LLM inference via Ollama and PostgreSQL for data persistence.

### Tech Stack:
- **Backend:** Python 3.9, FastAPI, SQLAlchemy, Pydantic
- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database:** PostgreSQL 15
- **AI/ML:** Ollama (llama3.2:3b), ChromaDB (vector store), LangChain
- **Deployment:** Local development (non-Docker)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Chat UI     │  │  Admin       │  │  Mobile      │         │
│  │  (React)     │  │  Dashboard   │  │  Browser     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    HTTP/REST API (Port 3000)
                             │
┌─────────────────────────────┼─────────────────────────────────┐
│                    FRONTEND (Next.js)                          │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Services → Components → Pages                         │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                     REST API (Port 8000)
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                    BACKEND (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Routers → Services → Database                         │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────┼─────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌──────────────────┐          ┌──────────────────┐
    │   PostgreSQL     │          │   Ollama Server  │
    │   (Port 5432)    │          │   (Port 11434)   │
    └──────────────────┘          └──────────────────┘
```

---

## Directory Structure

```
chatbot/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # App entry point
│   ├── requirements.txt        # Dependencies
│   ├── db/                     # Database layer
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── models.py           # ORM models
│   │   └── init.sql            # Schema
│   ├── routers/                # API endpoints
│   │   ├── chat.py             
│   │   ├── admin.py            
│   │   └── health.py           
│   ├── services/               # Business logic
│   │   ├── model_service.py    # Ollama integration
│   │   ├── rag_service.py      # Vector search
│   │   ├── log_service.py      # DB operations
│   │   └── geo_service.py      # IP geolocation
│   └── schemas.py              # Pydantic models
│
├── frontend/                   # Next.js Frontend
│   ├── pages/                  # Routes
│   │   ├── index.tsx           # Chat UI
│   │   └── admin.tsx           # Dashboard
│   ├── components/             # React components
│   └── services/               
│       └── api.ts              # API client
│
├── data/                       # Data directory
│   ├── papers/                 # PDFs for RAG
│   └── vectorstore/            # ChromaDB
│
├── setup-local.sh              # Setup script
├── start-backend.sh            # Backend launcher
└── start-frontend.sh           # Frontend launcher
```

---

## Backend Architecture

### Key Services:

**model_service.py** - AI Integration
- Connects to Ollama (llama3.2:3b)
- Enhanced toxicology system prompt
- Handles streaming/complete responses

**geo_service.py** - IP Geolocation
- Real-time IP→location lookup (ip-api.com)
- Returns country, city, region, timezone, ISP
- Handles private IPs gracefully

**rag_service.py** - Document Retrieval
- Loads PDFs, creates embeddings
- Stores in ChromaDB vector database
- Retrieves context for queries

**log_service.py** - Database Operations
- Logs every chat interaction
- Tracks sessions with geo data
- Search and analytics queries

---

## Frontend Architecture

**Pages:**
- `index.tsx` - Main chat interface
- `admin.tsx` - Analytics dashboard with geolocation data

**Components:**
- `ChatInterface.tsx` - Message list, input, session mgmt
- `MessageBubble.tsx` - Individual messages
- `SessionList.tsx` - Conversation history

**Services:**
- `api.ts` - Axios-based API client for all backend calls

---

## Database Schema

**chat_logs table:**
- Stores every question/answer
- Includes IP address, user agent, geolocation
- Response times, model used
- JSON metadata (RAG usage, geo data)

**sessions table:**
- Tracks unique user sessions
- Country, city, region, timezone
- Latitude/longitude coordinates
- ISP information

**analytics_with_location view:**
- Joins chat_logs + sessions
- Used for admin dashboard queries

---

## Data Flow

1. User asks question → Frontend
2. Frontend POST to `/api/chat` → Backend
3. Backend extracts IP, looks up geolocation
4. Updates session with geo data
5. (Optional) RAG retrieves relevant documents
6. Sends prompt to Ollama model
7. Logs interaction to PostgreSQL
8. Returns response to frontend
9. Frontend displays answer

Admin dashboard queries database for analytics and displays geolocation data.

---

## API Endpoints

**Chat:**
- `POST /api/chat` - Send message, get AI response
- `GET /api/history/{session_id}` - Get conversation

**Admin:**
- `GET /api/logs/recent?hours=24` - Recent queries
- `GET /api/stats/overview` - Dashboard statistics
- `GET /api/logs/search?q=query` - Search logs

**System:**
- `GET /health` - Health check (DB, Model, Vectorstore)
- `GET /docs` - Auto-generated API documentation

---

## Key Features

✅ **Implemented:**
- Real-time chat with AI (toxicology expert)
- Admin analytics dashboard
- Geographic tracking (IP→location)
- Session management
- RAG document retrieval (optional)
- Comprehensive logging (IP, geo, timestamps)
- Response time tracking
- Search functionality
- Daily usage charts

---

## Current Weaknesses & Improvement Opportunities

### 🔴 CRITICAL SECURITY ISSUES

**1. No Authentication**
- Admin dashboard publicly accessible
- No user login
- No API keys
- **Fix:** Implement JWT auth, protect routes

**2. No HTTPS**
- Running on HTTP
- Data sent in plain text
- **Fix:** Add SSL certificates, nginx reverse proxy

**3. Hardcoded DB Credentials**
- Passwords in scripts
- No encryption at rest
- **Fix:** Environment variables, secrets management

**4. No Request Protection**
- No rate limiting
- No CORS validation
- Vulnerable to abuse
- **Fix:** Rate limiting middleware, API keys

### 🟡 PERFORMANCE ISSUES

**5. No Caching**
- Every request hits database + model
- Slow dashboard loads
- **Fix:** Redis cache layer

**6. Synchronous Operations**
- Geolocation blocks requests
- No background jobs
- **Fix:** Celery task queue, async geo lookups

**7. Database Scaling**
- No connection pooling optimization
- No partitioning
- Full table scans
- **Fix:** Better indexing, table partitioning, read replicas

**8. Model Bottleneck**
- Single Ollama instance
- CPU-bound inference
- Can't handle concurrent users
- **Fix:** GPU acceleration, multiple instances, load balancing

### 🟠 FEATURE GAPS

**9. No User Accounts**
- Can't track individual users
- No personalization
- **Fix:** User registration/login system

**10. Limited RAG**
- No source attribution
- No document management UI
- **Fix:** Citations in answers, upload interface

**11. No Conversation Export**
- Can't save/share chats
- **Fix:** PDF/JSON export, email transcripts

**12. No Feedback System**
- Can't rate responses
- No improvement loop
- **Fix:** Thumbs up/down, ratings database

### 🟢 CODE QUALITY

**13. No Tests**
- Zero unit/integration tests
- Manual testing only
- **Fix:** pytest suite, 80% coverage target

**14. Poor Logging**
- Console.log only
- No log levels
- Hard to debug
- **Fix:** Structured logging, ELK stack, Sentry

**15. Hardcoded Config**
- URLs/ports in code
- Not environment-agnostic
- **Fix:** config.py with Pydantic settings

**16. No API Versioning**
- Breaking changes affect all clients
- **Fix:** /api/v1, /api/v2 paths

### 🔵 SCALABILITY

**17. Single Server**
- No horizontal scaling
- Single point of failure
- **Fix:** Docker + Kubernetes, load balancer

**18. No Request Queue**
- Model can be overwhelmed
- **Fix:** Celery + Redis/RabbitMQ

**19. Database Connections**
- Not optimized
- Can run out under load
- **Fix:** PgBouncer, connection pooling

### 🟣 USER EXPERIENCE

**20. No Mobile App**
- Web only
- No offline support
- **Fix:** PWA or React Native

**21. Poor Accessibility**
- Not WCAG compliant
- No screen reader support
- **Fix:** Semantic HTML, ARIA labels

**22. English Only**
- No i18n
- **Fix:** next-i18next, translation files

---

## Recommended Priority Order

### **Phase 1: Security (CRITICAL - Week 1-2)**
1. Add JWT authentication
2. Implement HTTPS/SSL
3. Environment variable config
4. Rate limiting
5. Database encryption

### **Phase 2: Performance (Week 3-4)**
6. Redis caching
7. Celery task queue
8. Database indexing
9. Async geolocation
10. Connection pooling

### **Phase 3: Reliability (Week 5-6)**
11. Structured logging
12. Error tracking (Sentry)
13. Health checks + auto-recovery
14. Automated backups
15. Uptime monitoring

### **Phase 4: Features (Week 7-8)**
16. User accounts
17. Conversation export
18. Feedback mechanism
19. Enhanced RAG
20. Mobile improvements

### **Phase 5: Testing (Week 9-10)**
21. Unit tests (80% coverage)
22. Integration tests
23. E2E tests
24. CI/CD pipeline
25. Load testing

---

## Discussion Questions

**Architecture:**
1. Monolith vs Microservices?
2. Stay with Ollama or use cloud APIs (OpenAI, Anthropic)?
3. SQL vs NoSQL for logs?

**Features:**
4. What's the most important missing feature?
5. Privacy vs Analytics - how much tracking?
6. Target users - medical professionals or general public?

**Business:**
7. Open source or proprietary?
8. Self-hosted only or SaaS offering?
9. Compliance requirements (GDPR, HIPAA)?

---

Ready to discuss and make the system more robust! What should we tackle first?
