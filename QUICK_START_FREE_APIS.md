# Quick Start: Free API Integration

## Step 1: Switch to Larger Groq Model (DO THIS FIRST!)

### Update Vercel Environment Variables:
1. Go to https://vercel.com/your-project/settings/environment-variables
2. Find `GROQ_MODEL` variable
3. **Change from**: `llama-3.1-8b-instant`
4. **Change to**: `llama-3.1-70b-versatile`
5. Click **Save**
6. **Redeploy** your project

**This gives you 128K token context window (vs 8K) - FREE!**

## Step 2: Get Optional API Keys (Higher Rate Limits)

### OpenFDA API Key (Optional - FREE):
1. Visit: https://open.fda.gov/apis/authentication/
2. Fill out registration form
3. Add to Vercel env: `OPENFDA_API_KEY=your_key_here`

### PubMed/NCBI API Key (Optional - FREE):
1. Visit: https://www.ncbi.nlm.nih.gov/account/
2. Create free NCBI account
3. Go to Settings → API Key Management
4. Generate key
5. Add to Vercel env: `NCBI_API_KEY=your_key_here`

## What We're Building

### FREE Data Sources (No API Keys Needed):
✅ **RxNorm** - Drug identifiers and basic interactions
✅ **FDA DailyMed** - Official drug labels
✅ **PubChem** - Chemical structures and toxicity
✅ **OpenFDA** - Real-world adverse events (240 req/min without key, 1000 with key)
✅ **PubMed** - Research literature (3 req/sec without key, 10 with key)
✅ **KEGG** - Metabolism pathways
✅ **ChEMBL** - Bioactivity data

### Query Flow:
```
User: "What are interactions between acetaminophen and ibuprofen?"
    ↓
1. Extract drug names: ["acetaminophen", "ibuprofen"]
2. RxNorm API → Get RxCUI identifiers
3. FDA DailyMed API → Get official labels
4. RxNorm Interactions API → Get known DDIs
5. PubChem API → Get chemical + toxicity data
6. OpenFDA API → Get adverse event statistics
7. PubMed API → Get recent studies
8. Aggregate all data → Build context (~50-100K tokens)
9. Send to Groq llama-3.1-70b-versatile (128K context window)
10. Get comprehensive, cited response!
```

## Implementation Progress

### ✅ Phase 1: Model Upgrade
- [x] Created integration plan
- [ ] Update GROQ_MODEL in Vercel
- [ ] Test with longer context

### 🔄 Phase 2: Database Schema
- [ ] Create PostgreSQL migration
- [ ] Add tables for drugs, interactions, labels
- [ ] Setup caching tables

### 🔄 Phase 3: API Services
- [ ] Build RxNorm client
- [ ] Build FDA DailyMed client  
- [ ] Build PubChem client
- [ ] Build OpenFDA client
- [ ] Build PubMed client
- [ ] Add response caching (30 days)

### 🔄 Phase 4: Integration
- [ ] Create DrugDataAggregator service
- [ ] Add drug name extraction
- [ ] Update chat router to use aggregated data
- [ ] Test end-to-end

## Benefits You'll Get

### Current System:
- Relies on model's training data (may be outdated)
- No citations to specific sources
- Limited interaction checking
- Can't access latest research

### New System (with FREE APIs):
- ✅ Real-time FDA label data
- ✅ Official drug interaction databases
- ✅ Current adverse event statistics
- ✅ Latest research from PubMed
- ✅ Chemical structure information
- ✅ Proper citations with PMIDs
- ✅ All for $0/month

## Example Improvement

**Old Response** (training data only):
> "Acetaminophen and ibuprofen can generally be taken together, but consult your doctor."

**New Response** (with FREE APIs):
> Taking acetaminophen (Tylenol) and ibuprofen (Advil) together is generally safe for short-term pain relief [1]. They work through different mechanisms - acetaminophen acts centrally while ibuprofen reduces inflammation [2].
>
> However, the FDA warns that prolonged combined use may increase risk of kidney damage and gastrointestinal bleeding [3]. OpenFDA data shows 234 reported cases of adverse events with this combination in 2024, primarily GI-related [4].
> 
> Recent studies indicate the combination is more effective than either drug alone for acute pain, but shouldn't exceed 3 days without medical supervision [5].
>
> **Safe Usage**:
> - Alternate doses: acetaminophen every 6 hours, ibuprofen every 6-8 hours
> - Don't exceed 3000mg acetaminophen or 1200mg ibuprofen daily
> - Take with food
> - Avoid if you have kidney disease or stomach ulcers
>
> ## REFERENCES
> [1] FDA DailyMed. Acetaminophen Label. SetID: abc123...
> [2] PubChem CID 1983, CID 3672. Mechanism summaries.
> [3] FDA Drug Safety Communication (2023). https://fda.gov/...
> [4] OpenFDA Adverse Events Database Query (2024). 
> [5] Smith et al. (2024). Combination analgesic therapy. PMID: 38756421

## Cost Comparison

| Approach | Monthly Cost | Data Freshness | Citations |
|----------|--------------|----------------|-----------|
| **Current (training data only)** | $0 | Static (pre-2023) | Generic |
| **New (FREE APIs)** | **$0** | **Real-time** | **Specific (PMID/FDA)** |
| DrugBank Commercial | $4,995+/year | Updated quarterly | Yes |
| UpToDate API | Custom pricing | Updated weekly | Yes |

## Next Steps

**I'm ready to build this when you say go!**

Just need you to:
1. **Update GROQ_MODEL** in Vercel to `llama-3.1-70b-versatile`
2. **Confirm your Supabase PostgreSQL** is accessible
3. **Give me the green light** to start coding!

This will transform ToxicoGPT from a smart chatbot into a **comprehensive drug information system** with real-time data - all for free!
