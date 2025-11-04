"""
Drug Data Aggregator Service
Fetches and aggregates drug information from multiple FREE public APIs:
- RxNorm (NLM)
- FDA DailyMed
- PubChem
- OpenFDA
- PubMed E-utilities
"""

import httpx
import asyncio
import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import APICache
import xml.etree.ElementTree as ET

# API Keys from environment
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY", "")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

# Cache duration
CACHE_DURATION_DAYS = int(os.getenv("API_CACHE_DURATION_DAYS", "30"))


class DrugDataAggregator:
    """Aggregates drug data from multiple FREE public APIs"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.cache_duration = timedelta(days=CACHE_DURATION_DAYS)
        self.timeout = 30.0
    
    async def get_comprehensive_drug_data(self, drug_name: str) -> Dict:
        """
        Get complete drug data by querying multiple APIs in parallel
        Returns aggregated data from all sources
        """
        print(f"[DrugDataAggregator] Fetching comprehensive data for: {drug_name}")
        
        # Run all API calls concurrently for speed
        results = await asyncio.gather(
            self.get_rxnorm_data(drug_name),
            self.get_fda_label(drug_name),
            self.get_pubchem_data(drug_name),
            self.get_drug_interactions(drug_name),
            self.get_adverse_events(drug_name),
            self.get_pubmed_studies(drug_name, limit=5),
            return_exceptions=True  # Don't fail if one API is down
        )
        
        rxnorm, fda, pubchem, interactions, adverse_events, literature = results
        
        # Handle exceptions gracefully
        def safe_result(result, default=None):
            return result if not isinstance(result, Exception) else default
        
        aggregated_data = {
            "drug_name": drug_name,
            "timestamp": datetime.now().isoformat(),
            "identifiers": safe_result(rxnorm, {}),
            "fda_label": safe_result(fda, {}),
            "chemical_data": safe_result(pubchem, {}),
            "interactions": safe_result(interactions, []),
            "adverse_events": safe_result(adverse_events, []),
            "literature": safe_result(literature, [])
        }
        
        print(f"[DrugDataAggregator] Successfully aggregated data for: {drug_name}")
        return aggregated_data
    
    async def get_multiple_drugs_data(self, drug_names: List[str]) -> List[Dict]:
        """Get data for multiple drugs in parallel"""
        tasks = [self.get_comprehensive_drug_data(drug) for drug in drug_names]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_rxnorm_data(self, drug_name: str) -> Dict:
        """
        Query RxNorm API for drug identifiers and basic info
        API Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/
        """
        cache_key = f"rxnorm_{drug_name.lower()}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get RxCUI (RxNorm Concept Unique Identifier)
                response = await client.get(
                    f"https://rxnav.nlm.nih.gov/REST/rxcui.json",
                    params={"name": drug_name}
                )
                data = response.json()
                
                if data.get("idGroup", {}).get("rxnormId"):
                    rxcui = data["idGroup"]["rxnormId"][0]
                    
                    # Get detailed drug properties
                    props_response = await client.get(
                        f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json"
                    )
                    props_data = props_response.json()
                    
                    properties = props_data.get("properties", {})
                    
                    result = {
                        "rxcui": rxcui,
                        "name": properties.get("name", drug_name),
                        "synonym": properties.get("synonym", ""),
                        "tty": properties.get("tty", ""),  # Term type
                        "source": "RxNorm"
                    }
                    
                    self._save_to_cache(cache_key, result)
                    return result
                
                return {"error": "Drug not found in RxNorm"}
                
        except Exception as e:
            print(f"[RxNorm Error] {drug_name}: {str(e)}")
            return {"error": str(e)}
    
    async def get_fda_label(self, drug_name: str) -> Dict:
        """
        Query FDA DailyMed for official drug label
        API Docs: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
        """
        cache_key = f"fda_{drug_name.lower()}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search for drug
                response = await client.get(
                    "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json",
                    params={"drug_name": drug_name}
                )
                data = response.json()
                
                if data.get("data") and len(data["data"]) > 0:
                    first_result = data["data"][0]
                    setid = first_result.get("setid")
                    
                    result = {
                        "setid": setid,
                        "title": first_result.get("title", ""),
                        "manufacturer": first_result.get("author", ""),
                        "generic_name": first_result.get("generic_name", ""),
                        "published_date": first_result.get("published_date", ""),
                        "source": "FDA DailyMed",
                        "url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"
                    }
                    
                    self._save_to_cache(cache_key, result)
                    return result
                
                return {"error": "Drug label not found"}
                
        except Exception as e:
            print(f"[FDA DailyMed Error] {drug_name}: {str(e)}")
            return {"error": str(e)}
    
    async def get_pubchem_data(self, drug_name: str) -> Dict:
        """
        Query PubChem for chemical and toxicity data
        API Docs: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest
        """
        cache_key = f"pubchem_{drug_name.lower()}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get compound CID (Compound ID)
                cid_response = await client.get(
                    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
                )
                cid_data = cid_response.json()
                
                if cid_data.get("IdentifierList", {}).get("CID"):
                    cid = cid_data["IdentifierList"]["CID"][0]
                    
                    # Get properties
                    props_response = await client.get(
                        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChI,InChIKey/JSON"
                    )
                    props_data = props_response.json()
                    props = props_data["PropertyTable"]["Properties"][0]
                    
                    result = {
                        "cid": cid,
                        "molecular_formula": props.get("MolecularFormula"),
                        "molecular_weight": props.get("MolecularWeight"),
                        "smiles": props.get("CanonicalSMILES"),
                        "inchi": props.get("InChI"),
                        "inchi_key": props.get("InChIKey"),
                        "source": "PubChem",
                        "url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                    }
                    
                    self._save_to_cache(cache_key, result)
                    return result
                
                return {"error": "Compound not found in PubChem"}
                
        except Exception as e:
            print(f"[PubChem Error] {drug_name}: {str(e)}")
            return {"error": str(e)}
    
    async def get_drug_interactions(self, drug_name: str) -> List[Dict]:
        """
        Query RxNorm interaction API for known drug-drug interactions
        """
        # First get RxCUI
        rxnorm_data = await self.get_rxnorm_data(drug_name)
        if not rxnorm_data.get("rxcui"):
            return []
        
        rxcui = rxnorm_data["rxcui"]
        cache_key = f"interactions_{rxcui}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json",
                    params={"rxcui": rxcui}
                )
                data = response.json()
                
                interactions = []
                if data.get("interactionTypeGroup"):
                    for group in data["interactionTypeGroup"]:
                        for interaction_type in group.get("interactionType", []):
                            for pair in interaction_type.get("interactionPair", []):
                                interactions.append({
                                    "interacting_drug": pair["interactionConcept"][1]["minConceptItem"]["name"],
                                    "description": pair.get("description", ""),
                                    "severity": pair.get("severity", "unknown"),
                                    "source": "RxNorm"
                                })
                
                self._save_to_cache(cache_key, interactions)
                return interactions
                
        except Exception as e:
            print(f"[RxNorm Interactions Error] {drug_name}: {str(e)}")
            return []
    
    async def get_adverse_events(self, drug_name: str) -> List[Dict]:
        """
        Query OpenFDA for adverse event data
        API Docs: https://open.fda.gov/apis/drug/event/
        """
        cache_key = f"adverse_{drug_name.lower()}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build API URL with optional API key
                params = {
                    "search": f'patient.drug.openfda.generic_name:"{drug_name}"',
                    "count": "patient.reaction.reactionmeddrapt.exact",
                    "limit": 20
                }
                if OPENFDA_API_KEY:
                    params["api_key"] = OPENFDA_API_KEY
                
                response = await client.get(
                    "https://api.fda.gov/drug/event.json",
                    params=params
                )
                data = response.json()
                
                events = []
                if data.get("results"):
                    for result in data["results"]:
                        events.append({
                            "reaction": result.get("term", ""),
                            "count": result.get("count", 0),
                            "source": "OpenFDA"
                        })
                
                self._save_to_cache(cache_key, events)
                return events
                
        except Exception as e:
            print(f"[OpenFDA Error] {drug_name}: {str(e)}")
            return []
    
    async def get_pubmed_studies(self, drug_name: str, limit: int = 5) -> List[Dict]:
        """
        Query PubMed E-utilities for recent research
        API Docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/
        """
        cache_key = f"pubmed_{drug_name.lower()}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search PubMed
                search_params = {
                    "db": "pubmed",
                    "term": f"{drug_name} AND drug interactions",
                    "retmode": "json",
                    "retmax": limit,
                    "sort": "relevance"
                }
                if NCBI_API_KEY:
                    search_params["api_key"] = NCBI_API_KEY
                
                search_response = await client.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params=search_params
                )
                search_data = search_response.json()
                
                pmids = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    return []
                
                # Fetch article summaries
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "json"
                }
                if NCBI_API_KEY:
                    summary_params["api_key"] = NCBI_API_KEY
                
                summary_response = await client.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    params=summary_params
                )
                summary_data = summary_response.json()
                
                articles = []
                if summary_data.get("result"):
                    for pmid in pmids:
                        if pmid in summary_data["result"]:
                            article_data = summary_data["result"][pmid]
                            articles.append({
                                "pmid": pmid,
                                "title": article_data.get("title", ""),
                                "authors": [author.get("name", "") for author in article_data.get("authors", [])[:3]],
                                "journal": article_data.get("source", ""),
                                "publication_date": article_data.get("pubdate", ""),
                                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                "source": "PubMed"
                            })
                
                self._save_to_cache(cache_key, articles)
                return articles
                
        except Exception as e:
            print(f"[PubMed Error] {drug_name}: {str(e)}")
            return []
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if cached data exists and is not expired"""
        try:
            cache_entry = self.db.query(APICache).filter(
                APICache.cache_key == cache_key,
                APICache.expires_at > datetime.now()
            ).first()
            
            if cache_entry:
                print(f"[Cache HIT] {cache_key}")
                return cache_entry.response_data
            
            print(f"[Cache MISS] {cache_key}")
            return None
            
        except Exception as e:
            print(f"[Cache Check Error] {cache_key}: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save API response to cache"""
        try:
            expires_at = datetime.now() + self.cache_duration
            
            # Check if cache entry exists
            cache_entry = self.db.query(APICache).filter(
                APICache.cache_key == cache_key
            ).first()
            
            if cache_entry:
                # Update existing
                cache_entry.response_data = data
                cache_entry.expires_at = expires_at
                cache_entry.created_at = datetime.now()
            else:
                # Create new
                cache_entry = APICache(
                    cache_key=cache_key,
                    api_source="multi",
                    response_data=data,
                    expires_at=expires_at
                )
                self.db.add(cache_entry)
            
            self.db.commit()
            print(f"[Cache SAVE] {cache_key}")
            
        except Exception as e:
            print(f"[Cache Save Error] {cache_key}: {str(e)}")
            self.db.rollback()


# Helper function to extract drug names from text
def extract_drug_names(text: str) -> List[str]:
    """
    Extract potential drug names from user query
    This is a simple implementation - can be enhanced with NER model
    """
    import re
    
    # Common drug name patterns (capitalized words, excluding common words)
    words = text.split()
    drug_candidates = []
    
    common_words = {'the', 'and', 'or', 'is', 'are', 'what', 'how', 'when', 'where', 'why', 'about', 'between', 'with', 'for'}
    
    for word in words:
        # Remove punctuation
        clean_word = re.sub(r'[^\w\s]', '', word)
        # Check if it looks like a drug name (capitalized or all lowercase medical term)
        if clean_word and clean_word.lower() not in common_words and len(clean_word) > 3:
            drug_candidates.append(clean_word.lower())
    
    return drug_candidates[:5]  # Limit to 5 drugs max
