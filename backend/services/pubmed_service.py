"""
PubMed API Service - Query real articles from NCBI PubMed
"""
import os
import requests
from typing import List, Dict, Optional
from xml.etree import ElementTree as ET


class PubMedService:
    """Service for querying PubMed API and getting real article metadata"""
    
    def __init__(self):
        self.api_key = os.getenv("NCBI_API_KEY", "")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = os.getenv("NCBI_EMAIL", "toxwiki@example.com")
    
    def search_articles(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search PubMed and return list of PMIDs
        
        Args:
            query: Search query (e.g., "acetaminophen toxicity")
            max_results: Maximum number of results to return
            
        Returns:
            List of PMIDs as strings
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/esearch.fcgi",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            pmids = data.get("esearchresult", {}).get("idlist", [])
            return pmids
        except Exception as e:
            print(f"[PUBMED] Search failed: {e}")
            return []
    
    def fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch detailed metadata for list of PMIDs
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of article dictionaries with metadata
        """
        if not pmids:
            return []
        
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/efetch.fcgi",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            articles = []
            
            for article_elem in root.findall(".//PubmedArticle"):
                article = self._parse_article_xml(article_elem)
                if article:
                    articles.append(article)
            
            return articles
        except Exception as e:
            print(f"[PUBMED] Fetch failed: {e}")
            return []
    
    def _parse_article_xml(self, article_elem) -> Optional[Dict]:
        """Parse XML element into article dictionary"""
        try:
            medline = article_elem.find(".//MedlineCitation")
            article_node = medline.find(".//Article")
            
            # Get PMID
            pmid = medline.find(".//PMID").text
            
            # Get title
            title_elem = article_node.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "No title"
            
            # Get authors
            authors = []
            author_list = article_node.find(".//AuthorList")
            if author_list is not None:
                for author in author_list.findall(".//Author")[:3]:  # First 3 authors
                    lastname = author.find(".//LastName")
                    forename = author.find(".//ForeName")
                    initials = author.find(".//Initials")
                    
                    if lastname is not None:
                        if initials is not None:
                            authors.append(f"{lastname.text}, {initials.text}")
                        elif forename is not None:
                            authors.append(f"{lastname.text}, {forename.text[0]}")
                        else:
                            authors.append(lastname.text)
                
                # Add et al. if more than 3 authors
                if len(author_list.findall(".//Author")) > 3:
                    authors.append("et al.")
            
            author_string = ", ".join(authors) if authors else "Unknown authors"
            
            # Get journal
            journal_elem = article_node.find(".//Journal")
            journal_title = "Unknown journal"
            volume = None
            issue = None
            year = None
            pages = None
            
            if journal_elem is not None:
                journal_title_elem = journal_elem.find(".//Title")
                if journal_title_elem is not None:
                    journal_title = journal_title_elem.text
                
                # Get publication date
                pub_date = journal_elem.find(".//PubDate")
                if pub_date is not None:
                    year_elem = pub_date.find(".//Year")
                    if year_elem is not None:
                        year = year_elem.text
                
                # Get volume/issue
                issue_node = journal_elem.find(".//JournalIssue")
                if issue_node is not None:
                    vol_elem = issue_node.find(".//Volume")
                    if vol_elem is not None:
                        volume = vol_elem.text
                    
                    issue_elem = issue_node.find(".//Issue")
                    if issue_elem is not None:
                        issue = issue_elem.text
            
            # Get pagination
            pagination = article_node.find(".//Pagination/MedlinePgn")
            if pagination is not None:
                pages = pagination.text
            
            # Get DOI
            doi = None
            article_ids = article_elem.findall(".//ArticleId")
            for aid in article_ids:
                if aid.get("IdType") == "doi":
                    doi = aid.text
                    break
            
            # Build volume/issue string
            volume_issue = None
            if volume:
                if issue:
                    volume_issue = f"{volume}({issue})"
                else:
                    volume_issue = volume
            
            return {
                "pmid": pmid,
                "title": title,
                "authors": author_string,
                "journal": journal_title,
                "year": int(year) if year else None,
                "volume_issue": volume_issue,
                "pages": pages,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
        except Exception as e:
            print(f"[PUBMED] Parse error: {e}")
            return None
    
    def get_references_for_topic(self, topic: str, max_refs: int = 6) -> List[Dict]:
        """
        Get real PubMed references for a topic
        
        Args:
            topic: Medical topic or drug name
            max_refs: Maximum number of references to return
            
        Returns:
            List of formatted reference dictionaries
        """
        # Search PubMed
        pmids = self.search_articles(topic, max_results=max_refs)
        
        if not pmids:
            return []
        
        # Fetch article details
        articles = self.fetch_article_details(pmids)
        
        # Format for use in responses
        references = []
        for i, article in enumerate(articles, start=1):
            if article:
                references.append({
                    "number": i,
                    "pmid": article["pmid"],
                    "authors": article["authors"],
                    "title": article["title"],
                    "journal": article["journal"],
                    "year": article["year"],
                    "volume_issue": article.get("volume_issue"),
                    "pages": article.get("pages"),
                    "doi": article.get("doi"),
                    "url": article["url"]
                })
        
        return references


# Global instance
pubmed_service = PubMedService()
