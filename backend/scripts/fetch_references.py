"""
CLI script to fetch reference URLs in the DB and populate Reference.excerpt fields.
Run: python backend/scripts/fetch_references.py
"""
import asyncio
import sys
import os

# Ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

from backend.db.database import get_db
from backend.db.models import Reference
import httpx
from bs4 import BeautifulSoup

async def fetch_and_update(limit=100):
    db = next(get_db())
    refs = db.query(Reference).filter(Reference.excerpt == None).limit(limit).all()
    if not refs:
        print("No references without excerpt found.")
        return

    async with httpx.AsyncClient(timeout=15.0) as client:
        for r in refs:
            try:
                resp = await client.get(r.url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                excerpt = None
                for p in soup.find_all('p'):
                    txt = p.get_text(strip=True)
                    if txt and len(txt) > 50:
                        excerpt = txt[:800]
                        break
                if not excerpt:
                    body = soup.get_text(separator=' ', strip=True)
                    excerpt = body[:800] if body else None

                if excerpt:
                    r.excerpt = excerpt
                    db.add(r)
                    db.commit()
                    print(f"Updated reference {r.id} ({r.url}) excerpt length {len(excerpt)}")
                else:
                    print(f"No excerpt found for {r.url}")
            except Exception as e:
                print(f"Error fetching {r.url}: {e}")

if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    asyncio.run(fetch_and_update(limit=limit))
