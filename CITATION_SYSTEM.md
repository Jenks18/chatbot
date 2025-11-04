# Model-Generated Citation System

## Overview
The AI model now automatically generates inline citations and references for all responses, similar to academic papers with APA-style formatting.

## How It Works

### 1. **System Prompt Instructions**
The model is instructed to:
- Include inline citations `[1]`, `[2]`, `[3]` after EVERY factual claim
- End responses with a `## REFERENCES` section
- Use APA-style formatting for all references
- Cite peer-reviewed journals, clinical guidelines, FDA labels, etc.
- Include author(s), year, title, journal/source, DOI/PMID when available

### 2. **Example Output**
```
Acetaminophen is metabolized primarily by hepatic conjugation [1]. 
The maximum daily dose is 4000mg to prevent hepatotoxicity [2].

## REFERENCES
[1] Prescott, L. F. (2000). Paracetamol, alcohol and the liver. British Journal of Clinical Pharmacology, 49(4), 291-301. PMID: 10759684
[2] FDA. (2011). Acetaminophen Information. FDA Drug Safety Communication.
```

### 3. **Backend Processing**
The backend (`backend/routers/chat.py`):
- Receives the model's response with citations and references
- Parses the `## REFERENCES` section using regex
- Extracts citation numbers, titles, and URLs/PMIDs
- Converts PMIDs to PubMed URLs
- Creates evidence objects with the parsed references
- Sends structured data to the frontend

### 4. **Frontend Display**
The frontend (`components/ChatInterface.tsx`):
- Parses inline citations `[1]`, `[2]` from the text
- Renders them as clickable, styled badges
- Displays the full references section at the bottom
- Allows clicking citations to jump to references
- Shows references expanded by default

### 5. **Citation Styling**
Enhanced CSS (`styles/globals.css`):
- Citation badges with emerald gradient backgrounds
- Hover effects with elevation
- Numbered circular badges for references
- Professional APA-style formatting

## Benefits

1. **No Database Required**: Model generates citations from its training data
2. **Always Up-to-Date**: Uses model's knowledge of medical literature
3. **Comprehensive**: Cites multiple authoritative sources
4. **Professional**: Academic-quality APA formatting
5. **Interactive**: Clickable citations with smooth scrolling
6. **Transparent**: Clear source attribution for all claims

## Configuration

### Model Service (`backend/services/groq_model_service.py`)
- Updated `DDI_ANALYSIS_SYSTEM_PROMPT` with citation requirements
- Updated `generate_consumer_summary()` to include citations
- Increased max_tokens to 150 for summaries with citations

### Citation Parsing (`backend/routers/chat.py`)
- Regex pattern: `r'##\s*REFERENCES?\s*\n(.*?)(?=\n##|\Z)'`
- Reference pattern: `r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|\Z)'`
- PMID conversion: `PMID: 12345` → `https://pubmed.ncbi.nlm.nih.gov/12345/`

## Testing

Try queries like:
- "Tell me about panadol"
- "What are the drug interactions with acetaminophen?"
- "Explain the toxicity of lead"

You should see:
- Inline citations [1], [2], [3] throughout the response
- A "References (X)" button at the bottom
- Full references with clickable links to PubMed/sources
- Smooth animations when clicking citations

## Future Enhancements

- [ ] Add citation count to response metadata
- [ ] Allow filtering by citation quality/source type
- [ ] Export references to BibTeX format
- [ ] Add "Cite this" button for copying APA format
- [ ] Track most commonly cited sources
