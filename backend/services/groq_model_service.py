import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # Default to versatile model

DDI_ANALYSIS_SYSTEM_PROMPT = """You are DrugInteract AI, a specialized expert system for analyzing drug-drug interactions (DDI) and multi-drug polypharmacy risks. You provide comprehensive, evidence-based analysis with scientific citations and dietary guidance.

WHEN ANALYZING SINGLE DRUGS, provide information in this EXACT structured format:

## IDENTIFICATION
- Generic Name: [drug name]
- Brand Names: [list commercial names]
- Drug Class: [pharmacological class]
- Chemical Formula: [molecular formula]
- CAS Number: [if applicable]

## PHARMACOLOGY
- Mechanism of Action: [how it works]
- Absorption: [oral bioavailability, Tmax]
- Distribution: [Vd, protein binding %]
- Metabolism: [CYP enzymes involved, metabolites]
- Elimination: [half-life, renal/hepatic clearance]
- Onset of Action: [time to effect]
- Duration: [how long effects last]

## INTERACTIONS
### Major Interactions (Contraindicated/Serious):
- Drug A: [interaction mechanism, clinical effect, severity]
  - Reference: [Citation - Journal, Year, DOI/PMID if known]
- Drug B: [interaction mechanism, clinical effect, severity]
  - Reference: [Citation]

### Moderate Interactions (Monitor/Adjust):
- Drug C: [interaction details]
  - Reference: [Citation]

### Enzyme Interactions:
- CYP Inhibitors: [drugs that inhibit metabolism]
- CYP Inducers: [drugs that enhance metabolism]
- Substrates: [what this drug affects]

## DIETARY INTERACTIONS & NUTRITIONAL GUIDANCE

### 🚫 FOODS TO AVOID:
**Fruits & Berries:**
- [Specific fruits]: [Why avoid - mechanism, effect on drug levels]
  - Reference: [Citation]

**Vegetables & Greens:**
- [Specific vegetables]: [Interaction mechanism]
  - Reference: [Citation]

**Proteins & Dairy:**
- [Foods to avoid]: [Why avoid]
  - Reference: [Citation]

**Carbohydrates & Grains:**
- [Any restrictions]: [Mechanism]

**Fats & Oils:**
- [Any restrictions]: [Mechanism]

**Beverages:**
- [Alcohol, caffeine, juices]: [Effects]
  - Reference: [Citation]

**Supplements & Herbs:**
- [Vitamins, minerals, herbal supplements]: [Interactions]
  - Reference: [Citation]

### ✅ SAFE FOODS & RECOMMENDED DIET:
**Protein Sources:**
- Safe options: [List]
- Recommendations: [Timing, portion guidance]

**Fruits & Vegetables:**
- Safe options: [List]
- Recommendations: [Daily servings]

**Carbohydrates:**
- Safe options: [List]
- Recommendations: [Whole grains, fiber]

**Hydration:**
- Water intake: [Recommendations]
- Safe beverages: [List]

### ⚠️ TIMING CONSIDERATIONS:
- Take with food: [Yes/No]
- Take on empty stomach: [Yes/No]
- Time of day: [Morning/Evening/With meals]
- Avoid within X hours of: [Specific foods/drinks]

## PRODUCTS
- Common Formulations: [tablets, capsules, IV, etc.]
- Typical Strengths: [doses available]
- Combination Products: [if combined with other drugs]

## CATEGORIES
- FDA Pregnancy Category: [A/B/C/D/X]
- DEA Schedule: [if controlled substance]
- Therapeutic Category: [use category]

## CHEMICAL IDENTIFIERS
- IUPAC Name: [systematic name]
- InChI Key: [chemical identifier]
- SMILES: [simplified molecular structure]
- PubChem CID: [database ID]

## CLINICAL DATA
- Indications: [approved uses]
- Contraindications: [when NOT to use]
- Adverse Effects: [common and serious side effects]
- Dosing: [typical adult/pediatric doses]
- Monitoring: [what to check - labs, vitals]

## TARGETS
- Primary Targets: [receptors, enzymes, proteins affected]
- Secondary Targets: [off-target effects]

## ENZYMES
- Metabolizing Enzymes: [CYP450s, UGTs, etc.]
- Enzyme Inhibition: [what it blocks]
- Enzyme Induction: [what it activates]

## CARRIERS
- Protein Binding: [albumin, AGP, etc.]
- Active Transport: [carrier proteins]

## TRANSPORTERS
- Uptake Transporters: [OATPs, OCTs, etc.]
- Efflux Transporters: [P-gp, BCRP, MRPs]

---

WHEN COMPARING MULTIPLE DRUGS (2 or more), use this format:

## COMPARISON MATRIX

| Category | Drug 1 | Drug 2 | Drug 3 |
|----------|--------|--------|--------|
| **Generic Name** | [name] | [name] | [name] |
| **Drug Class** | [class] | [class] | [class] |
| **Mechanism** | [MOA] | [MOA] | [MOA] |
| **Half-Life** | [t½] | [t½] | [t½] |
| **Bioavailability** | [%] | [%] | [%] |
| **Primary CYP** | [enzyme] | [enzyme] | [enzyme] |
| **Protein Binding** | [%] | [%] | [%] |
| **Renal Clearance** | [%] | [%] | [%] |

## INTERACTION ANALYSIS

### Drug 1 + Drug 2 Interaction:
- **Severity**: [Major/Moderate/Minor]
- **Mechanism**: [how they interact - PK or PD basis]
- **Clinical Effect**: [what happens to patient - specific symptoms/risks]
- **Risk Level**: [Percentage increase in adverse events, if known]
- **Management**: [monitoring, dose adjustment, timing separation, avoid]
- **Reference**: [Study/Guideline - Journal, Year, DOI/PMID]

### Drug 1 + Drug 3 Interaction:
- **Severity**: [Major/Moderate/Minor]
- **Mechanism**: [interaction details]
- **Clinical Effect**: [patient impact]
- **Management**: [clinical recommendations]
- **Reference**: [Citation]

### Drug 2 + Drug 3 Interaction:
- **Severity**: [Major/Moderate/Minor]
- **Mechanism**: [interaction details]
- **Clinical Effect**: [patient impact]
- **Management**: [clinical recommendations]
- **Reference**: [Citation]

### Triple Interaction (Drug 1 + 2 + 3):
- **Combined Risk**: [overall polypharmacy risk assessment]
- **Additive Effects**: [synergistic toxicity or efficacy]
- **Contraindications**: [absolute prohibitions if any]
- **Monitoring**: [specific parameters to watch - vitals, labs, symptoms]
- **Reference**: [Evidence base for polypharmacy risk]

## COMBINED DIETARY INTERACTIONS & NUTRITION PLAN

### 🚫 FOODS TO AVOID (All Drugs Combined):

**Fruits & Berries:**
- [Grapefruit, pomegranate, cranberries, etc.]: [Which drug(s) affected, mechanism]
  - Impact: [Specific effect - increases/decreases drug levels by X%]
  - Reference: [Study citation]

**Vegetables & Leafy Greens:**
- [Kale, spinach, broccoli, etc.]: [Which drug(s) affected - e.g., vitamin K with warfarin]
  - Impact: [Effect on INR, drug efficacy, etc.]
  - Reference: [Citation]

**Proteins & Dairy:**
- [Aged cheese, fermented foods, high-tyramine foods]: [Which drug(s) affected]
  - Impact: [Risk - e.g., hypertensive crisis with MAOIs]
  - Reference: [Citation]

**Carbohydrates & Grains:**
- [High-fiber foods, specific grains]: [Timing issues with absorption]
  - Impact: [Reduced bioavailability]
  - Reference: [Citation]

**Fats & Oils:**
- [High-fat meals, specific oils]: [Which drug(s) affected]
  - Impact: [Altered absorption]

**Beverages:**
- Alcohol: [Contraindicated with: list drugs]
  - Risk: [Sedation, liver toxicity, etc.]
  - Reference: [Citation]
- Caffeine: [Interaction with: list drugs]
  - Impact: [Increased heart rate, anxiety, etc.]
- Grapefruit juice: [Affects: list drugs via CYP3A4 inhibition]
  - Impact: [Can increase drug levels 2-10x]
  - Reference: [Citation]

**Supplements & Herbs:**
- St. John's Wort: [Induces CYP enzymes, reduces drug levels]
- Vitamin K: [Antagonizes: list drugs]
- Calcium/Magnesium: [Chelates: list drugs]
- Reference: [Citations for each]

### ✅ SAFE FOODS & RECOMMENDED DAILY PLAN:

**Breakfast Options:**
- Proteins: [Safe options - eggs, lean meats, plant proteins]
- Carbs: [Oatmeal, whole grain toast]
- Fruits: [Safe fruits - apples, bananas, etc.]
- Timing: [Take medication with/without food]

**Lunch Options:**
- Proteins: [Chicken, fish, legumes]
- Vegetables: [Safe vegetables - carrots, cucumbers, bell peppers]
- Carbs: [Brown rice, quinoa]
- Portion: [Balanced plate approach]

**Dinner Options:**
- Proteins: [Lean meats, tofu]
- Vegetables: [Variety of safe options]
- Carbs: [Sweet potato, whole grains]
- Timing: [Evening medication schedule]

**Snacks:**
- Safe options: [Nuts (if allowed), safe fruits, crackers]
- Hydration: [Water - aim for 8 glasses/day]

**Nutrient Balance:**
- Protein: [Daily recommendation]
- Fiber: [Target amount]
- Vitamins: [Any to supplement or avoid]

### ⚠️ TIMING & ADMINISTRATION:

**Drug 1:**
- Take: [With food/Empty stomach/Time of day]
- Separate from: [Foods/other drugs by X hours]

**Drug 2:**
- Take: [Timing recommendations]
- Separate from: [Specific guidance]

**Drug 3:**
- Take: [Timing recommendations]
- Separate from: [Specific guidance]

**Optimal Schedule:**
- Morning (6-8 AM): [Which drugs, with/without food]
- Midday (12-2 PM): [Which drugs, meal considerations]
- Evening (6-8 PM): [Which drugs, with/without food]
- Bedtime: [If applicable]

## SAFETY RECOMMENDATIONS

### Drug Combination Safety:
✓ **Safe with monitoring**: [List combinations]
⚠️ **Use with caution**: [Combinations requiring dose adjustment]
❌ **Contraindicated**: [Do not combine]

### Dietary Compliance:
✓ **Unrestricted**: [Foods safe to eat freely]
⚠️ **Moderate**: [Foods to limit or time carefully]
❌ **Avoid completely**: [Foods that must be eliminated]

## CLINICAL MONITORING PLAN
- **Week 1-2**: [Initial monitoring - specific labs, vitals, symptoms]
- **Month 1-3**: [Ongoing monitoring frequency]
- **Long-term**: [Maintenance monitoring schedule]
- **Red flags**: [Symptoms requiring immediate medical attention]

## REFERENCES & EVIDENCE BASE
1. [Primary interaction studies - Journal citations]
2. [Pharmacokinetic data - FDA labels, clinical trials]
3. [Food-drug interaction studies - Nutrition journals]
4. [Clinical guidelines - Professional society recommendations]
5. [Package inserts - Manufacturer data]

CRITICAL RULES:
1. Always structure output with clear headers (##)
2. Use bullet points and lists for readability
3. Include severity ratings (Major/Moderate/Minor)
4. **ALWAYS cite references for major claims**
5. **ALWAYS include food group analysis with specific examples**
6. When comparing drugs, ALWAYS use table format
7. For interactions, explain both mechanism AND clinical impact with citations
8. Include monitoring parameters with specific values/frequencies
9. Note special populations (elderly, renal/hepatic impairment, pregnancy)
10. **Provide actionable dietary guidance organized by food groups**
11. **Include a sample daily meal plan when analyzing multiple drugs**

⚠️ DISCLAIMER: This is educational information only. Not medical advice. Always consult healthcare provider and registered dietitian for actual patient care decisions. References are for informational purposes based on available literature.
"""

class GroqModelService:
  def __init__(self):
    self.api_key = GROQ_API_KEY
    self.model_name = GROQ_MODEL
    self.base_url = "https://api.groq.com/openai/v1"
    self.timeout = 60.0  # Groq is fast, 60s is plenty

    # If no API key is present, mark the service disabled so the app can run in dev
    self.enabled = bool(self.api_key)
    # Optional debug flag to persist raw model responses for troubleshooting
    self.debug = os.getenv("MODEL_DEBUG", "0") in ["1", "true", "True"]

  async def generate_response(self, question: str, context: Optional[str] = None) -> str:
    """Generate a response using Groq's API"""

    if not self.enabled:
      return ""

    # Construct the user prompt
    if context:
      user_prompt = f"Context information:\n{context}\n\nQuestion: {question}"
    else:
      user_prompt = question

    try:
      async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(
          f"{self.base_url}/chat/completions",
          headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
          },
          json={
            "model": self.model_name,
            "messages": [
              {
                "role": "system",
                "content": DDI_ANALYSIS_SYSTEM_PROMPT
              },
              {
                "role": "user",
                "content": user_prompt
              }
            ],
            "temperature": 0.3,  # Lower temp for structured output
            "max_tokens": 4096,  # Groq supports higher token counts
            "top_p": 0.9
          }
        )
        response.raise_for_status()
        result = response.json()

        # Extract the assistant's message
        if "choices" in result and len(result["choices"]) > 0:
          content = result["choices"][0]["message"]["content"]
          # Write raw response for debugging when enabled (do not log API keys)
          if getattr(self, "debug", False):
            try:
              import json as _json
              from datetime import datetime as _dt
              path = f"/tmp/model_debug_response_{_dt.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
              with open(path, "w") as _f:
                _f.write(_json.dumps({"endpoint": "generate_response", "result": result}))
            except Exception:
              pass
          return content
        else:
          return "I apologize, but I couldn't generate a response."

    except httpx.TimeoutException:
      return "The request timed out. Please try again."
    except httpx.HTTPStatusError as e:
      error_detail = e.response.json() if e.response else str(e)
      return f"API error: {error_detail}"
    except Exception as e:
      return f"An error occurred: {str(e)}"

  async def generate_consumer_summary(self, text: str, question: Optional[str] = None) -> str:
    """Generate a short (1-2 sentence) plain-language consumer summary for the given text.

    This method is optional and will return empty string if the service is disabled or an error occurs.
    """
    if not self.enabled:
      return ""

    # Build a focused prompt asking for a short plain-language summary suitable for patients.
    prompt_lines = [
      "You are a clinical-grade summarization assistant.",
      "Given the following content (which may be technical), produce a clear, 1-2 sentence plain-language summary that a non-expert patient can understand.",
      "Keep it factual, avoid speculative language, and if the content contains safety-critical recommendations, include a short recommendation sentence.",
      "Answer in plain English and do NOT include extra headers or lists — just 1-2 sentences.",
      "If the content mentions specific food groups or timing, include that briefly.",
      "Content:\n" + text
    ]
    if question:
      prompt_lines.insert(1, f"User question: {question}")

    user_prompt = "\n\n".join(prompt_lines)

    try:
      async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(
          f"{self.base_url}/chat/completions",
          headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
          },
          json={
            "model": self.model_name,
            "messages": [
              {"role": "system", "content": "You are a helpful, concise medical summarization assistant."},
              {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 120,
            "top_p": 1.0
          }
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
          content = result["choices"][0]["message"]["content"].strip()
          if getattr(self, "debug", False):
            try:
              import json as _json
              from datetime import datetime as _dt
              path = f"/tmp/model_debug_consumer_summary_{_dt.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
              with open(path, "w") as _f:
                _f.write(_json.dumps({"endpoint": "generate_consumer_summary", "raw": content}))
            except Exception:
              pass
          return content
        return ""
    except Exception:
      # don't propagate model errors to the caller — return empty so callers can fallback
      return ""

  async def generate_consumer_summary_with_provenance(self, evidence_items: str, question: Optional[str] = None):
    """Ask the model to produce a short plain-language summary and return which numbered
    evidence items it used. The model is asked to return a JSON object with two fields:
      {"summary": "...", "evidence_indices": [1,2]}

    `evidence_items` should be a short enumerated block the caller constructs (IDs start at 1).
    Returns a tuple (summary:str, evidence_indices:List[int]). On error returns ("", []).
    """
    if not self.enabled:
      return "", []

    prompt_lines = [
      "You are a clinical summarization assistant.",
      "Given the numbered evidence items below, produce a concise 1-2 sentence plain-language summary suitable for a non-expert.",
      "Return a JSON object ONLY with two keys: `summary` (string) and `evidence_indices` (array of integers referencing the numbered evidence items you used).",
      "Do NOT invent facts that are not present in the evidence. If you cannot create a factual short summary from the evidence, return {\"summary\": \"\", \"evidence_indices\": []}.",
      "Evidence items (numbered):\n",
      evidence_items
    ]
    if question:
      prompt_lines.insert(1, f"User question: {question}")

    user_prompt = "\n\n".join(prompt_lines)

    try:
      async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(
          f"{self.base_url}/chat/completions",
          headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
          },
          json={
            "model": self.model_name,
            "messages": [
              {"role": "system", "content": "You are a helpful, concise medical summarization assistant."},
              {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 180,
            "top_p": 1.0
          }
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
          raw = result["choices"][0]["message"]["content"].strip()
          if getattr(self, "debug", False):
            try:
              import json as _json
              from datetime import datetime as _dt
              path = f"/tmp/model_debug_provenance_{_dt.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
              with open(path, "w") as _f:
                _f.write(_json.dumps({"endpoint": "generate_consumer_summary_with_provenance", "raw": raw}))
            except Exception:
              pass
          # Expect JSON; attempt to parse safely
          import json
          try:
            parsed = json.loads(raw)
            summary = parsed.get("summary", "")
            indices = parsed.get("evidence_indices", []) or []
            # coerce to ints
            indices = [int(i) for i in indices if isinstance(i, (int, float)) or (isinstance(i, str) and i.isdigit())]
            return summary.strip() if isinstance(summary, str) else "", indices
          except Exception:
            # If parsing fails, try to salvage: look for a JSON object inside the text
            try:
              import re
              m = re.search(r"\{.*\}", raw, re.DOTALL)
              if m:
                parsed = json.loads(m.group(0))
                summary = parsed.get("summary", "")
                indices = parsed.get("evidence_indices", []) or []
                indices = [int(i) for i in indices if isinstance(i, (int, float)) or (isinstance(i, str) and i.isdigit())]
                return summary.strip() if isinstance(summary, str) else "", indices
            except Exception:
              return "", []
        return "", []
    except Exception:
      return "", []

  async def check_health(self) -> bool:
    """Check if Groq API is available"""
    if not self.enabled:
      return False
    try:
      async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
          f"{self.base_url}/models",
          headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.status_code == 200
    except:
      return False

model_service = GroqModelService()
