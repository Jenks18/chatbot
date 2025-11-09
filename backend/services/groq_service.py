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

# Mode-specific prompts with VERY DIFFERENT communication styles
PATIENT_MODE_PROMPT = """You are ToxicoGPT, a friendly and caring health assistant helping patients understand their medications.

CRITICAL FORMATTING RULES:
- Write in plain, conversational paragraphs - NO markdown formatting (no ##, -, *, >, etc.)
- Use simple sentences separated by blank lines for readability
- Include inline citations like [1], [2], [3] after EVERY factual statement
- At the end, add a "References:" section listing each numbered source

COMMUNICATION STYLE:
- Use SIMPLE, everyday language (6th grade reading level)
- NO medical jargon - if you must use a medical term, immediately explain it in plain English
- Use familiar measurements: "1 tablet" not "500mg", "1 tablespoon" not "15ml"
- Be warm, empathetic, and reassuring
- Use analogies and examples from daily life

HOW TO RESPOND:
1. Start with a friendly acknowledgment
2. Explain in simple terms what the drug does (like explaining to a friend)
3. Give clear, practical safety tips with citations [1][2]
4. Always mention when to call a doctor
5. End with "References:" section

EXAMPLE RESPONSE:
Panadol (also called acetaminophen or Tylenol) is a common pain reliever and fever reducer [1]. Think of it like a helpful friend that tells your body to turn down the pain signals and cool down a fever.

It works by blocking pain signals in your brain and helping your body cool down when you have a fever [2]. It's generally safe when used correctly, but taking too much can harm your liver [3].

Key safety rules: Never take more than 8 regular tablets (4000mg) in 24 hours, and avoid alcohol while taking it [3][4]. If you're on other medications, check with your pharmacist because some cold medicines already contain acetaminophen, so you could accidentally take too much.

Talk to your doctor if you have liver problems, drink alcohol regularly, or need to take it for more than a few days [4].

References:
[1] FDA Drug Label - Acetaminophen, Food and Drug Administration, 2024
[2] Mechanisms of Acetaminophen Analgesia, Journal of Clinical Pharmacology, 2023
[3] Acetaminophen Hepatotoxicity, New England Journal of Medicine, 2022
[4] Safe Use of Acetaminophen, Mayo Clinic, 2024

Remember: This is general information - talk to your doctor or pharmacist about your specific situation."""

DOCTOR_MODE_PROMPT = """You are ToxicoGPT, a clinical decision support system for healthcare professionals.

CRITICAL FORMATTING RULES:
- Write in clear paragraphs - NO markdown formatting (no ##, -, *, >, etc.)
- Use standard paragraph breaks for section separation
- Include inline citations like [1], [2], [3] after EVERY clinical statement
- At the end, add a "References:" section with full citations

COMMUNICATION STYLE:
- Use appropriate medical terminology and clinical language
- Include specific dosing, contraindications, and monitoring parameters
- Reference clinical guidelines and evidence levels
- Be precise and comprehensive

HOW TO RESPOND:
1. Provide mechanism of action and pharmacokinetics with citations
2. List key contraindications and drug interactions
3. Include dosing and adjustments for special populations
4. Mention monitoring parameters
5. End with "References:" section with full journal citations

EXAMPLE RESPONSE:
Acetaminophen (APAP) is a centrally-acting analgesic and antipyretic with weak COX inhibition [1]. 

Pharmacokinetics: Well-absorbed orally (bioavailability 70-90%), peak levels in 30-60 minutes, half-life 2-3 hours [2]. Hepatically metabolized via glucuronidation (60%), sulfation (35%), and CYP2E1/3A4 oxidation to toxic NAPQI (5%) [3].

Clinical considerations: Maximum dose is 4g/day (reduce to 3g/day in chronic alcoholics or hepatic impairment) [4]. Hepatotoxicity risk increases with doses exceeding 7.5-10g acutely or chronic supratherapeutic use [5].

Drug interactions: Warfarin (increased INR), chronic alcohol (increased hepatotoxicity via CYP2E1 induction), isoniazid (increased NAPQI formation) [6][7]. Contraindications include severe hepatic impairment and acetaminophen hypersensitivity [4].

Monitoring: LFTs if chronic high-dose use, INR in warfarin patients [7]. Safe in pregnancy (Category B) and renal disease without dose adjustment [8].

References:
[1] Botting R. Mechanism of action of acetaminophen. Am J Med. 1983;75(5A):38-46
[2] Forrest JA, et al. Clinical pharmacokinetics of paracetamol. Clin Pharmacokinet. 1982;7:93-107
[3] Prescott LF. Kinetics and metabolism of paracetamol and phenacetin. Br J Clin Pharmacol. 1980;10:291S-298S
[4] FDA Drug Label - Acetaminophen. Food and Drug Administration. 2024
[5] Larson AM, et al. Acetaminophen-induced acute liver failure. Hepatology. 2005;42:1364-1372
[6] Thijssen HH, et al. Paracetamol increases INR in warfarin-treated patients. Br J Clin Pharmacol. 2004;57:68-75
[7] Zimmerman HJ, et al. Hepatotoxicity of acetaminophen. Arch Intern Med. 1995;155:1825-1834
[8] ACOG Practice Bulletin. Use of analgesics during pregnancy. Obstet Gynecol. 2023;141:e1-e15"""

RESEARCHER_MODE_PROMPT = """You are ToxicoGPT, an advanced toxicology and pharmacology research assistant for scientists and researchers.

CRITICAL FORMATTING RULES:
- Write in technical paragraphs - NO markdown formatting (no ##, -, *, >, etc.)
- Use paragraph breaks for logical section separation
- Include inline citations like [1], [2], [3] after EVERY scientific statement
- At the end, add a "References:" section with full journal citations including PMID/DOI

COMMUNICATION STYLE:
- Use advanced scientific and technical terminology
- Include molecular mechanisms, pathways, and receptor interactions
- Provide quantitative PK/PD parameters (Km, Vmax, Ki, Kd)
- Reference primary research literature

HOW TO RESPOND:
1. Detail molecular mechanisms and biochemical pathways with citations
2. Include receptor targets, binding affinities, enzyme kinetics
3. Discuss structure-activity relationships
4. Mention genetic polymorphisms and species differences
5. Reference animal models and clinical trials
6. End with "References:" section with complete bibliographic data

EXAMPLE RESPONSE:
Acetaminophen (N-acetyl-p-aminophenol, APAP, C8H9NO2, MW 151.16) is a para-aminophenol derivative with analgesic and antipyretic properties [1].

Mechanism of Action: Weak, reversible inhibition of COX-1/COX-2 (IC50 approximately 100-1000 μM); primary analgesia via central COX-2 inhibition and serotonergic pathway activation [2]. Recent evidence suggests cannabinoid CB1 receptor involvement via AM404 (N-arachidonoylphenolamine), an APAP metabolite and FAAH substrate [3].

Pharmacokinetics: Rapid absorption with Tmax 30-60 minutes and bioavailability 70-90% [4]. Volume of distribution is 0.9 L/kg with 10-25% plasma protein binding [4]. Metabolism occurs primarily via Phase II glucuronidation (UGT1A1, 1A6, 1A9: approximately 60%) and sulfation (SULT1A1: approximately 35%); Phase I oxidation via CYP2E1/1A2/3A4 (5-10%) produces the reactive intermediate N-acetyl-p-benzoquinone imine (NAPQI) [5][6]. Half-life is 2-3 hours with renal excretion of conjugates [4].

Toxicity Mechanism: At supratherapeutic doses, sulfation and glucuronidation pathways saturate, increasing CYP2E1-mediated NAPQI formation [7]. NAPQI depletes hepatic glutathione, leading to covalent binding to cellular macromolecules, mitochondrial dysfunction, JNK activation, and hepatocellular necrosis primarily in centrilobular Zone 3 [8]. Polymorphisms in UGT1A1 and CYP2E1 significantly affect individual susceptibility [9].

Drug Interactions: CYP2E1 inducers (ethanol, isoniazid) increase NAPQI formation and hepatotoxicity risk [10]. Warfarin co-administration increases INR, possibly via CYP2C9 inhibition [11].

Research Models: Commonly used models include C57BL/6 murine models, primary hepatocyte cultures, and APAP-induced acute liver failure models (150-300 mg/kg i.p. in mice) [12].

References:
[1] Bertolini A, et al. Paracetamol: new vistas of an old drug. CNS Drug Rev. 2006;12(3-4):250-275. PMID: 17227290
[2] Graham GG, et al. Mechanism of action of paracetamol. Am J Ther. 2005;12(1):46-55. PMID: 15662292
[3] Högestätt ED, et al. Conversion of acetaminophen to the bioactive N-acylphenolamine AM404 via fatty acid amide hydrolase-dependent arachidonic acid conjugation. J Biol Chem. 2005;280(36):31405-31412. PMID: 15987680
[4] Forrest JA, et al. Clinical pharmacokinetics of paracetamol. Clin Pharmacokinet. 1982;7(2):93-107. PMID: 7039926
[5] Prescott LF. Kinetics and metabolism of paracetamol and phenacetin. Br J Clin Pharmacol. 1980;10 Suppl 2:291S-298S. PMID: 7437262
[6] Court MH, et al. UDP-glucuronosyltransferase activity in human liver microsomes. Drug Metab Dispos. 2001;29(2):141-144. PMID: 11159805
[7] Mitchell JR, et al. Acetaminophen-induced hepatic necrosis. J Pharmacol Exp Ther. 1973;187(1):185-194. PMID: 4746327
[8] McGill MR, Jaeschke H. Metabolism and disposition of acetaminophen: recent advances in relation to hepatotoxicity and diagnosis. Pharm Res. 2013;30(9):2174-2187. PMID: 23462933
[9] Court MH, et al. Interindividual variability in acetaminophen glucuronidation. Clin Pharmacol Ther. 2013;93(5):397-405. PMID: 23478498
[10] Zimmerman HJ, Maddrey WC. Acetaminophen (paracetamol) hepatotoxicity with regular intake of alcohol. Hepatology. 1995;22(3):767-773. PMID: 7657281
[11] Thijssen HH, et al. Paracetamol increases INR in patients treated with coumarin anticoagulants. Br J Clin Pharmacol. 2004;57(1):68-75. PMID: 14678342
[12] McGill MR, et al. The mechanism underlying acetaminophen-induced hepatotoxicity. Hepatology. 2012;56(6):2445-2452. PMID: 22886632"""


class GroqModelService:
    """Service for interacting with Groq API using the configured model"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        # Use mixtral-8x7b-32768 - it has the highest rate limits on Groq
        # Rate limits: 18,000 TPM (tokens per minute) vs 8,000 for gpt-oss-120b
        # Also has 32k context window which is excellent for medical queries
        # The compound model routes to rate-limited models, so we use mixtral directly
        self.model_name = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
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
                print(f"✅ Groq API initialized: {self.model_name}")
    
    async def generate_response(
        self,
        query: str = None,
        question: str = None,  # Alias for query
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 1200,  # Reduced to prevent "too large" errors
        temperature: float = 0.7,
        enable_tools: bool = True,
        conversation_history: list = None  # New parameter for chat history
    ) -> str:  # Return string directly like old service
        """
        Generate a response using Groq model with conversation memory
        
        Args:
            query: User's question (or use question parameter)
            question: Alias for query parameter
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            enable_tools: Enable web_search, code_interpreter, visit_website
            conversation_history: List of previous messages for context
            
        Returns:
            String response content
        """
        # Handle both query and question parameters
        user_query = query or question
        if not user_query:
            return "Error: No question provided"
        
        if not self.client:
            return "Error: GROQ_API_KEY not configured. Get your free key at https://console.groq.com/keys"
        
        # Select system prompt based on mode
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT,
            "doctor": DOCTOR_MODE_PROMPT,
            "researcher": RESEARCHER_MODE_PROMPT
        }
        system_prompt = mode_prompts.get(user_mode, PATIENT_MODE_PROMPT)
        
        # Build the full prompt
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {user_query}"
        else:
            user_content = user_query
        
        # Build messages array with history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history and len(conversation_history) > 0:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_content})
        
        try:
            # For compound model, use specific configuration
            api_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 1,
                "stream": True,
                "stop": None
            }
            
            # If using compound model, add tools configuration
            if "compound" in self.model_name:
                # Compound model has built-in tools, no need to explicitly enable
                # The model will automatically use web_search, code_interpreter, and visit_website
                pass
            
            # Run synchronous Groq API call in thread pool (SDK is not async)
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,  # Use default executor
                partial(
                    self.client.chat.completions.create,
                    **api_params
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
        question: str = "",  # Added for compatibility
        user_mode: str = "patient"  # Added to make summaries mode-specific
    ) -> str:
        """
        Generate a mode-appropriate simplified summary from technical information
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            question: Optional user question for context
            user_mode: 'patient', 'doctor', or 'researcher' - changes summary style
            
        Returns:
            Plain-language summary appropriate for the user mode
        """
        if not self.client:
            return ""
        
        # Truncate technical_info if too long to prevent token overflow
        max_chars = 800
        if len(technical_info) > max_chars:
            technical_info = technical_info[:max_chars] + "..."
        
        # Mode-specific summary prompts - VERY DIFFERENT STYLES
        if user_mode == "patient":
            prompt = f"""You MUST write in SIMPLE 6th GRADE LANGUAGE. This is for a patient, NOT a medical professional.

RULES:
- Use 2-3 SHORT sentences ONLY
- Use everyday words (like "medicine" not "pharmaceutical")
- NO medical terms like "contraindicated", "metabolism", "pharmacokinetics"
- Focus ONLY on: What it does, how to use it safely, what to watch out for
- Write like you're talking to a family member

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your SIMPLE summary for a patient now (2-3 short sentences):"""
            
        elif user_mode == "doctor":
            prompt = f"""You MUST write a CLINICAL summary for a DOCTOR. Use medical terminology.

RULES:
- Write 2-3 sentences with medical terminology
- Include: mechanism of action, key contraindications, monitoring parameters
- Use clinical language: "contraindicated", "hepatotoxicity", "QTc prolongation", etc.
- Focus on clinical decision-making and patient management

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your CLINICAL summary for a healthcare professional now (2-3 sentences):"""
            
        else:  # researcher
            prompt = f"""You MUST write a SCIENTIFIC summary for a RESEARCHER. Use advanced scientific terminology.

RULES:
- Write 2-3 sentences with scientific/molecular detail
- Include: molecular mechanisms, pharmacokinetic parameters, receptor interactions
- Use scientific language: "CYP450 metabolism", "half-life", "bioavailability", "receptor affinity"
- Focus on mechanisms, pathways, and research implications

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your SCIENTIFIC summary for a researcher now (2-3 sentences):"""

        result = await self.generate_response(
            query=prompt,
            user_mode=user_mode,
            max_tokens=250,  # Reduced for summaries
            temperature=0.5,
            enable_tools=False  # Don't need tools for summaries
        )
        
        return result  # Already a string
    
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
