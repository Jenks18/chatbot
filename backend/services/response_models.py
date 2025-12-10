"""
Response Models for Structured LLM Output
Using Pydantic models with Instructor to enforce clean, consistent formatting
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Reference(BaseModel):
    """A properly formatted reference with working links"""
    number: int = Field(..., description="Reference number for citation")
    authors: str = Field(..., description="Author names (e.g., 'Smith et al.' or 'FDA')")
    title: str = Field(..., description="Full title of the source")
    journal: str = Field(..., description="Journal name or source (e.g., 'New England Journal of Medicine' or 'FDA Drug Label')")
    year: int = Field(..., description="Publication year")
    volume_pages: Optional[str] = Field(None, description="Volume and page numbers if applicable (e.g., '10(2):123-456')")
    pmid: Optional[str] = Field(None, description="PubMed ID if available")
    doi: Optional[str] = Field(None, description="DOI if available")
    url: Optional[str] = Field(None, description="Full working URL to the source")

    def format_citation(self) -> str:
        """Format reference in standard citation style"""
        citation = f"{self.authors}. {self.title}. {self.journal}. {self.year}"
        if self.volume_pages:
            citation += f";{self.volume_pages}"
        if self.pmid:
            citation += f". PMID: {self.pmid}"
        if self.doi:
            citation += f". DOI: {self.doi}"
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
        
        # Add references section
        if self.references:
            output.append("\nReferences:")
            for ref in self.references:
                output.append(f"[{ref.number}] {ref.format_citation()}")
        
        return "\n".join(output)


class PatientResponse(BaseModel):
    """
    Response format for patient mode - simple, educational, non-assumptive
    """
    main_content: str = Field(
        ..., 
        description="Educational explanation in simple 6th-grade language. Use clear paragraphs. Include inline citations [1], [2]. NO assumptions about the patient's health. Present neutral facts."
    )
    key_points: List[str] = Field(
        ..., 
        description="3-5 key takeaway points as plain text bullet items with citations. Start each with a relevant emoji."
    )
    references: List[Reference] = Field(
        ..., 
        description="Complete, properly formatted references with working URLs"
    )
    next_question_suggestion: Optional[str] = Field(
        None, 
        description="Helpful follow-up question they might want to ask (not assumptive)"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean text format"""
        output = [self.main_content, "\n"]
        
        if self.key_points:
            output.append("\nKey Points:")
            for point in self.key_points:
                output.append(f"  • {point}")
            output.append("")
        
        if self.references:
            output.append("\nReferences:")
            for ref in self.references:
                output.append(f"[{ref.number}] {ref.format_citation()}")
        
        if self.next_question_suggestion:
            output.append(f"\n{self.next_question_suggestion}")
        
        return "\n".join(output)


class ClinicalResponse(BaseModel):
    """
    Response format for clinical/doctor mode - technical, evidence-based
    """
    clinical_summary: str = Field(
        ..., 
        description="Clinical overview with medical terminology. Use paragraphs with inline citations [1], [2]."
    )
    safety_considerations: List[str] = Field(
        ..., 
        description="Critical safety points for clinical decision-making with citations"
    )
    monitoring_parameters: Optional[List[str]] = Field(
        None, 
        description="Specific monitoring parameters if applicable"
    )
    references: List[Reference] = Field(
        ..., 
        description="Complete, properly formatted references with working URLs"
    )
    
    def to_plain_text(self) -> str:
        """Convert to clean text format"""
        output = [self.clinical_summary, "\n"]
        
        if self.safety_considerations:
            output.append("\nSafety Considerations:")
            for item in self.safety_considerations:
                output.append(f"  • {item}")
            output.append("")
        
        if self.monitoring_parameters:
            output.append("\nMonitoring Parameters:")
            for param in self.monitoring_parameters:
                output.append(f"  • {param}")
            output.append("")
        
        if self.references:
            output.append("\nReferences:")
            for ref in self.references:
                output.append(f"[{ref.number}] {ref.format_citation()}")
        
        return "\n".join(output)


class ResearchResponse(BaseModel):
    """
    Response format for research mode - detailed, analytical
    """
    analysis: str = Field(
        ..., 
        description="Detailed analytical content in technical paragraphs with inline citations [1], [2]"
    )
    key_findings: List[str] = Field(
        ..., 
        description="Major findings or insights with citations"
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
