from sqlalchemy.orm import Session
from db.models import Interaction, Reference
from typing import List, Optional

class InteractionService:
    @staticmethod
    def create_interaction(
        db: Session,
        drug_name: str,
        title: str,
        summary: str,
        mechanism: Optional[str] = None,
        food_groups: Optional[list] = None,
        recommended_actions: Optional[str] = None,
        evidence_quality: Optional[str] = None,
        references: Optional[List[dict]] = None,
    ) -> Interaction:
        inter = Interaction(
            drug_name=drug_name.lower(),
            title=title,
            summary=summary,
            mechanism=mechanism,
            food_groups=food_groups or [],
            recommended_actions=recommended_actions,
            evidence_quality=evidence_quality,
        )
        db.add(inter)
        db.commit()
        db.refresh(inter)

        # Add references
        if references:
            for ref in references:
                r = Reference(
                    interaction_id=inter.id,
                    title=ref.get("title"),
                    url=ref.get("url"),
                    excerpt=ref.get("excerpt"),
                )
                db.add(r)
            db.commit()
        db.refresh(inter)
        return inter

    @staticmethod
    def get_interactions_by_drug(db: Session, drug_name: str) -> List[Interaction]:
        return db.query(Interaction).filter(Interaction.drug_name == drug_name.lower()).all()

    @staticmethod
    def search_interactions_in_text(db: Session, text: str) -> List[Interaction]:
        """
        Very small naive matcher: looks for known drug_name tokens in text and returns interactions.
        In future this can be replaced with a NLP entity extractor.
        """
        text_l = text.lower()
        interactions = db.query(Interaction).all()
        matches = []
        for inter in interactions:
            if inter.drug_name and inter.drug_name in text_l:
                matches.append(inter)
        return matches


interaction_service = InteractionService()

def build_consumer_summary_from_evidence(db: Session, evidence_list: List[dict], max_items: int = 2) -> tuple[str, list]:
    """Deterministically build a short consumer-friendly summary from DB evidence.

    Returns (summary, evidence_ids_used)
    """
    def clean(s: Optional[str]) -> str:
        if not s:
            return ""
        return " ".join(str(s).replace('\n', ' ').split()).strip()

    if not evidence_list:
        return "", []

    # Prefer evidence with excerpts and higher evidence_quality (simple heuristic)
    def score(ev: dict):
        score = 0
        if ev.get('excerpt'):
            score += 2
        if ev.get('evidence_quality') == 'high':
            score += 1
        return score

    sorted_ev = sorted(evidence_list, key=lambda e: (-score(e), e.get('id', 0)))
    chosen = sorted_ev[:max_items]

    findings = []
    recommendations = []
    ids = []

    for ev in chosen:
        ids.append(ev.get('id'))
        rec = ev.get('recommended_actions')
        excerpt = ev.get('references') and len(ev.get('references')) and ev.get('references')[0].get('excerpt')
        summary_field = ev.get('summary') or ev.get('title') or ev.get('drug_name') or ''
        if rec:
            recommendations.append(clean(rec))
        elif excerpt:
            findings.append(clean(excerpt))
        else:
            findings.append(clean(summary_field))

    # Build sentences
    sentences = []
    if findings:
        sentences.append(" ".join(findings))
    if recommendations:
        sentences.append("Recommendation: " + "; ".join(recommendations))

    # Add provenance suffix with source indices
    if ids:
        sentences.append("Sources: " + ", ".join([str(i) for i in ids]))

    full = " ".join(sentences).strip()
    # clamp length to ~60 words
    words = full.split()
    if len(words) > 60:
        full = " ".join(words[:60]) + "..."

    return full, ids

def seed_default_interactions(db: Session):
    """Seed a small set of initial interactions if they don't exist."""
    # Check if any interactions exist
    existing = db.query(Interaction).count()
    if existing > 0:
        return

    # Minimal seed data for common examples
    seeds = [
        {
            "drug_name": "warfarin",
            "title": "Warfarin — vitamin K and cranberry",
            "summary": "Vitamin K foods alter warfarin effect; cranberry products have been reported to affect INR in some patients.",
            "mechanism": "Vitamin K antagonizes warfarin's anticoagulant effect; cranberry may affect warfarin metabolism leading to INR changes.",
            "food_groups": ["leafy_greens", "fruit_juices"],
            "recommended_actions": "Keep vitamin K intake consistent. Tell your prescriber if you start/stop cranberry products; monitor INR.",
            "evidence_quality": "moderate",
            "references": [
                {"title": "Warfarin: drug information - MedlinePlus", "url": "https://medlineplus.gov/druginfo/meds/a682277.html"},
                {"title": "Warfarin and diet - NHS", "url": "https://www.nhs.uk/conditions/warfarin/"}
            ]
        },
        {
            "drug_name": "simvastatin",
            "title": "Simvastatin — grapefruit interaction",
            "summary": "Grapefruit can increase statin blood levels and risk of muscle toxicity.",
            "mechanism": "Grapefruit inhibits intestinal CYP3A4, increasing systemic exposure of CYP3A4-metabolized statins.",
            "food_groups": ["grapefruit"],
            "recommended_actions": "Avoid grapefruit and grapefruit juice while taking certain statins; ask your pharmacist which statin you have.",
            "evidence_quality": "high",
            "references": [{"title": "Grapefruit juice and some common medications - FDA", "url": "https://www.fda.gov/consumers/consumer-updates/grapefruit-juice-and-some-medications"}]
        },
        {
            "drug_name": "levodopa",
            "title": "Levodopa — high-protein meals",
            "summary": "Large protein meals can reduce levodopa's effectiveness by competing for transport.",
            "mechanism": "Dietary amino acids compete with levodopa for absorption and brain transport.",
            "food_groups": ["proteins"],
            "recommended_actions": "Take levodopa 30–60 minutes before meals if tolerated or redistribute protein throughout the day.",
            "evidence_quality": "moderate",
            "references": [{"title": "Levodopa patient information - NHS", "url": "https://www.nhs.uk/conditions/parkinsons-disease/treatment/levodopa/"}]
        },
        {
            "drug_name": "doxycycline",
            "title": "Doxycycline — dairy and minerals",
            "summary": "Dairy, calcium, and iron reduce absorption if taken together with doxycycline.",
            "mechanism": "Divalent cations bind tetracyclines forming insoluble complexes and reduce absorption.",
            "food_groups": ["dairy", "calcium", "iron_supplements"],
            "recommended_actions": "Separate doses by ~2 hours; follow product labeling.",
            "evidence_quality": "high",
            "references": [{"title": "Doxycycline - MedlinePlus", "url": "https://medlineplus.gov/druginfo/meds/a682063.html"}]
        },
        {
            "drug_name": "metronidazole",
            "title": "Metronidazole — alcohol",
            "summary": "Avoid alcohol during and shortly after metronidazole to prevent disulfiram-like reactions.",
            "mechanism": "Metronidazole can cause disulfiram-like effects when combined with ethanol.",
            "food_groups": ["alcohol"],
            "recommended_actions": "Avoid alcohol while on treatment and for 48–72 hours after finishing.",
            "evidence_quality": "moderate",
            "references": [{"title": "Metronidazole - NHS", "url": "https://www.nhs.uk/medicines/metronidazole/"}]
        },
        {
            "drug_name": "maoi",
            "title": "MAOIs — tyramine-rich foods",
            "summary": "MAOIs interact with tyramine-containing foods, risking hypertensive crisis.",
            "mechanism": "MAO inhibition impairs tyramine metabolism leading to catecholamine release.",
            "food_groups": ["aged_cheeses", "cured_meats", "fermented_foods"],
            "recommended_actions": "Follow low-tyramine diet while on MAOIs; check specific lists with your clinician.",
            "evidence_quality": "high",
            "references": [{"title": "MAOI antidepressants - NHS", "url": "https://www.nhs.uk/conditions/maoi-antidepressants/"}]
        }
    ]

    for s in seeds:
        InteractionService.create_interaction(
            db=db,
            drug_name=s["drug_name"],
            title=s.get("title"),
            summary=s.get("summary"),
            mechanism=s.get("mechanism"),
            food_groups=s.get("food_groups"),
            recommended_actions=s.get("recommended_actions"),
            evidence_quality=s.get("evidence_quality"),
            references=s.get("references"),
        )
