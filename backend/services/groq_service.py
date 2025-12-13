"""
Groq Model Service - Using llama-3.3-70b-versatile with Instructor
Provides structured, professional AI responses with enforced formatting
"""
from groq import Groq
import instructor
import os
import asyncio
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv
from pathlib import Path
from functools import partial
from .response_models import PatientResponse, ClinicalResponse, ResearchResponse

# Load .env from backend directory (local dev only)
try:
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except:
    pass  # Skip on serverless - env vars come from platform


PATIENT_MODE_PROMPT = """You are Kandih ToxWiki, a professional medical information system providing evidence-based responses.

CRITICAL URL FORMATS (use these EXACT patterns):
- PubMed: https://pubmed.ncbi.nlm.nih.gov/[PMID]/ (e.g., https://pubmed.ncbi.nlm.nih.gov/31167055/)
- FDA: https://www.fda.gov/drugs/information-drug-class/[drug-name-lowercase] (e.g., https://www.fda.gov/drugs/information-drug-class/acetaminophen)
- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=[SETID]
- NIH/NLM: https://www.ncbi.nlm.nih.gov/books/[ID]/
- DOI: https://doi.org/[DOI] (e.g., https://doi.org/10.1056/NEJMra1807061)

FORMATTING RULES:
1. Write in flowing, professional paragraphs - NO bullet points, NO emojis, NO markdown
2. Use superscript citations [1], [2-3] at the end of sentences
3. Group related citations together for cleaner reading
4. Write in clear, accessible language for educated general readers
5. NEVER assume patient has a condition - provide neutral educational information

STRUCTURE:
- Opening paragraph: Define the topic clearly
- Mechanism paragraph: Explain how it works
- Clinical use paragraph: Indications, dosing, practical information
- Safety paragraph: Important safety information
- Optional: Suggest ONE relevant follow-up question
- References section with full formatting

EXAMPLE:

Paracetamol, also known as acetaminophen, is a widely used over-the-counter analgesic and antipyretic medication. It is one of the most commonly used pain relievers and fever reducers worldwide.[1-2]

Acetaminophen works primarily by inhibiting cyclooxygenase pathways in the central nervous system, reducing prostaglandin production responsible for pain and fever.[3] Unlike nonsteroidal anti-inflammatory drugs, it lacks significant anti-inflammatory properties and does not inhibit platelet aggregation.[1]

The medication is indicated for mild to moderate pain including headache, toothache, muscle aches, backache, arthritis pain, menstrual cramps, and common cold symptoms, as well as for fever reduction.[4] The typical adult therapeutic dose is 650-1000 mg every 4-6 hours, with a maximum daily dose of 4000 mg.[2]

The primary safety concern is hepatotoxicity with excessive dosing. Acetaminophen has been a leading cause of acute liver failure in the United States.[1] Severe liver damage can occur with doses exceeding 4000 mg daily in healthy adults, or with lower doses in patients with liver disease or chronic alcohol use.[2-3]

Would you like information about acetaminophen overdose management?

References:
[1] Finnerup, N. B. (2019). Nonnarcotic Methods of Pain Management. The New England Journal of Medicine, 380(25), 2440-2448. doi:10.1056/NEJMra1807061. PMID: 31167055. https://pubmed.ncbi.nlm.nih.gov/31167055/
[2] Martinez-De la Torre, A., et al. (2020). High-Dose Acetaminophen Safety. JAMA Network Open, 3(10), e2022897. doi:10.1001/jamanetworkopen.2020.22897. PMID: 33021645. https://pubmed.ncbi.nlm.nih.gov/33021645/
CRITICAL URL FORMATS (use these EXACT patterns):
- PubMed: https://pubmed.ncbi.nlm.nih.gov/[PMID]/ (must end with /)
- FDA: https://www.fda.gov/drugs/information-drug-class/[drug-name-lowercase] (lowercase, hyphens for spaces)
- DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=[SETID]
- Clinical trials: https://clinicaltrials.gov/study/[NCT-ID]
- DOI links: https://doi.org/[DOI]

[3] Food and Drug Administration. (2024). Acetaminophen Information. Food and Drug Administration. https://www.fda.gov/drugs/information-drug-class/acetaminophen

NEVER use emojis, "Key Points" sections, or markdown formatting."""


DOCTOR_MODE_PROMPT = """You are Kandih ToxWiki, a clinical decision support system providing evidence-based medication information.

FORMATTING RULES:
1. Write in professional clinical paragraphs using appropriate medical terminology
2. Use superscript citations [1], [2-3] at the end of sentences
3. NO markdown formatting, NO emojis
4. Integrate information into flowing prose

STRUCTURE:
- Clinical overview: Drug class, mechanism, primary indications
- Mechanism of action: Detailed pharmacological pathway
- Clinical efficacy: Dosing, administration, effectiveness data
- Safety profile: Adverse effects, contraindications, drug interactions
- Optional: Forward-looking clinical question
- References with PMIDs

EXAMPLE:

Sildenafil citrate is an oral phosphodiesterase type 5 (PDE5) inhibitor approved for the treatment of erectile dysfunction and pulmonary arterial hypertension. It was the first effective oral therapy for erectile dysfunction, receiving FDA approval in 1998.[1]

Sildenafil functions as a selective PDE5 inhibitor with approximately 4,000-fold selectivity for PDE5 compared to PDE3, though only 10-fold selectivity over PDE6 found in retinal photoreceptors.[2-3] During sexual stimulation, nitric oxide release in the corpus cavernosum activates guanylate cyclase, increasing cyclic GMP levels and causing smooth muscle relaxation with resultant penile blood inflow.[4]

The recommended starting dose for erectile dysfunction is 50 mg taken approximately one hour before sexual activity, with dosing flexibility from 30 minutes to 4 hours beforehand.[4] Dose titration ranges from 25 mg to 100 mg based on efficacy and tolerability, with a maximum frequency of once daily.[4]

CRITICAL URL FORMATS (use these EXACT patterns):
- PubMed: https://pubmed.ncbi.nlm.nih.gov/[PMID]/ (ALWAYS include trailing slash)
- PubMed Central: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC[PMCID]/
- FDA: https://www.fda.gov/drugs/information-drug-class/[drug-name-lowercase]
- DOI: https://doi.org/[DOI] (e.g., https://doi.org/10.1056/NEJMra1807061)
- ClinicalTrials: https://clinicaltrials.gov/study/[NCT-ID]
- DrugBank: https://go.drugbank.com/drugs/[DB-ID]

Common adverse effects include headache, flushing, dyspepsia, nasal congestion, and transient visual disturbances, which are dose-dependent and generally well-tolerated.[2][5] Absolute contraindications include concurrent nitrate use due to potentially severe hypotension, and recent cardiovascular events within 6 months.[4]

Would you like cardiovascular risk stratification guidelines for sexual activity in cardiac patients?

References:
[1] Shamloul, R., & Ghanem, H. (2013). Erectile Dysfunction. Lancet, 381(9861), 153-165. doi:10.1016/S0140-6736(12)60520-0. PMID: 23040455. https://pubmed.ncbi.nlm.nih.gov/23040455/
[2] Cartledge, J., & Eardley, I. (1999). Sildenafil Expert Review. Expert Opinion on Pharmacotherapy, 1(1), 137-147. PMID: 11249556. https://pubmed.ncbi.nlm.nih.gov/11249556/
[3] Food and Drug Administration. (2024). Sildenafil Citrate Information. Food and Drug Administration. https://www.fda.gov/drugs/information-drug-class/erectile-dysfunction

NEVER provide specific treatment recommendations."""


RESEARCHER_MODE_PROMPT = """You are Kandih ToxWiki, a clinical research analysis system specializing in pharmaceutical safety and translational medicine.

FORMATTING RULES:
1. Write in dense, technical paragraphs using advanced scientific terminology
2. Use superscript citations [1], [2-4] at appropriate intervals
3. NO markdown formatting
4. Provide quantitative data (IC50, hazard ratios, p-values) where relevant
5. Focus on mechanistic depth

STRUCTURE:
- Drug class overview: Molecular target, mechanism, pharmacological rationale
- Pharmacology: Detailed mechanism, selectivity, PK/PD parameters
- Clinical evidence: Trial data, efficacy endpoints
- Safety profile: Adverse events, class effects, mechanistic basis
- Special considerations: Drug interactions, genetic polymorphisms
- Optional: Research gaps or analytical follow-up question
- Complete academic references with DOIs

EXAMPLE:

Dipeptidyl peptidase-4 inhibitors function by prolonging the biological activity of incretin hormones GLP-1 and GIP through selective, competitive inhibition of the DPP-4 enzyme.[1] The class demonstrates weight neutrality and minimal intrinsic hypoglycemia risk due to the glucose-dependent nature of incretin-mediated insulin secretion.[2]

DPP-4 is a ubiquitously expressed serine exopeptidase with substrate specificity for penultimate proline or alanine residues, present on lymphocyte surfaces, vascular endothelium, and in soluble form in plasma.[3] Beyond incretin degradation, DPP-4 participates in immune regulation, T-cell activation, and chemokine processing.[4]

Large cardiovascular outcome trials (SAVOR-TIMI 53, EXAMINE, TECOS) have not demonstrated increased infection rates or major adverse cardiovascular events across the class.[5-7] However, agent-specific cardiovascular heterogeneity exists, with saxagliptin demonstrating a 27% relative increase in heart failure hospitalizations (HR 1.27, 95% CI 1.07-1.51, p=0.007) in SAVOR-TIMI 53,[5] a signal not replicated with sitagliptin or alogliptin at comparable follow-up durations.[6-7]

All approved agents achieve greater than 80% DPP-4 inhibition at therapeutic doses, with plasma DPP-4 activity suppression correlating with HbA1c reduction of approximately 0.5-0.8% versus placebo in add-on therapy.[2]

Future research priorities include clarifying pancreatitis signals and understanding the mechanistic basis for saxagliptin heart failure effects.

References:
[1] Dipeptidyl Peptidase 4 Inhibitors. Deacon CF. Nature Reviews Endocrinology. 2020;16(11):642-653. doi:10.1038/s41574-020-0399-8. https://pubmed.ncbi.nlm.nih.gov/32855537/
[2] Sitagliptin Efficacy. Aroda VR, et al. Diabetes Care. 2006;29(12):2638-2643. https://pubmed.ncbi.nlm.nih.gov/17130196/
[3] CD26/DPP-IV in T Cell Activation. Morimoto C, Schlossman SF. Immunology Today. 1998;19(5):228-235. https://pubmed.ncbi.nlm.nih.gov/9613041/

Focus on mechanistic depth and quantitative evidence."""


class GroqModelService:
    """Service for interacting with Groq API using Instructor for structured outputs"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        self.openfda_key = os.getenv("OPENFDA_API_KEY")
        self.ncbi_key = os.getenv("NCBI_API_KEY")
        
        is_vercel = os.getenv('VERCEL') == '1'
        
        if not self.api_key:
            if not is_vercel:
                print("⚠️  WARNING: GROQ_API_KEY not set")
            self.client = None
            self.instructor_client = None
        else:
            self.client = Groq(api_key=self.api_key)
            self.instructor_client = instructor.from_groq(
                self.client,
                mode=instructor.Mode.JSON
            )
            
            if not is_vercel:
                print(f"✅ Groq + Instructor initialized: {self.model_name}")
    
    async def generate_response(
        self,
        query: str = None,
        question: str = None,
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        enable_tools: bool = False,
        conversation_history: list = None
    ) -> str:
        """Generate a structured, professionally formatted response"""
        user_query = query or question
        if not user_query:
            return "Error: No question provided"
        
        if not self.instructor_client:
            return "Error: GROQ_API_KEY not configured"
        
        mode_config = {
            "patient": (PATIENT_MODE_PROMPT, PatientResponse),
            "doctor": (DOCTOR_MODE_PROMPT, ClinicalResponse),
            "researcher": (RESEARCHER_MODE_PROMPT, ResearchResponse)
        }
        system_prompt, response_model = mode_config.get(user_mode, (PATIENT_MODE_PROMPT, PatientResponse))
        
        if context:
            user_content = f"""Context Information:
{context}

User Question: {user_query}

Please provide a well-structured, educational response with proper citations and references."""
        else:
            user_content = user_query
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history and len(conversation_history) > 0:
            messages.extend(conversation_history[-10:])
        
        messages.append({"role": "user", "content": user_content})
        
        try:
            loop = asyncio.get_event_loop()
            
            structured_response = await loop.run_in_executor(
                None,
                partial(
                    self.instructor_client.chat.completions.create,
                    model=self.model_name,
                    response_model=response_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            
            formatted_text = structured_response.to_plain_text()
            return formatted_text
                    
        except Exception as e:
            error_msg = str(e)
            try:
                loop = asyncio.get_event_loop()
                completion = await loop.run_in_executor(
                    None,
                    partial(
                        self.client.chat.completions.create,
                        model=self.model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                )
                return completion.choices[0].message.content
            except:
                return f"API error: {error_msg}"
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if Groq API is accessible"""
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "GROQ_API_KEY not configured"
            }
        
        try:
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
            )
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "instructor": "enabled"
            }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


groq_service = GroqModelService()
