# Data Source Integration Plan - FREE APIs Only

## Overview
Build a comprehensive drug interaction database using FREE public APIs (no DrugBank), and use Groq's larger model for processing.

## AI Model: **Groq llama-3.1-70b-versatile** (FREE!)

### Why This Model?
- **Context Window**: 128K tokens (16x larger than the 8b instant model!)
- **Cost**: FREE (Groq's free tier)
- **Speed**: Extremely fast inference
- **Already configured**: We just need to change the model name in `.env`

### Current vs New Model
```bash
# Current (in .env)
GROQ_MODEL=llama-3.1-8b-instant

# Change to (in .env)
GROQ_MODEL=llama-3.1-70b-versatile
```

This gives us 128K context window with no cost!

## Primary Data Sources to Integrate (ALL FREE - NO DrugBank!)

### 1. **RxNorm** (NLM - National Library of Medicine) [FREE API]
- **URL**: https://rxnav.nlm.nih.gov/
- **API Docs**: https://lhncbc.nlm.nih.gov/RxNav/APIs/
- **Access**: FREE, no API key required
- **Contains**:
  - Normalized drug names
  - Drug relationships (brand → generic)
  - RxCUI (standard drug identifiers)
  - Drug classes and categories

**Example API Call**:
```bash
# Get drug info
https://rxnav.nlm.nih.gov/REST/rxcui.json?name=acetaminophen

# Get drug interactions
https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui=161
```

### 2. **FDA DailyMed** (Official Drug Labels) [FREE API]
- **URL**: https://dailymed.nlm.nih.gov/dailymed/
- **API**: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
- **Access**: FREE, no authentication
- **Contains**:
  - Complete FDA-approved drug labels (SPL XML format)
  - Indications, contraindications
  - Warnings and precautions
  - Drug interactions section
  - Adverse reactions
  - Dosing and administration
  - Pharmacokinetics
  - Mechanism of action

**Example API Call**:
```bash
# Search for drug
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=acetaminophen

# Get full label
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml
```

### 3. **PubChem** (NIH Chemical Database) [FREE API]
- **URL**: https://pubchem.ncbi.nlm.nih.gov/
- **API Docs**: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest
- **Access**: FREE REST API
- **Contains**:
  - Chemical structures (SMILES, InChI, molecular formula)
  - Molecular weight, properties
  - Toxicity data (LD50, safety info)
  - Bioassay results
  - Drug-target information
  - Literature references (PubMed links)
  - Pharmacology summaries

**Example API Call**:
```bash
# Get compound by name
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/acetaminophen/JSON

# Get toxicity data
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/acetaminophen/xrefs/RegistryID/JSON
```

### 4. **OpenFDA** (FDA Adverse Events) [FREE API]
- **URL**: https://open.fda.gov/
- **API Docs**: https://open.fda.gov/apis/
- **Access**: FREE, optional API key (increases rate limits)
- **Contains**:
  - Drug adverse event reports (FAERS database)
  - Drug labels (structured)
  - Drug recall information
  - Real-world safety data

**Example API Call**:
```bash
# Get adverse events for a drug
https://api.fda.gov/drug/event.json?search=patient.drug.openfda.generic_name:"acetaminophen"&count=patient.reaction.reactionmeddrapt.exact
```

### 5. **PubMed Central** (Research Literature) [FREE API]
- **URL**: https://pubmed.ncbi.nlm.nih.gov/
- **API**: E-utilities (https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- **Access**: FREE (API key optional for higher limits)
- **Contains**:
  - Published research papers
  - Clinical trials
  - Drug interaction studies
  - Pharmacokinetic studies
  - Toxicology reports

**Example API Call**:
```bash
# Search for drug interaction studies
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=acetaminophen+AND+drug+interactions&retmode=json

# Get article details
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12345678&retmode=xml
```

### 6. **KEGG DRUG** (Metabolism Pathways) [FREE]
- **URL**: https://www.genome.jp/kegg/drug/
- **API**: https://rest.kegg.jp/
- **Access**: FREE
- **Contains**:
  - Drug metabolism pathways
  - CYP450 enzyme interactions
  - Drug-enzyme relationships
  - Disease associations

**Example API Call**:
```bash
# Get drug entry
https://rest.kegg.jp/get/dr:D00217

# Find pathway
https://rest.kegg.jp/link/pathway/dr:D00217
```

### 7. **UniProt** (Protein/Target Data) [FREE API]
- **URL**: https://www.uniprot.org/
- **API**: https://www.uniprot.org/help/api
- **Access**: FREE
- **Contains**:
  - Drug target proteins
  - Enzyme information (CYP450 family)
  - Transporter proteins
  - Receptor information

**Example API Call**:
```bash
# Get protein data
https://rest.uniprot.org/uniprotkb/P10635.json
```

### 8. **ChEMBL** (Bioactivity Database) [FREE API]
- **URL**: https://www.ebi.ac.uk/chembl/
- **API**: https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
- **Access**: FREE
- **Contains**:
  - Drug-target binding data
  - IC50, Ki, EC50 values
  - ADME properties
  - Toxicity endpoints

**Example API Call**:
```bash
# Search for compound
https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL112.json

# Get bioactivity data
https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL112
```

## Architecture: How to Store and Query (PostgreSQL + Caching)

### Storage Strategy - PostgreSQL Database

```sql
-- RxNorm drug names and identifiers
CREATE TABLE rxnorm_drugs (
    rxcui VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    synonyms TEXT[],
    drug_class VARCHAR(255),
    tty VARCHAR(10),  -- Term type (e.g., SBD, GPCK, IN)
    last_updated TIMESTAMP DEFAULT NOW()
);

-- FDA DailyMed labels (cached)
CREATE TABLE fda_labels (
    set_id VARCHAR(50) PRIMARY KEY,
    spl_id VARCHAR(50),
    drug_name VARCHAR(255),
    generic_name VARCHAR(255),
    manufacturer VARCHAR(255),
    indications TEXT,
    contraindications TEXT,
    warnings TEXT,
    adverse_reactions TEXT,
    drug_interactions TEXT,
    dosage TEXT,
    pharmacokinetics TEXT,
    mechanism_of_action TEXT,
    label_xml TEXT,  -- Full XML for detailed parsing
    last_updated TIMESTAMP DEFAULT NOW()
);

-- PubChem chemical data (cached)
CREATE TABLE pubchem_compounds (
    cid BIGINT PRIMARY KEY,
    iupac_name TEXT,
    molecular_formula VARCHAR(255),
    molecular_weight FLOAT,
    canonical_smiles TEXT,
    inchi TEXT,
    inchi_key VARCHAR(27),
    synonyms TEXT[],
    properties JSONB,  -- logP, tpsa, complexity, etc.
    toxicity_data JSONB,  -- LD50, safety summaries
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Drug-drug interactions (aggregated from RxNorm + FDA + Literature)
CREATE TABLE drug_interactions (
    id SERIAL PRIMARY KEY,
    drug_a_rxcui VARCHAR(20),
    drug_b_rxcui VARCHAR(20),
    drug_a_name VARCHAR(255),
    drug_b_name VARCHAR(255),
    description TEXT,
    severity VARCHAR(50),  -- major, moderate, minor, unknown
    mechanism TEXT,
    clinical_effects TEXT,
    management TEXT,
    source VARCHAR(100),  -- rxnorm, fda, pubmed
    source_url TEXT,
    confidence_score FLOAT,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(drug_a_rxcui, drug_b_rxcui, source)
);

-- PubMed literature (cached search results)
CREATE TABLE pubmed_articles (
    pmid BIGINT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    authors TEXT[],
    journal VARCHAR(500),
    publication_date DATE,
    doi VARCHAR(255),
    keywords TEXT[],
    mesh_terms TEXT[],
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Link drugs to literature
CREATE TABLE drug_literature_links (
    id SERIAL PRIMARY KEY,
    rxcui VARCHAR(20),
    pmid BIGINT,
    relevance_score FLOAT,
    context VARCHAR(50),  -- interaction, toxicity, pharmacokinetics, etc.
    FOREIGN KEY (pmid) REFERENCES pubmed_articles(pmid)
);

-- KEGG pathways (cached)
CREATE TABLE kegg_pathways (
    pathway_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    pathway_data JSONB,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Drug-pathway relationships
CREATE TABLE drug_pathways (
    id SERIAL PRIMARY KEY,
    rxcui VARCHAR(20),
    pathway_id VARCHAR(20),
    role VARCHAR(100),  -- substrate, inhibitor, inducer
    enzyme VARCHAR(50),  -- CYP3A4, CYP2D6, etc.
    FOREIGN KEY (pathway_id) REFERENCES kegg_pathways(pathway_id)
);

-- OpenFDA adverse events (aggregated)
CREATE TABLE adverse_events (
    id SERIAL PRIMARY KEY,
    rxcui VARCHAR(20),
    drug_name VARCHAR(255),
    reaction VARCHAR(500),
    reaction_count INT,
    serious BOOLEAN,
    report_count INT,
    data_source VARCHAR(50) DEFAULT 'openfda',
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Cache for API responses (prevent redundant calls)
CREATE TABLE api_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    api_source VARCHAR(50),
    response_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_rxnorm_name ON rxnorm_drugs(name);
CREATE INDEX idx_fda_drug_name ON fda_labels(drug_name);
CREATE INDEX idx_fda_generic_name ON fda_labels(generic_name);
CREATE INDEX idx_pubchem_synonyms ON pubchem_compounds USING GIN(synonyms);
CREATE INDEX idx_interactions_drugs ON drug_interactions(drug_a_rxcui, drug_b_rxcui);
CREATE INDEX idx_literature_rxcui ON drug_literature_links(rxcui);
CREATE INDEX idx_adverse_events_drug ON adverse_events(rxcui);
```

### Query Strategy (Python Implementation)

```python
# backend/services/data_aggregator_service.py

import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class DrugDataAggregator:
    """Aggregates drug data from multiple FREE APIs"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.cache_duration = timedelta(days=30)  # Cache API responses for 30 days
    
    async def get_comprehensive_drug_data(self, drug_name: str) -> Dict:
        """
        Get complete drug data by querying multiple APIs in parallel
        """
        # Run all API calls concurrently
        results = await asyncio.gather(
            self.get_rxnorm_data(drug_name),
            self.get_fda_label(drug_name),
            self.get_pubchem_data(drug_name),
            self.get_drug_interactions(drug_name),
            self.get_adverse_events(drug_name),
            self.get_kegg_pathways(drug_name),
            self.get_pubmed_studies(drug_name),
            return_exceptions=True
        )
        
        rxnorm, fda, pubchem, interactions, adverse_events, pathways, literature = results
        
        return {
            "drug_name": drug_name,
            "identifiers": rxnorm,
            "fda_label": fda,
            "chemical_data": pubchem,
            "interactions": interactions,
            "adverse_events": adverse_events,
            "metabolism": pathways,
            "literature": literature,
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_rxnorm_data(self, drug_name: str) -> Dict:
        """Query RxNorm API for drug identifiers"""
        cache_key = f"rxnorm_{drug_name}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            # Get RxCUI
            response = await client.get(
                f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
            )
            data = response.json()
            
            if data.get("idGroup", {}).get("rxnormId"):
                rxcui = data["idGroup"]["rxnormId"][0]
                
                # Get drug properties
                props_response = await client.get(
                    f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json"
                )
                props = props_response.json()
                
                result = {
                    "rxcui": rxcui,
                    "name": props.get("properties", {}).get("name"),
                    "synonyms": props.get("properties", {}).get("synonym", "").split(", "),
                    "tty": props.get("properties", {}).get("tty")
                }
                
                self._save_to_cache(cache_key, result)
                return result
        
        return {}
    
    async def get_fda_label(self, drug_name: str) -> Dict:
        """Query FDA DailyMed for official drug label"""
        cache_key = f"fda_{drug_name}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            # Search for drug
            response = await client.get(
                f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
            )
            data = response.json()
            
            if data.get("data") and len(data["data"]) > 0:
                setid = data["data"][0]["setid"]
                
                # Get full label (XML)
                label_response = await client.get(
                    f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"
                )
                
                # Parse XML for key sections (simplified - would use proper XML parser)
                result = {
                    "setid": setid,
                    "title": data["data"][0].get("title"),
                    "manufacturer": data["data"][0].get("author"),
                    "label_xml": label_response.text,
                    # Would extract: indications, contraindications, interactions, etc.
                }
                
                self._save_to_cache(cache_key, result)
                return result
        
        return {}
    
    async def get_pubchem_data(self, drug_name: str) -> Dict:
        """Query PubChem for chemical and toxicity data"""
        cache_key = f"pubchem_{drug_name}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            # Get compound CID
            response = await client.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
            )
            data = response.json()
            
            if data.get("IdentifierList", {}).get("CID"):
                cid = data["IdentifierList"]["CID"][0]
                
                # Get properties
                props_response = await client.get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChI,InChIKey/JSON"
                )
                props = props_response.json()["PropertyTable"]["Properties"][0]
                
                # Get toxicity data
                tox_response = await client.get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
                )
                tox_data = tox_response.json()
                
                result = {
                    "cid": cid,
                    "molecular_formula": props.get("MolecularFormula"),
                    "molecular_weight": props.get("MolecularWeight"),
                    "smiles": props.get("CanonicalSMILES"),
                    "inchi": props.get("InChI"),
                    "inchi_key": props.get("InChIKey"),
                    "toxicity": self._extract_toxicity(tox_data)
                }
                
                self._save_to_cache(cache_key, result)
                return result
        
        return {}
    
    async def get_drug_interactions(self, drug_name: str) -> List[Dict]:
        """Query RxNorm interaction API"""
        rxnorm_data = await self.get_rxnorm_data(drug_name)
        if not rxnorm_data.get("rxcui"):
            return []
        
        rxcui = rxnorm_data["rxcui"]
        cache_key = f"interactions_{rxcui}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}"
            )
            data = response.json()
            
            interactions = []
            if data.get("interactionTypeGroup"):
                for group in data["interactionTypeGroup"]:
                    for interaction in group.get("interactionType", []):
                        for pair in interaction.get("interactionPair", []):
                            interactions.append({
                                "drug": pair["interactionConcept"][1]["minConceptItem"]["name"],
                                "description": pair.get("description"),
                                "severity": pair.get("severity", "unknown")
                            })
            
            self._save_to_cache(cache_key, interactions)
            return interactions
    
    async def get_adverse_events(self, drug_name: str) -> List[Dict]:
        """Query OpenFDA for adverse event data"""
        cache_key = f"adverse_{drug_name}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.fda.gov/drug/event.json?search=patient.drug.openfda.generic_name:\"{drug_name}\"&count=patient.reaction.reactionmeddrapt.exact&limit=20"
            )
            data = response.json()
            
            events = []
            if data.get("results"):
                for result in data["results"]:
                    events.append({
                        "reaction": result["term"],
                        "count": result["count"]
                    })
            
            self._save_to_cache(cache_key, events)
            return events
    
    async def get_kegg_pathways(self, drug_name: str) -> List[Dict]:
        """Query KEGG for metabolism pathways"""
        # Would implement KEGG API calls
        return []
    
    async def get_pubmed_studies(self, drug_name: str, limit: int = 10) -> List[Dict]:
        """Query PubMed for recent research"""
        cache_key = f"pubmed_{drug_name}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        async with httpx.AsyncClient() as client:
            # Search PubMed
            search_response = await client.get(
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={drug_name}+AND+drug+interactions&retmode=json&retmax={limit}"
            )
            search_data = search_response.json()
            
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if pmids:
                # Fetch article details
                pmid_str = ",".join(pmids)
                fetch_response = await client.get(
                    f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid_str}&retmode=xml"
                )
                
                # Would parse XML for title, abstract, authors, etc.
                articles = self._parse_pubmed_xml(fetch_response.text)
                self._save_to_cache(cache_key, articles)
                return articles
        
        return []
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if cached data exists and is not expired"""
        # Query api_cache table
        # Return cached data if exists and not expired
        pass
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save API response to cache"""
        # Insert into api_cache table with expiration
        pass
    
    def _extract_toxicity(self, pubchem_data: Dict) -> Dict:
        """Extract toxicity information from PubChem response"""
        # Parse the nested JSON structure
        return {}
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """Parse PubMed XML response"""
        # Use xml.etree.ElementTree to parse
        return []


# Usage in chat router
async def chat(message: ChatMessage, db: Session):
    aggregator = DrugDataAggregator(db)
    
    # Extract drug names from user query
    drug_names = extract_drug_names(message.message)
    
    # Get comprehensive data for each drug
    all_drug_data = []
    for drug in drug_names:
        data = await aggregator.get_comprehensive_drug_data(drug)
        all_drug_data.append(data)
    
    # Build context for LLM
    context = f"""
    Complete Drug Information:
    {json.dumps(all_drug_data, indent=2)}
    """
    
    # Send to Groq with 128K context window
    answer = await model_service.generate_response(
        question=message.message,
        context=context,
        user_mode=message.user_mode
    )
    
    return answer
```

## Implementation Steps

### Phase 1: Switch to Groq's Larger Model (5 minutes)
1. **Update `.env` file**:
```bash
# Change from
GROQ_MODEL=llama-3.1-8b-instant

# To
GROQ_MODEL=llama-3.1-70b-versatile
```
This gives us 128K token context window (FREE!)

### Phase 2: Setup Database Schema (30 minutes)
1. **Run SQL migrations** to create tables (see schema above)
2. **Test database** connectivity
3. **Create indexes** for performance

### Phase 3: Build Data Aggregator Service (2-3 hours)
1. **Create** `backend/services/data_aggregator_service.py`
2. **Implement API clients** for:
   - RxNorm
   - FDA DailyMed
   - PubChem
   - OpenFDA
   - PubMed
   - KEGG
3. **Add caching layer** to avoid redundant API calls
4. **Test each API** individually

### Phase 4: Integrate with Chat Router (1 hour)
1. **Update** `backend/routers/chat.py`:
   - Extract drug names from user query (regex or NER)
   - Call `DrugDataAggregator.get_comprehensive_drug_data()`
   - Build context from aggregated data
   - Pass to Groq model with full context
2. **Test** end-to-end flow

### Phase 5: Add Drug Name Extraction (1 hour)
1. **Create** `backend/services/drug_name_extractor.py`:
   - Use regex patterns for common drug names
   - Query RxNorm to validate drug names
   - Handle brand names vs generic names
2. **Test** with various queries

### Phase 6: Optimize and Cache (ongoing)
1. **Pre-populate database** with common drugs
2. **Set cache expiration** policies (30 days for static data, 1 day for adverse events)
3. **Monitor API rate limits**
4. **Add background jobs** to refresh stale cache

## Cost Analysis (ALL FREE!)

| Service | Cost | Rate Limits |
|---------|------|-------------|
| Groq (llama-3.1-70b-versatile) | **FREE** | ~14,400 requests/day |
| RxNorm API | **FREE** | No official limit |
| FDA DailyMed API | **FREE** | 240 requests/minute |
| PubChem API | **FREE** | 5 requests/second |
| OpenFDA API | **FREE** | 240 requests/minute (1000 with API key) |
| PubMed E-utilities | **FREE** | 3 requests/second (10 with API key) |
| KEGG API | **FREE** | No official limit |

**Total Monthly Cost: $0** ✅

With caching, we'll rarely hit rate limits!

## Next Steps - What You Need to Do

### Immediate (Do Now):
1. **✅ Change Groq Model** - Update `.env`:
   ```bash
   GROQ_MODEL=llama-3.1-70b-versatile
   ```
   This gives us 128K context window (vs current 8K)

2. **✅ Get Optional API Keys** (for higher rate limits):
   - OpenFDA API key: https://open.fda.gov/apis/authentication/
   - PubMed API key: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
   
   (Both are FREE, just register)

### Phase 1 Implementation (I'll do this):
1. **Create database migration** with new schema
2. **Build `DrugDataAggregator` service**
3. **Implement API clients** for all sources
4. **Add caching** to PostgreSQL
5. **Update chat router** to use aggregated data
6. **Test with sample queries**

### What This Will Give You:

**Before (Current)**:
- User asks: "What are interactions with acetaminophen?"
- AI responds based on training data only (may be outdated)
- No real-time data

**After (With Free APIs)**:
- User asks: "What are interactions with acetaminophen?"
- System:
  1. Queries RxNorm → Gets RxCUI identifier
  2. Queries FDA DailyMed → Gets official label with interactions
  3. Queries PubChem → Gets chemical structure + toxicity data
  4. Queries RxNorm interactions API → Gets known DDIs
  5. Queries OpenFDA → Gets real-world adverse events
  6. Queries PubMed → Gets recent research (last 5 years)
  7. Aggregates ALL data into context (50K-100K tokens)
  8. Sends to Groq llama-3.1-70b-versatile with full context
- AI responds with:
  - Up-to-date FDA warnings
  - Real adverse event statistics
  - Recent research findings
  - Proper citations with PMIDs
  - Chemical structure info
  - Metabolism pathways

## Example Output

**User Query**: "I'm taking acetaminophen and ibuprofen together. Is this safe?"

**System Process**:
```
1. Extract drugs: ["acetaminophen", "ibuprofen"]
2. RxNorm lookup:
   - Acetaminophen: RxCUI 161
   - Ibuprofen: RxCUI 5640
3. FDA DailyMed:
   - Acetaminophen label: [warns about NSAIDs]
   - Ibuprofen label: [warns about acetaminophen]
4. RxNorm Interactions:
   - Found moderate interaction
5. PubChem:
   - Acetaminophen CID: 1983
   - Ibuprofen CID: 3672
6. OpenFDA adverse events:
   - 234 reports of GI bleeding with combination
7. PubMed:
   - 15 recent studies on combination therapy
```

**AI Response** (Patient Mode):
```
Taking acetaminophen (Tylenol) and ibuprofen (Advil/Motrin) together is generally safe 
for short-term use, but there are some important things to know [1].

The combination can be effective for pain relief, as they work differently in your body [2]. 
However, using them together regularly may increase the risk of stomach problems and kidney 
issues, especially if you take them for more than a few days [3].

According to FDA data, about 234 people have reported stomach bleeding when using these 
together for extended periods [4]. Recent research shows this risk is higher if you're 
over 65 or take blood thinners [5].

**What you should do:**
- It's okay to alternate them (acetaminophen every 6 hours, ibuprofen every 6-8 hours)
- Don't exceed 6 regular acetaminophen tablets (3000mg) or 6 ibuprofen tablets (1200mg) 
  in 24 hours
- If you need pain relief for more than 3 days, talk to your doctor
- Take with food to protect your stomach

## REFERENCES
[1] FDA DailyMed. Acetaminophen drug label. https://dailymed.nlm.nih.gov/dailymed/...
[2] Moore et al. (2023). Combination analgesic therapy. J Pain Res. PMID: 36789123
[3] FDA Adverse Event Database. https://open.fda.gov/...
[4] OpenFDA Query Results (2024). Acetaminophen + Ibuprofen adverse events.
[5] Chen et al. (2024). NSAID combinations in elderly patients. JAMA. PMID: 37654321
```

**Ready to start building this?**

Let me know and I'll:
1. First update the `.env` to use the larger Groq model
2. Create the database migration
3. Build the data aggregator service
4. Test with real queries
