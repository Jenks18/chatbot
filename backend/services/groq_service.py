"""
Groq Model Service - Using Compound Model with Official SDK
Provides AI responses using Groq's compound model with tools (web_search, code_interpreter, visit_website)
"""
from groq import Groq
import os
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from functools import partial

# Load .env from backend directory (local dev only)
try:
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except:
    pass  # Skip on serverless - env vars come from platform

# Mode-specific prompts with reading level enforcement
PATIENT_MODE_PROMPT = """You are a helpful medical assistant speaking to a general patient audience.

CRITICAL FORMATTING - Write for patients (6th grade reading level):

**NEVER use dense paragraphs, complex tables, or medical jargon!**

**Required Structure:**
1. Start with a simple 1-sentence answer
2. Use emoji section headers (💊 📋 ⚠️ 🏥)
3. Short paragraphs (2-3 sentences MAXIMUM)
4. Simple bullet points with dashes (-)
5. Use **bold** for safety warnings
6. End with "Questions? Talk to your doctor or pharmacist."

**Writing Style:**
- Sentences: 10-15 words max
- Words: Simple (use "take" not "administer", "doctor" not "physician")
- No medical terms (if needed, explain in parentheses)
- Active voice ("Take 2 pills" not "2 pills should be taken")
- Use "you" and "your" (conversational)

**Example Format:**
💊 **What is [Drug]?**
[Drug] is a pain reliever. It helps with headaches and fever.

📋 **How to Take It**
- Take 1-2 pills every 4-6 hours
- Don't take more than 8 pills in 24 hours
- You can take it with or without food

⚠️ **Important Warnings**
**Stop taking it and call your doctor if you:**
- Get a rash or itching
- Feel very sick to your stomach
- Notice yellow skin or eyes

**Tone:** Friendly, caring, like talking to a family member who needs help."""

DOCTOR_MODE_PROMPT = """You are a medical expert assistant speaking to a healthcare professional.

CRITICAL FORMATTING - Write for physicians (12th grade medical level):

**NEVER use dense paragraph walls or excessive tables!**

**Required Structure:**
1. One-sentence clinical summary
2. Clear sections with bold headers
3. Bullet points (NOT long paragraphs)
4. Only use tables if absolutely necessary (max 1 small table)
5. Bold critical info
6. End with key clinical pearl

**Sections to Include:**
**Clinical Use:** Indications with evidence level
**Dosing:** Standard + adjustments (bullets, not tables)
**Contraindications:** Key ones only
**Interactions:** Significant ones with mechanism
**Monitoring:** What to check
**Clinical Pearl:** One actionable tip

**Writing Style:**
- Concise bullets (1-2 lines each)
- Medical terms OK (contraindication, pharmacokinetics)
- Include mechanism ONLY if clinically relevant
- Use abbreviations (PO, BID, q6h, PRN)
- Focus on decision-making

**Example Format:**
**Clinical Use**
First-line for mild-moderate pain (Level A evidence). Antipyretic in fever of any cause.

**Dosing**
- Standard: 500-1000 mg PO q4-6h PRN (max 4g/day)
- Hepatic impairment: Max 2g/day
- Elderly: Start 500 mg q6h

**Contraindications**
- Severe hepatic disease
- Acute liver failure

**Key Interaction**
Warfarin: Monitor INR (minor ↑ risk)

**Clinical Pearl**
Schedule dosing (q6h) for chronic pain rather than PRN for better analgesia.

**Tone:** Professional, concise, clinical."""

RESEARCHER_MODE_PROMPT = """You are a scientific research assistant speaking to an academic researcher or scientist.

CRITICAL FORMATTING - Write for researchers (academic level):

**NEVER use clinical-style tables or oversimplify!**

**Required Structure:**
1. Brief scientific context (1-2 sentences)
2. Clear sections with scientific focus
3. Academic prose with embedded data
4. Quantitative parameters inline (not in tables)
5. Study citations inline (design, n, findings)
6. End with knowledge gaps

**Sections to Include:**
**Molecular Mechanism:** Targets, pathways with intermediate steps
**Pharmacokinetics:** ADME with quantitative parameters
**Current Research:** Recent findings with study details
**Methodology:** Analytical approaches
**Knowledge Gaps:** What's unknown/under investigation

**Writing Style:**
- Scientific prose (not bullet points)
- Technical terminology (IC₅₀, Kd, t½, AUC, Cmax)
- Biochemical pathways (MAPK/ERK, CYP450, etc.)
- Inline data: "exhibits biphasic elimination (t½α = 0.5h, t½β = 2.1h)"
- Study context: "Phase III RCT (n=1,203) demonstrated..."
- Statistical rigor: confidence intervals, p-values

**Example Format:**
Acetaminophen (APAP) primarily acts via central COX inhibition, though the precise molecular mechanism remains debated. Current evidence suggests weak, reversible inhibition of both COX-1 and COX-2 isoforms (IC₅₀ ≈ 25-50 μM in neural tissue), with preferential activity in the CNS versus peripheral tissues.

Pharmacokinetically, APAP exhibits rapid oral absorption (tmax = 30-60 min) with extensive first-pass hepatic metabolism. Approximately 90-95% undergoes Phase II conjugation (glucuronidation 50-60%, sulfation 30-40%), while 5-10% is oxidized via CYP2E1 to the reactive intermediate NAPQI. A recent metabolomics study (J Pharm Sci 2024, n=156 healthy volunteers) identified three novel minor metabolites, suggesting additional metabolic pathways warrant investigation.

Current research focuses on APAP's role in endocannabinoid modulation. APAP is deacetylated to p-aminophenol, which conjugates with arachidonic acid to form AM404, an endocannabinoid reuptake inhibitor. This pathway may explain APAP's analgesic effects independent of prostaglandin synthesis.

**Knowledge gap:** The relative contribution of COX inhibition versus endocannabinoid modulation to clinical analgesia remains unquantified in human studies.

**Tone:** Academic, precise, hypothesis-driven."""


class GroqModelService:
    """Service for interacting with Groq API using compound model with tools"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = "groq/compound"
        is_vercel = os.getenv('VERCEL') == '1'
        
        if not self.api_key:
            if not is_vercel:
                print("⚠️  WARNING: GROQ_API_KEY not set")
            self.client = None
        else:
            self.client = Groq(
                api_key=self.api_key,
                default_headers={
                    "Groq-Model-Version": "latest"
                }
            )
            if not is_vercel:
                print(f"✅ Groq API initialized: {self.model_name} (with tools enabled)")
    
    async def generate_response(
        self,
        query: str = None,
        question: str = None,  # Alias for query
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 1500,  # Reduced from 2000 to prevent "too large" errors
        temperature: float = 0.7,
        enable_tools: bool = True
    ) -> str:  # Return string directly like old service
        """
        Generate a response using Groq compound model
        
        Args:
            query: User's question (or use question parameter)
            question: Alias for query parameter
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            enable_tools: Enable web_search, code_interpreter, visit_website
            
        Returns:
            String response content
        """
        # Handle both query and question parameters
        user_query = query or question
        if not user_query:
            return "Error: No question provided"
        
        if not self.client:
            return "Error: GROQ_API_KEY not configured. Get your free key at https://console.groq.com/keys"
        
        # Select system prompt based on mode with formatting enforcement
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT + "\n\n🚨 CRITICAL: You MUST use emoji headers, short paragraphs (max 3 sentences), simple bullets, and bold warnings. NO medical jargon or dense text!",
            "doctor": DOCTOR_MODE_PROMPT + "\n\n🚨 CRITICAL: You MUST use bullet points, NOT paragraph walls. ONE small table maximum. Focus on clinical decisions. Be scannable!",
            "researcher": RESEARCHER_MODE_PROMPT + "\n\n🚨 CRITICAL: You MUST use scientific prose with inline data. NO clinical tables. Include quantitative parameters, study details, and mechanisms."
        }
        system_prompt = mode_prompts.get(user_mode, mode_prompts["patient"])
        
        # Build the full prompt
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {user_query}"
        else:
            user_content = user_query
        
        try:
            # Run synchronous Groq API call in thread pool (SDK is not async)
            # The compound model automatically has tools enabled
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,  # Use default executor
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=True,
                    stop=None
                )
            )
            
            # Collect streamed response
            full_content = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return full_content  # Return string directly
                    
        except Exception as e:
            error_msg = str(e)
            return f"API error: {error_msg}"
    
    async def generate_consumer_summary(
        self,
        technical_info: str,
        drug_name: str = "",
        question: str = "",
        user_mode: str = "patient"  # Add user_mode parameter
    ) -> str:
        """
        Generate mode-appropriate simplified summary from technical information
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            question: Optional user question for context
            user_mode: patient/doctor/researcher to customize summary level
            
        Returns:
            Simplified summary appropriate for the user mode
        """
        if not self.client:
            return ""
        
        # Mode-specific summary prompts
        if user_mode == "patient":
            prompt = f"""Create a very brief, patient-friendly summary.

REQUIREMENTS:
- Write for 6th graders
- Use 2-4 SHORT sentences (10-15 words each)
- Use simple everyday words
- Focus on: what it does, how to use it, key warning

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Information:
{technical_info[:1000]}

Provide ONLY the simple summary (no headers, no formatting)."""
            
        elif user_mode == "doctor":
            prompt = f"""Create a concise clinical summary for physicians.

REQUIREMENTS:
- 2-3 sentences maximum
- Key clinical points only (indication, dosing, major contraindication)
- Use medical terminology
- Actionable and concise

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Information:
{technical_info[:1200]}

Provide ONLY the clinical summary."""
            
        else:  # researcher
            prompt = f"""Create a scientific summary for researchers.

REQUIREMENTS:
- 2-3 sentences maximum
- Focus on mechanisms, pathways, and research gaps
- Include quantitative data if available
- Academic tone

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Information:
{technical_info[:1200]}

Provide ONLY the scientific summary."""

        result = await self.generate_response(
            query=prompt,
            user_mode=user_mode,
            max_tokens=300,  # Keep summaries short
            temperature=0.5,
            enable_tools=False
        )
        
        return result
    
    async def generate_consumer_summary_with_provenance(
        self,
        evidence_items: str,
        question: str = None
    ) -> tuple:
        """
        Generate a summary with provenance tracking
        
        Args:
            evidence_items: Numbered evidence items
            question: User's question
            
        Returns:
            Tuple of (summary: str, evidence_indices: List[int])
        """
        if not self.client:
            return "", []
        
        prompt_lines = [
            "You are a clinical summarization assistant.",
            "Given the numbered evidence items below, produce a concise 1-2 sentence plain-language summary suitable for a non-expert.",
            "Return a JSON object ONLY with two keys: `summary` (string) and `evidence_indices` (array of integers referencing the numbered evidence items you used).",
            "Do NOT invent facts. If you cannot create a factual summary, return {\"summary\": \"\", \"evidence_indices\": []}.",
            "",
            "Evidence items (numbered):",
            evidence_items
        ]
        if question:
            prompt_lines.insert(1, f"User question: {question}")
        
        user_prompt = "\n".join(prompt_lines)
        
        try:
            # Run synchronous SDK call in thread pool
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful, concise medical summarization assistant. Always return valid JSON."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    max_tokens=200,
                    stream=False
                )
            )
            
            raw = completion.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            parsed = json.loads(raw)
            summary = parsed.get("summary", "")
            indices = parsed.get("evidence_indices", []) or []
            
            # Validate indices are integers
            valid_indices = [int(i) for i in indices if isinstance(i, (int, float))]
            
            return summary, valid_indices
            
        except Exception as e:
            # Return empty on error so caller can fallback
            return "", []
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Groq API is accessible
        
        Returns:
            Dict with health status
        """
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "GROQ_API_KEY not configured",
                "details": "Get your free API key at https://console.groq.com/keys"
            }
        
        try:
            # Run synchronous SDK call in thread pool
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                    stream=False
                )
            )
            
            print("[Groq Health Check] ✓ API is accessible")
            return {
                "status": "healthy",
                "model": self.model_name,
                "tools": ["web_search", "code_interpreter", "visit_website"]
            }
                    
        except Exception as e:
            error_msg = str(e)
            print(f"[Groq Health Check] ✗ API error: {error_msg}")
            return {
                "status": "unhealthy",
                "error": error_msg,
                "details": "Cannot connect to Groq API"
            }


# Create singleton instance
groq_service = GroqModelService()
