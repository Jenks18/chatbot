# Kandih ToxWiki - Medical Chatbot

A Next.js medical chatbot powered by Groq's Llama models with PubMed integration for accurate scientific references.

## 🚀 Features

- **3 User Modes**: Patient, Doctor, Researcher (tailored responses)
- **Real References**: PubMed API integration for verified citations
- **Admin Dashboard**: View all conversations with password protection
- **Smart Tracking**: Saves all requests including rate-limited ones
- **Chat Titles**: Auto-generated from first message

## 📦 Tech Stack

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS

**Backend:**
- Vercel Serverless Functions (Python)
- Groq API (Llama 3.3 70B)
- Instructor (structured outputs)
- PubMed API (NCBI E-utilities)

**Database:**
- Supabase (PostgreSQL)
- Tracks: conversations, sessions, failed requests

## 🛠️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/Jenks18/chatbot.git
cd chatbot
npm install
```

### 2. Environment Variables

Create `.env.local`:

```env
# Groq API
GROQ_API_KEY=your_groq_api_key

# Database (Supabase)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Admin Password (optional, default: admin123)
NEXT_PUBLIC_ADMIN_PASSWORD=your_secure_password

# PubMed API (optional, increases rate limits)
NCBI_API_KEY=your_ncbi_api_key
```

### 3. Database Setup

Run migration:

```bash
python3 migrate_add_title_and_status.py
```

### 4. Run Locally

```bash
npm run dev
```

Visit:
- Chat: `http://localhost:3000`
- Admin: `http://localhost:3000/admin` (password: `admin123`)

## 🚢 Deploy to Vercel

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

## 📁 Project Structure

```
chatbot/
├── api/                    # Vercel serverless endpoints
│   ├── chat.py            # Main chat endpoint
│   ├── admin.py           # Admin dashboard API
│   └── health.py          # Health check
├── backend/
│   ├── db/                # Database models
│   └── services/          # Groq, PubMed services
├── components/            # React components
├── pages/                 # Next.js pages
│   ├── index.tsx         # Chat interface
│   └── admin.tsx         # Admin dashboard
├── services/             # API client
└── styles/               # Global CSS
```

## 🔐 Admin Dashboard

Access: `/admin` | Password: `admin123` (default)

Change via `NEXT_PUBLIC_ADMIN_PASSWORD` environment variable.

**Features:**
- View all chat sessions with titles
- Click to see full conversation history
- Basic analytics (queries, response times)
- Rate limit tracking

## 🐛 Troubleshooting

**Rate Limit Errors:**
- Groq free tier: 30 req/min, 14,400 tokens/min
- Check usage at console.groq.com
- Consider upgrading or adding fallback

**Database Issues:**
- Verify DATABASE_URL
- Check Supabase project isn't paused
- Run migration: `python3 migrate_add_title_and_status.py`

**Admin Login:**
- Default password: `admin123`
- Set custom via NEXT_PUBLIC_ADMIN_PASSWORD
- Clear browser sessionStorage if stuck

## 📝 Documentation

- `ADMIN_AUTH_SETUP.md` - Admin authentication
- `CHAT_TITLES_AND_TRACKING.md` - Features explained
- `DEPLOYMENT.md` - Deployment guide
- `PROJECT_SUMMARY.md` - Technical details

## ⚠️ Medical Disclaimer

For **educational and research purposes only**. Not a substitute for professional medical advice.

## 📜 License

MIT License

## 📧 Contact

Ian Njenga - [GitHub](https://github.com/Jenks18)
