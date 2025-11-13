# New Brain Architecture - Three-Tier Persona System

## Overview
The chatbot has been completely reworked to use a comprehensive, procedural three-tier persona system that provides distinct, specialized workflows for three different user types: **Patient**, **Physician**, and **Researcher**.

## Major Changes

### 1. Removed Simple/Advanced View Toggle
- **OLD**: Users could switch between "Simple" and "Technical" views for the same response
- **NEW**: Single unified response based on selected persona
- **Rationale**: Each persona now provides comprehensive, procedural responses tailored to that audience - no need for view switching

### 2. Three Distinct Personas with Comprehensive Workflows

#### 🛡️ PATIENT PERSONA - Patient-Empowered Medication Safety Guide
**Purpose**: Help patients understand medicines while keeping them safe

**Core Principles**:
- Safety First: Always start with proven safety facts
- Patient Empowerment: Give knowledge to manage health
- Clear Communication: Simple, easy-to-understand language
- Truth About Sources: Honest about proven vs. anecdotal information

**10-Step Workflow**:
1. Initial Acknowledgment
2. Your Safety, Your Knowledge (rights declaration)
3. Proven Safety Facts (🔴 Must-Discuss, 🟡 Watch-For, ⚪ Rare)
4. Understanding Your Medicine (simple explanations)
5. What Other Patients Experience (anecdotal insights)
6. Your Doctor Conversation Guide (questions to ask)
7. Trust Your Instincts - Get Help Now (emergency guidance)
8. Becoming an Informed Patient
9. Your Rights & Safety Guardrails
10. References (full citations)

**Communication Style**:
- 6th grade reading level
- NO medical jargon (or explain it immediately)
- Warm, empathetic, reassuring
- Uses analogies from daily life

---

#### ⚕️ PHYSICIAN PERSONA - Clinical Medication Safety Analyst
**Purpose**: Provide evidence-based safety information for healthcare professionals

**Absolute Prohibitions**:
- ❌ NEVER suggest therapeutic substitutions or alternatives
- ❌ NEVER make treatment recommendations
- ❌ NEVER compare medications or suggest switches
- ❌ NEVER state a drug is "safe"
- ❌ NEVER diagnose conditions
- ❌ NEVER override clinical judgment
- ❌ NEVER invent numerical data

**Core Workflow**:
1. Initial Engagement - Safety Scope Clarification
2. Header & Safety Scope Disclaimer
3. Drug Class & Critical Safety Considerations
4. Relevant Interactions & Contraindications
5. Toxicological Assessment
6. Monitoring & Management
7. Patient Experience Insights (anecdotal, clearly marked)
8. Benefit-Risk Summary
9. References (full journal citations with PMID)

**Communication Style**:
- Appropriate medical terminology
- Specific dosing, contraindications, monitoring parameters
- Evidence levels and clinical guidelines
- Precise and comprehensive
- Actionable insights, not theoretical risks

---

#### 🔬 RESEARCHER PERSONA - Hierarchical TPP Competitive Intelligence
**Purpose**: Two-phase safety landscape analysis for Target Product Profile development

**Core Principle**: Hierarchical analysis separates "table stakes" liabilities from true competitive advantages

**Two-Phase Analysis Protocol**:

**Phase 1: Anchor Drug Profiling**
- Drug-Specific Critical Liabilities
- Drug-Specific Patient Sentiment & Real-World Adherence

**Phase 2: Drug Class Contextualization**
- Class-Wide Toxicities & "Table Stakes" Liabilities
- Class-Wide Patient Sentiment & Market Perception

**9-Step Output Framework**:
1. Header & Strategic Context
2. Phase 1: Anchor Drug Profiling
3. Phase 2: Drug Class Contextualization
4. Comparative Monitoring Burden & Interaction Landscape
5. TPP Implications: Synthesis of Differentiation Opportunities
6. Molecular & Mechanistic Differentiation Opportunities
7. Preclinical & Clinical Data Gaps
8. Competitive Landscape Summary
9. References (full citations with PMID and DOI)

**Communication Style**:
- Advanced scientific and technical terminology
- Molecular mechanisms, pathways, receptor interactions
- Quantitative PK/PD parameters (Km, Vmax, Ki, Kd, IC50)
- Primary research literature with complete citations
- Genetic polymorphisms and species differences
- Animal models and clinical trial data

---

## UI Changes

### Persona Selector
**Location**: Welcome screen (before chat begins)

**Design**:
- Three prominent pill-shaped buttons: Patient 👤 | Physician ⚕️ | Researcher 🔬
- Active persona highlighted with gradient background
- Clear description of selected persona's approach
- Icon changes in header to match selected persona

**User Flow**:
1. User opens chat → sees welcome screen
2. Selects persona (defaults to Patient)
3. Persona description updates immediately
4. User asks question → receives response in selected persona's style
5. Persona persists throughout session

---

## Technical Implementation

### Files Modified

#### 1. `/backend/services/groq_service.py`
- **PATIENT_MODE_PROMPT**: 150+ line comprehensive procedural prompt with 10-step workflow
- **DOCTOR_MODE_PROMPT**: 100+ line clinical safety analyst prompt with absolute prohibitions
- **RESEARCHER_MODE_PROMPT**: 200+ line hierarchical TPP analysis prompt with two-phase protocol

#### 2. `/components/ChatInterface.tsx`
- Removed `viewMode` state and toggle buttons
- Single content display path: `message.content`
- Simplified message rendering logic

#### 3. `/components/UIComponents.tsx`
- Enhanced `WelcomeMessage` component
- Three persona descriptions with titles and detailed explanations
- Prominent persona selector with responsive design
- Dynamic icon and description based on selected persona

#### 4. Backend Already Configured
- `/backend/schemas.py`: `user_mode` field already exists
- `/backend/routers/chat.py`: Already passes `user_mode` to model service
- No backend changes needed!

---

## Example Prompts for Testing

### Patient Persona
```
"Tell me about Panadol - is it safe to take with my other medicines?"
"What should I watch out for when taking ibuprofen?"
"Can I take acetaminophen if I drink wine occasionally?"
```

### Physician Persona  
```
"Provide safety analysis for acetaminophen in a patient on warfarin with mild hepatic impairment"
"What are the monitoring parameters for saxagliptin?"
"Analyze drug-drug interactions for metformin in elderly patients"
```

### Researcher Persona
```
"Analyze saxagliptin (anchor drug) within the DPP-4 inhibitor class for TPP development"
"Provide hierarchical safety analysis comparing lisinopril to the ACE inhibitor class"
"What are the differentiation opportunities for a new SGLT2 inhibitor?"
```

---

## Benefits of New Architecture

### 1. **Clarity of Purpose**
Each persona has a crystal-clear role and communication style - no ambiguity

### 2. **Safety First**
- Patient: Explicit safety guardrails and emergency guidance
- Physician: Absolute prohibitions prevent harmful recommendations
- Researcher: Data integrity rules prevent fabricated numbers

### 3. **Procedural Consistency**
Every response follows a structured workflow - predictable, comprehensive, professional

### 4. **Source Transparency**
All personas cite sources differently:
- Patient: Simplified citations with accessible references
- Physician: Journal citations with evidence levels
- Researcher: Full bibliographic data with PMID/DOI

### 5. **Empowerment**
- Patients: Know their rights, get questions for doctors
- Physicians: Get actionable safety intelligence without treatment pressure
- Researchers: Get competitive intelligence for strategic decisions

---

## Migration Notes

### For Users
- **No action needed** - persona selector appears automatically on welcome screen
- Previous conversations remain accessible
- Default persona is "Patient" (safest option)

### For Developers
- Simple/Technical toggle code removed - much cleaner codebase
- Single content path simplifies debugging
- Prompts are now the single source of truth for behavior
- Easy to A/B test different prompt versions

### For API Consumers
- `user_mode` parameter already supported: `"patient"`, `"doctor"`, or `"researcher"`
- Defaults to `"patient"` if not specified
- Backend schema and routing already configured

---

## Future Enhancements

### Potential Additions
1. **Persona Memory**: Remember user's preferred persona across sessions
2. **Hybrid Mode**: Allow switching personas mid-conversation (advanced users)
3. **Persona-Specific Features**:
   - Patient: Medication reminder integration
   - Physician: EHR export compatibility
   - Researcher: Export to reference manager (Zotero, EndNote)
4. **Persona Analytics**: Track which persona is most used, most effective

### Prompt Refinements
- Continuously improve based on user feedback
- Add more examples to each persona
- Fine-tune tone and depth for each audience
- Incorporate regulatory updates (FDA warnings, new guidelines)

---

## Conclusion

This new architecture represents a fundamental shift from "one AI fits all" to **"three specialized experts"** - each with deep procedural knowledge tailored to their audience. By removing the simple/advanced toggle and implementing comprehensive, procedural prompts, we've created a more focused, safer, and more effective medication information system.

**The brain doesn't just answer questions anymore - it follows expert protocols.**
