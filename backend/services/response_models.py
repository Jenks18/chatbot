"""
Response Models for Structured LLM Output
Using Pydantic models with Instructor to enforce clean, consistent formatting
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Reference(BaseModel):
    """APA-style reference with complete bibliographic information"""
    number: int = Field(..., description="Reference number [1], [2], etc.")
    authors: str = Field(..., description="Complete author names in APA format: 'LastName, F. M.' or 'Organization Name'. For multiple authors: 'Smith, J., & Jones, A.' Use 'et al.' for 4+ authors.")
    title: str = Field(..., description="Complete article/document title")
    journal: str = Field(..., description="Full journal name or source (e.g., 'The New England Journal of Medicine', 'Food and Drug Administration')")
    year: int = Field(..., description="Publication year")
    volume_issue: Optional[str] = Field(None, description="Volume and issue in format: '380(25)' or just '380'")
    pages: Optional[str] = Field(None, description="Page range: '2440-2448' or article number: 'e2022897'")
    doi: Optional[str] = Field(None, description="DOI in format: '10.1056/NEJMra1807061'")
    pmid: Optional[str] = Field(None, description="PubMed ID number only: '31167055'")
    url: str = Field(..., description="REQUIRED: Full working URL - PubMed link https://pubmed.ncbi.nlm.nih.gov/[PMID]/ or official source URL")
    
    def format_citation(self) -> str:
        """Format reference in APA style with URL"""
        # APA format: Authors. (Year). Title. Journal, Volume(Issue), Pages. doi:XX.XXXX/XXXXX. URL
        citation = f"{self.authors}. ({self.year}). {self.title}. {self.journal}"
        
        if self.volume_issue:
            citation += f", {self.volume_issue}"
        if self.pages:
            citation += f", {self.pages}"
        citation += "."
        
        if self.doi:
            citation += f" doi:{self.doi}."
        
        if self.pmid:
            citation += f" PMID: {self.pmid}."
            
        citation += f" {self.url}"
        
        return citation


class ContentSection(BaseModel):
    """A section of content with proper formatting"""
    heading: Optional[str] = Field(None, description="Section heading in plain text (no markdown)")
    paragraphs: List[str] = Field(..., description="List of paragraphs, each as plain text with inline citations like [1], [2]")
    bullet_points: Optional[List[str]] = Field(None, description="Optional bullet points as plain list items with inline citations")
    
    
class StructuredResponse(BaseModel):
    """
    Main response model ensuring clean, professional formatting
    NO markdown symbols (**, ##, -, >, etc.)
    Proper paragraphs and bullet lists
    Working reference links
    """
    content_sections: List[ContentSection] = Field(
        ..., 
        description="Main content divided into logical sections with headings and paragraphs"
    )
    references: List[Reference] = Field(
        ..., 
        description="Complete list of references with working URLs, properly formatted"
    )
    tone: Literal["educational", "clinical", "research"] = Field(
        ..., 
        description="Response tone - educational for patients, clinical for doctors, research for scientists"
    )
    
    def to_plain_text(self) -> str:
        """Convert structured response to clean plain text"""
        output = []
        
        for section in self.content_sections:
            # Add heading if present (no markdown symbols)
            if section.heading:
                output.append(f"\n{section.heading}\n")
            
            # Add paragraphs
            for para in section.paragraphs:
                output.append(f"{para}\n")
            
            # Add bullet points with proper formatting
            if section.bullet_points:
                for bullet in section.bullet_points:
                    output.append(f"  • {bullet}")
                output.append("")  # Add spacing after bullets
        
    Professional, paragraph-based response for general audience
    NO emojis, NO bullet points, NO markdown
    """
    paragraphs: List[str] = Field(
        ..., 
        min_items=3,
        max_items=6,
        description="3-6 flowing paragraphs in clear, accessible language. Each paragraph is a complete unit with inline citations [1], [2-3] at the end of sentences. NO emojis. NO bullet points. NO markdown. Structure: (1) Definition/overview, (2) Mechanism/how it works, (3) Clinical uses/indications, (4) Safety/dosing, (5) Optional: Availability/formulations."
    )
    references: List[Reference] = Field(
        ..., 
        min_items=3,
        max_items=10,
        description="3-10 complete APA-style references with working PubMed or official source URLs. MUST include proper author names, full title, journal, year, volume/pages, DOI if available, and URL."
    )
    follow_up_question: Optional[str] = Field(
        None, 
        description="ONE brief, relevant follow-up question suggestion (optional)"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean plain text"""
        output = []
        
        # Add paragraphs with spacing
        for i, para in enumerate(self.paragraphs):
            output.append(para)
            if i < len(self.paragraphs) - 1:
                output.append("")  # Blank line between paragraphs
        
        # Add follow-up question if present
        if self.follow_up_question:
            output.append("")
            output.append(self.follow_up_question)
        
        # Add references
        if self.references:
            output.append("")
            output.append("References:")
            for ref in self.references:
                output.append(f"[{ref.number}] {ref.format_citation()
            for point in self.key_points:
    Professional clinical response in paragraph format
    NO bullet points unless absolutely critical for safety warnings
    """
    paragraphs: List[str] = Field(
        ..., 
        min_items=4,
        max_items=7,
        description="4-7 clinical paragraphs using appropriate medical terminology. Inline citations [1], [2-4] at sentence ends. Structure: (1) Clinical overview/drug class, (2) Mechanism of action with pharmacology, (3) Dosing/administration/efficacy, (4) Safety profile and adverse effects, (5) Drug interactions if relevant, (6) Special populations if applicable. NO bullet points - integrate all information into flowing prose."
    )
    references: List[Reference] = Field(
        ..., 
        min_items=4,
        max_items=15,
        description="4-15 complete APA-style clinical references with PubMed URLs. Must include authors, title, journal, year, volume/pages, PMID, DOI, and URL."
    )
    clinical_question: Optional[str] = Field(
        None, 
        description="Optional forward-looking clinical question or guideline reference"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean plain text"""
        output = []
        
        # Add paragraphs
        for i, para in enumerate(self.paragraphs):
            output.append(para)
            if i < len(self.paragraphs) - 1:
                output.append("")
        
        # Add clinical question if present
        if self.clinical_question:
            output.append("")
            output.append(self.clinical_question)
        
        # Add references
        if self.references:
            output.append("")
            output.append("ext format"""
        output = [self.clinical_summary, "\n"]
        
        if self.safety_considerations:
            output.append("\nSafety Considerations:")
            for item in self.safety_considerations:
                output.append(f"  • {item}")
    Dense, technical research analysis in paragraph format
    """
    paragraphs: List[str] = Field(
        ..., 
        min_items=5,
        max_items=10,
        description="5-10 dense, technical paragraphs with advanced scientific terminology. Frequent inline citations [1-4]. Include quantitative data (IC50, HR, p-values). Structure: (1) Drug class overview/molecular target, (2) Detailed pharmacology/mechanism, (3) Clinical trial data/efficacy endpoints, (4) Safety profile with mechanistic basis, (5) Drug interactions/PK considerations, (6) Special populations/genetic polymorphisms, (7) Comparative effectiveness if relevant. NO bullet points."
    )
    references: List[Reference] = Field(
        ..., 
        min_items=5,
        max_items=20,
        description="5-20 complete academic references in APA style. MUST include full author lists (or et al.), complete title, full journal name, year, volume(issue), pages, DOI, PMID, and PubMed URL."
    )
    research_question: Optional[str] = Field(
        None, 
        description="Optional analytical follow-up or research gap identification"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean plain text"""
        output = []
        
        # Add paragraphs
        for i, para in enumerate(self.paragraphs):
            output.append(para)
            if i < len(self.paragraphs) - 1:
                output.append("")
        
        # Add research question if present
        if self.research_question:
            output.append("")
            output.append(self.research_question)
        
        # Add references
        if self.references:
            output.append("")
            output.append("ndings or insights with citations"
    )
    references: List[Reference] = Field(
        ..., 
        description="Complete, properly formatted academic references with DOIs/PMIDs and URLs"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean text format"""
        output = [self.analysis, "\n"]
        
        if self.key_findings:
            output.append("\nKey Findings:")
            for finding in self.key_findings:
                output.append(f"  • {finding}")
            output.append("")
        
        if self.references:
            output.append("\nReferences:")
            for ref in self.references:
                output.append(f"[{ref.number}] {ref.format_citation()}")
        
        return "\n".join(output)
