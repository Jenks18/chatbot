import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # Default to versatile model

DDI_ANALYSIS_SYSTEM_PROMPT = """You are DrugInteract AI, a specialized expert system for analyzing drug-drug interactions (DDI) and multi-drug polypharmacy risks. You provide comprehensive, structured analysis of medications.

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
- Drug B: [interaction mechanism, clinical effect, severity]

### Moderate Interactions (Monitor/Adjust):
- Drug C: [interaction details]

### Enzyme Interactions:
- CYP Inhibitors: [drugs that inhibit metabolism]
- CYP Inducers: [drugs that enhance metabolism]
- Substrates: [what this drug affects]

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
- **Mechanism**: [how they interact]
- **Clinical Effect**: [what happens to patient]
- **Management**: [monitoring, dose adjustment, avoid]

### Drug 1 + Drug 3 Interaction:
[same format]

### Drug 2 + Drug 3 Interaction:
[same format]

### Triple Interaction (Drug 1 + 2 + 3):
- **Combined Risk**: [overall polypharmacy risk]
- **Additive Effects**: [synergistic toxicity or efficacy]
- **Contraindications**: [absolute prohibitions]
- **Monitoring**: [what to watch]

## SAFETY RECOMMENDATIONS
✓ Safe combinations with monitoring
⚠️ Use with caution (dose adjustment needed)
❌ Contraindicated (do not combine)

CRITICAL RULES:
1. Always structure output with clear headers (##)
2. Use bullet points and lists for readability
3. Include severity ratings (Major/Moderate/Minor)
4. Provide actionable clinical recommendations
5. When comparing drugs, ALWAYS use table format
6. For interactions, explain both mechanism AND clinical impact
7. Include monitoring parameters
8. Note special populations (elderly, renal/hepatic impairment, pregnancy)

⚠️ DISCLAIMER: This is educational information only. Not medical advice. Always consult healthcare provider for actual patient care decisions.
"""

class GroqModelService:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model_name = GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = 60.0  # Groq is fast, 60s is plenty

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

    async def generate_response(self, question: str, context: Optional[str] = None) -> str:
        """Generate a response using Groq's API"""
        
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
                    return result["choices"][0]["message"]["content"]
                else:
                    return "I apologize, but I couldn't generate a response."
                
        except httpx.TimeoutException:
            return "The request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else str(e)
            return f"API error: {error_detail}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def check_health(self) -> bool:
        """Check if Groq API is available"""
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
