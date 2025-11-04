# Deployment Checklist - FREE API Integration

## ✅ What's Been Pushed to GitHub

1. **DrugDataAggregator Service** - Queries 6 FREE APIs
2. **APICache Model** - Caches API responses for 30 days
3. **Updated Chat Router** - Extracts drug names and builds rich context
4. **Groq Model Upgraded** - Changed to `llama-3.1-70b-versatile` (128K context)

## 🔧 What You Need to Do in Vercel

### Step 1: Add Environment Variables
Go to: https://vercel.com/[your-project]/settings/environment-variables

Add these NEW variables:

```bash
# Groq Model (upgrade from 8b to 70b for larger context)
GROQ_MODEL=llama-3.1-70b-versatile

# DeepSeek (for future use - even larger context)
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d

# OpenFDA API Key (1000 requests/min instead of 240)
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb

# PubMed/NCBI API Key (10 requests/sec instead of 3)
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209

# API Caching Settings
API_CACHE_DURATION_DAYS=30
ENABLE_API_CACHING=true
```

### Step 2: Run Database Migration

The `api_cache` table needs to be created in your Supabase database.

**Option A: Via Supabase Dashboard**
1. Go to https://supabase.com/dashboard
2. Select your project → SQL Editor
3. Run the migration file: `/backend/db/migration_add_api_cache.sql`

**Option B: Via psql**
```bash
psql $DATABASE_URL < backend/db/migration_add_api_cache.sql
```

### Step 3: Redeploy on Vercel
After adding environment variables, Vercel should auto-redeploy.
If not, trigger manual deployment.

## 🎯 What This Changes

### Before (Current Live):
- User asks: "What are interactions with acetaminophen?"
- AI responds based on training data only (may be outdated)
- Generic responses, no specific citations

### After (Once Deployed):
- User asks: "What are interactions with acetaminophen?"
- System:
  1. Extracts "acetaminophen" from query
  2. Queries RxNorm → Gets RxCUI: 161
  3. Queries FDA DailyMed → Gets official label with warnings
  4. Queries PubChem → Gets CID: 1983, molecular data, toxicity
  5. Queries RxNorm Interactions → Gets known DDIs
  6. Queries OpenFDA → Gets real adverse event statistics
  7. Queries PubMed → Gets 5 recent research papers
  8. Builds comprehensive context (~50-100K tokens)
  9. Sends to Groq llama-3.1-70b-versatile (128K context window)
- AI responds with:
  - Up-to-date FDA warnings
  - Real adverse event data
  - Recent research findings
  - Proper citations (PMIDs, FDA URLs)
  - Chemical structure info

## 📊 Example Output Improvement

**Query:** "I'm taking acetaminophen and ibuprofen. Is this safe?"

**Old Response:**
> "Generally safe but consult your doctor."

**New Response with FREE APIs:**
> Taking acetaminophen (Tylenol) and ibuprofen (Advil) together can be effective for pain relief [1], as they work through different mechanisms [2].
>
> **FDA Official Guidance:**
> The FDA label for acetaminophen warns about potential risks when combined with NSAIDs like ibuprofen, particularly regarding kidney function and gastrointestinal bleeding [3].
>
> **Real-World Data:**
> OpenFDA adverse event database shows 234 reports of adverse reactions with this combination in 2024, primarily GI-related issues [4]. Risk is higher in patients over 65 or with existing kidney/stomach problems.
>
> **Recent Research:**
> A 2024 study in JAMA found the combination provides superior pain relief compared to either drug alone, but recommends limiting use to 3 days for acute pain [5].
>
> **Safe Usage Guidelines:**
> - Alternate doses: acetaminophen every 6 hours, ibuprofen every 8 hours
> - Maximum: 3000mg acetaminophen + 1200mg ibuprofen per 24 hours
> - Take with food to protect stomach
> - Avoid if you have kidney disease or stomach ulcers
>
> ## REFERENCES
> [1] PubChem CID 1983 (Acetaminophen), CID 3672 (Ibuprofen)
> [2] FDA DailyMed. Acetaminophen Label. SetID: abc123...
> [3] FDA Drug Safety Communication. https://dailymed.nlm.nih.gov/...
> [4] OpenFDA Adverse Events Query (2024). https://open.fda.gov/...
> [5] Smith et al. (2024). Combination analgesic efficacy. JAMA. PMID: 38756421

## 🚀 Testing After Deployment

1. **Test Drug Name Extraction:**
   - Ask: "Tell me about aspirin"
   - Should fetch data from all APIs

2. **Test Multiple Drugs:**
   - Ask: "Interactions between warfarin and aspirin"
   - Should fetch data for both drugs

3. **Test Caching:**
   - Ask same question twice
   - Second response should be instant (cached)

4. **Check Admin Panel:**
   - Go to /admin
   - Verify queries are being logged
   - Check response times (should be 2-3 seconds with API calls, <500ms with cache)

## 💰 Cost Analysis

| Component | Cost | Rate Limit |
|-----------|------|------------|
| Groq llama-3.1-70b-versatile | **FREE** | 14,400 req/day |
| RxNorm API | **FREE** | Unlimited |
| FDA DailyMed | **FREE** | 240/min |
| PubChem API | **FREE** | 5/sec |
| OpenFDA (with key) | **FREE** | 1000/min |
| PubMed (with key) | **FREE** | 10/sec |
| **Total Monthly Cost** | **$0** | ✅ |

With 30-day caching, you'll rarely hit rate limits!

## 📝 Notes

- The data aggregator runs asynchronously (all APIs called in parallel)
- Failed API calls don't break the system (graceful fallback)
- Cache expires after 30 days (configurable via `API_CACHE_DURATION_DAYS`)
- Drug name extraction is simple (can be enhanced with NER model later)
- All citations include proper URLs to source data

## ⚠️ Important

Make sure to add the **Vercel environment variables** before the deployment finishes, or redeploy after adding them!

Ready to transform ToxicoGPT into a comprehensive drug information system! 🚀
