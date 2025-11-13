# Before & After Comparison

## Old System vs. New System

### OLD: Simple/Advanced Toggle System
```
┌─────────────────────────────────────────┐
│  User asks question                     │
│  ↓                                       │
│  AI generates ONE response              │
│  ↓                                       │
│  Backend creates TWO versions:          │
│  • Technical (full response)            │
│  • Simple (consumer summary)            │
│  ↓                                       │
│  Frontend shows toggle:                 │
│  [Simple] [Technical]                   │
│  ↓                                       │
│  User switches views of SAME content    │
└─────────────────────────────────────────┘

Problems:
❌ Same content, just simplified
❌ No procedural workflow
❌ Not tailored to user expertise
❌ No safety framework
❌ Generic "one size fits all" approach
```

### NEW: Three-Tier Persona System
```
┌─────────────────────────────────────────┐
│  User selects PERSONA first:            │
│  [Patient] [Physician] [Researcher]     │
│  ↓                                       │
│  User asks question                     │
│  ↓                                       │
│  AI uses PERSONA-SPECIFIC PROMPT with:  │
│  • Distinct workflow (10, 9, or 9 steps)│
│  • Appropriate language level           │
│  • Role-specific prohibitions           │
│  • Tailored safety guidance             │
│  • Custom citation style                │
│  ↓                                       │
│  ONE comprehensive response             │
│  ↓                                       │
│  Frontend displays as-is (no toggle)    │
└─────────────────────────────────────────┘

Benefits:
✅ Three distinct expert modes
✅ Structured procedural workflows
✅ Safety-first frameworks
✅ Appropriate language for audience
✅ Clear role boundaries
✅ No ambiguity about purpose
```

---

## Comparison by Feature

| Feature | OLD System | NEW System |
|---------|-----------|------------|
| **User Selection** | Simple/Technical toggle | Patient/Physician/Researcher selector |
| **When Selected** | After response generated | Before asking question |
| **Response Generation** | Same content, different views | Different content, different workflows |
| **Language Level** | Two levels (simple/technical) | Three levels (6th grade/clinical/scientific) |
| **Workflow** | None - ad-hoc responses | 10-step (Patient), 9-step (Physician), 9-step (Researcher) |
| **Safety Guidance** | General disclaimers | Persona-specific (emergency guidance for patients, prohibitions for physicians, data integrity for researchers) |
| **Citations** | Generic references | Tailored (simple for patients, PMID for physicians, PMID+DOI for researchers) |
| **Purpose** | Information delivery | Patient empowerment / Clinical decision support / Competitive intelligence |
| **Prohibitions** | None explicit | 7 absolute prohibitions for physicians |
| **Rights Declaration** | None | Explicit patient rights in Patient mode |
| **Emergency Guidance** | Generic | Step 7 in Patient workflow |
| **Hierarchical Analysis** | Not available | Phase 1 & 2 in Researcher mode |
| **Code Complexity** | Higher (dual content paths) | Lower (single content path) |

---

## Example Response Comparison

### Question: "Tell me about acetaminophen safety"

#### OLD System - Simple View
```
Acetaminophen (Panadol/Tylenol) is a pain reliever. 
It's generally safe when used correctly. Maximum 
dose is 4000mg per day. Can cause liver damage if 
taken in excess. Avoid alcohol while taking it.

[Toggle to Technical View]
```

#### OLD System - Technical View  
```
Acetaminophen is a centrally-acting analgesic with 
COX inhibition. Hepatically metabolized via 
glucuronidation and CYP2E1 oxidation to NAPQI. 
Hepatotoxicity risk with doses >7.5g. Contraindicated 
in severe hepatic impairment.

[1] FDA Label 2024
[2] Prescott et al. Br J Clin Pharmacol 1980
```

---

#### NEW System - Patient Persona
```
Thanks for asking about acetaminophen. I can help you 
understand this medicine so you can make safer decisions 
with your doctor.

I'll provide:
A) Key Safety Facts - what's proven by medical research
B) What other patients experience
C) Questions to ask your doctor
D) When to get emergency help

YOUR SAFETY, YOUR KNOWLEDGE

You have the right to understand your medicines.

This information comes from:
- Government-approved drug safety labels
- Medical research studies  
- What other patients experience

Your doctor knows your personal health story best. 
Use this information to have better conversations 
with your healthcare team.

🔴 PROVEN SAFETY FACTS

From Government Medical Agencies:

Must-Discuss Risks: Never take more than 8 regular 
tablets (4000mg) in 24 hours [1]. Taking too much 
can seriously harm your liver, which is the organ 
that cleans your blood [2]. This is especially 
dangerous if you drink alcohol regularly [3].

🟡 Watch-For Issues: Check all your medicines because 
some cold and flu products already contain 
acetaminophen [4]. Taking them together could mean 
you accidentally take too much without realizing it.

[Continues through all 10 steps...]

REFERENCES:
[1] FDA Drug Label - Acetaminophen, Food and Drug 
    Administration, 2024
[2] Acetaminophen Hepatotoxicity, New England Journal 
    of Medicine, 2022
[... full simplified references]
```

#### NEW System - Physician Persona
```
I provide safety analysis for specified medications 
only. I cannot recommend treatments or alternatives.

I can provide:
- Quick Overview: major warnings and top concerns 
  for acetaminophen
- Personalized Risk Assessment: detailed safety 
  analysis with specific patient context

For personalized assessment, I'll need relevant context:
• Other medications (prescription/OTC)
• Supplements/herbal products
• Relevant medical conditions

ACETAMINOPHEN - CLINICAL SAFETY ASSESSMENT

⚠️ Important: This is a safety report for the 
specified medication only. It does not compare 
treatments, recommend alternatives, or assess efficacy.

DRUG CLASS & CRITICAL SAFETY CONSIDERATIONS

Drug Class: Centrally-acting analgesic and antipyretic 
with weak, reversible COX-1/COX-2 inhibition [1]

Boxed Warnings/Important Safety Information: 
Hepatotoxicity risk with supratherapeutic dosing. 
Maximum daily dose 4g (reduce to 3g in chronic 
alcoholics or hepatic impairment) [2]. Acute 
liver failure can occur with doses exceeding 
7.5-10g or chronic supratherapeutic use [3].

[Continues through all 9 steps...]

REFERENCES:
[1] Botting R. Mechanism of action of acetaminophen. 
    Am J Med. 1983;75(5A):38-46
[2] FDA Drug Label - Acetaminophen. Food and Drug 
    Administration. 2024
[... full journal citations with PMID]
```

#### NEW System - Researcher Persona
```
I will conduct a hierarchical safety analysis for 
your TPP. We'll start with a specific drug, then 
expand to its class.

To analyze acetaminophen comprehensively, please specify:
- Drug class for comparison (e.g., "all analgesics", 
  "COX inhibitors", "OTC pain relievers")
- Target patient population and comorbidities
- TPP strategic goal

[If user provides: "Compare to NSAIDs for OTC pain relief"]

TPP SAFETY LANDSCAPE: Acetaminophen vs. NSAIDs

Strategic Goal: Identifying differentiation 
opportunities for acetaminophen positioning 
relative to NSAID class for OTC pain management

PHASE 1: ANCHOR DRUG PROFILING (Acetaminophen)

A) Drug-Specific Critical Liabilities:

Acetaminophen carries unique hepatotoxicity risk 
via NAPQI-mediated glutathione depletion, a mechanism 
not shared by NSAIDs [1]. The narrow therapeutic 
index (toxic dose approximately 10g vs. therapeutic 
dose 4g, margin of 2.5) presents significant safety 
concern [2].

Metabolism via CYP2E1 creates vulnerability to 
enzyme inducers (ethanol, isoniazid) that increase 
NAPQI formation and hepatotoxicity risk [3].

[Continues through comprehensive 9-step analysis 
with molecular mechanisms, PK/PD data, competitive 
positioning...]

REFERENCES:
[1] Mitchell JR, et al. Acetaminophen-induced hepatic 
    necrosis. J Pharmacol Exp Ther. 1973;187(1):185-194. 
    PMID: 4746327 DOI: 10.1016/xxxxx
[... complete bibliographic data]
```

---

## Visual UI Comparison

### OLD Interface
```
┌─────────────────────────────────────────────┐
│ 🧬 Kandih ToxWiki             [Clear] [Auth]│
├─────────────────────────────────────────────┤
│                                             │
│  You: Tell me about acetaminophen           │
│                                             │
│  🧬 Kandih ToxWiki    [Simple] [Technical] ← Toggle
│  Acetaminophen is a pain reliever...        │
│                                             │
└─────────────────────────────────────────────┘
    ↑ Toggle appears AFTER response
```

### NEW Interface
```
┌─────────────────────────────────────────────┐
│ 🧬 Kandih ToxWiki             [Clear] [Auth]│
├─────────────────────────────────────────────┤
│        Welcome to Kandih ToxWiki            │
│                                             │
│          Select Your Persona:               │
│                                             │
│    [👤 Patient] [⚕️ Physician] [🔬 Researcher] ← Selector
│                                             │
│    Patient-Empowered Medication Safety      │
│    I help you understand your medicines     │
│    while keeping you safe...                │
│                                             │
│  [Ask about medications...]                 │
└─────────────────────────────────────────────┘
    ↑ Persona selection BEFORE asking
```

---

## Key Differences

### 1. **Timing**
- **OLD**: Select view AFTER response
- **NEW**: Select persona BEFORE asking

### 2. **Content**
- **OLD**: Same content, different presentations
- **NEW**: Different content, different workflows

### 3. **Purpose**
- **OLD**: Simplify complex information
- **NEW**: Provide expert-level guidance for specific audiences

### 4. **Safety**
- **OLD**: Generic disclaimers
- **NEW**: Persona-specific safety frameworks

### 5. **User Experience**
- **OLD**: Toggle between views, possibly confusing
- **NEW**: Single clear response tailored to you

### 6. **Developer Experience**
- **OLD**: Maintain two content paths, complexity
- **NEW**: Single content path, simpler code

---

## Migration Impact

### For End Users
- **More focused**: Get exactly what you need for your role
- **More comprehensive**: Follow structured workflows
- **More empowering**: Know your rights, get guidance
- **Clearer expectations**: Know what the AI will/won't do

### For Developers
- **Simpler codebase**: One display path instead of two
- **Easier to test**: Clear expected outputs per persona
- **Easier to improve**: Update one prompt at a time
- **Better separation of concerns**: Prompts own behavior

### For API Consumers
- **Backward compatible**: Still accepts `user_mode` parameter
- **Defaults to safe**: "patient" mode is default
- **Clear contract**: Each mode has defined behavior

---

## Bottom Line

**OLD**: One AI trying to serve everyone by simplifying content  
**NEW**: Three specialized experts, each following professional protocols

The new system doesn't just format information differently - it thinks differently based on who you are and what you need.
