# Quick Start - Testing Your New Brain

## Start the System

### 1. Start Backend
```bash
cd /Users/iannjenga/Desktop/chatbot/backend
uvicorn main:app --reload
```

### 2. Start Frontend (in new terminal)
```bash
cd /Users/iannjenga/Desktop/chatbot
npm run dev
```

### 3. Open Browser
```
http://localhost:3000
```

---

## Test Each Persona

### 🛡️ Test 1: Patient Persona

**Steps:**
1. Select **👤 Patient** persona
2. Read the description - should say "Patient-Empowered Medication Safety"
3. Ask: **"Tell me about Panadol - is it safe to take?"**

**Expected Response Should Include:**
- ✅ Friendly acknowledgment
- ✅ "Thanks for asking about..."
- ✅ 🔴 Must-Discuss Risks section
- ✅ 🟡 Watch-For Issues section
- ✅ Simple language (6th grade level)
- ✅ "Questions to Ask Your Doctor" section
- ✅ "Go to Emergency or Call 911 if..." section
- ✅ YOUR RIGHTS AS A PATIENT section
- ✅ SAFETY GUARDRAILS section
- ✅ References section
- ❌ NO medical jargon without explanation
- ❌ NO complex pharmacology

**Look for emojis**: 🛡️, 🚨, 💡, 👥, 🎯, ✅, ❌, ❗

---

### ⚕️ Test 2: Physician Persona

**Steps:**
1. Click **Clear** to start fresh
2. Select **⚕️ Physician** persona
3. Read the description - should say "Clinical Medication Safety Analysis"
4. Ask: **"Provide safety analysis for acetaminophen in a patient on warfarin"**

**Expected Response Should Include:**
- ✅ "I provide safety analysis for specified medications only"
- ✅ ⚠️ Important disclaimer about not recommending alternatives
- ✅ Drug Class & Critical Safety Considerations
- ✅ Drug-Drug Interactions section (warfarin mentioned)
- ✅ Monitoring Parameters section
- ✅ Medical terminology (hepatotoxicity, glucuronidation, CYP2E1)
- ✅ "Patient Experience Insights" clearly marked as anecdotal
- ✅ References with journal names and PMID numbers
- ❌ NO treatment recommendations ("try this instead...")
- ❌ NO diagnosis statements
- ❌ NO invented numbers

**Look for clinical language**: contraindications, pharmacokinetics, monitoring, evidence levels

---

### 🔬 Test 3: Researcher Persona

**Steps:**
1. Click **Clear** to start fresh
2. Select **🔬 Researcher** persona
3. Read the description - should say "Hierarchical TPP Competitive Intelligence"
4. Ask: **"Analyze acetaminophen compared to the NSAID class for TPP development"**

**Expected Response Should Include:**
- ✅ "I will conduct a hierarchical safety analysis for your TPP"
- ✅ Request for more context (anchor drug, class, strategic goal)
- ✅ "TPP Safety Landscape: [Drug] vs. [Class]" header
- ✅ PHASE 1: Anchor Drug Profiling section
- ✅ PHASE 2: Drug Class Contextualization section
- ✅ Drug-Specific Liabilities vs. Class-Wide Liabilities
- ✅ Molecular mechanisms (COX inhibition, NAPQI formation, etc.)
- ✅ Quantitative data (IC50, Km, Vd, t1/2, therapeutic margins)
- ✅ TPP Implications: Differentiation Opportunities
- ✅ References with full citations (journal, year, volume, pages, PMID, DOI)
- ❌ NO simplified language
- ❌ NO generic patient advice

**Look for technical depth**: receptor targets, enzyme kinetics, structure-activity relationships

---

## Quick Validation Checklist

### ✅ UI Checks
- [ ] Persona selector appears on welcome screen
- [ ] Three options: Patient, Physician, Researcher
- [ ] Selected persona is highlighted
- [ ] Description updates when selecting different personas
- [ ] Icon changes in response header
- [ ] NO Simple/Technical toggle buttons visible
- [ ] References section is collapsible

### ✅ Patient Mode Checks
- [ ] Simple, warm, friendly language
- [ ] Emojis used for visual clarity
- [ ] Emergency guidance present
- [ ] Patient rights declaration present
- [ ] Questions for doctor included
- [ ] No unexplained medical jargon

### ✅ Physician Mode Checks
- [ ] Clinical terminology used appropriately
- [ ] Prohibitions stated upfront
- [ ] No treatment recommendations
- [ ] Monitoring parameters included
- [ ] Patient insights marked as anecdotal
- [ ] PMID citations present

### ✅ Researcher Mode Checks
- [ ] Requests strategic context
- [ ] Two-phase structure visible
- [ ] Molecular mechanisms detailed
- [ ] Quantitative data included
- [ ] Competitive positioning analysis
- [ ] Full bibliographic citations (PMID + DOI)

---

## Common Issues & Solutions

### Issue: Persona selector not showing
**Solution**: Check that you're on the welcome screen (no messages yet). Clear chat if needed.

### Issue: Response doesn't match persona style
**Solution**: 
1. Check browser console for errors
2. Verify backend is using updated groq_service.py
3. Restart backend: Ctrl+C, then `uvicorn main:app --reload`
4. Hard refresh frontend: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### Issue: Getting generic responses
**Solution**: 
1. Check that `user_mode` is being sent in API request (check Network tab)
2. Verify GROQ_API_KEY is set in backend/.env
3. Check backend logs for which mode is being used

### Issue: References not showing
**Solution**: 
1. Click the "References" dropdown (it's collapsible)
2. Check that AI is including citations in response
3. Verify references parsing logic in ChatInterface.tsx

---

## What Success Looks Like

### Patient Mode Response
```
Thanks for asking about Panadol. I can help you...

YOUR SAFETY, YOUR KNOWLEDGE
You have the right to understand...

🔴 PROVEN SAFETY FACTS
Must-Discuss Risks: Never take more than...

[10-step workflow clearly visible]

References:
[1] FDA Drug Label...
```

### Physician Mode Response
```
I provide safety analysis for specified medications only...

ACETAMINOPHEN - CLINICAL SAFETY ASSESSMENT
⚠️ Important: This is a safety report...

Drug Class: Centrally-acting analgesic...

[9-step clinical workflow]

References:
[1] Author et al. Journal. Year;Vol:Pages. PMID: xxxxx
```

### Researcher Mode Response
```
I will conduct a hierarchical safety analysis...

TPP Safety Landscape: Acetaminophen vs. NSAIDs

PHASE 1: ANCHOR DRUG PROFILING
Drug-Specific Critical Liabilities:...

PHASE 2: DRUG CLASS CONTEXTUALIZATION
Class-Wide Toxicities:...

[9-step research workflow]

References:
[1] Author et al. Journal. Year;Vol:Pages. PMID: xxxxx DOI: xx.xxxx
```

---

## Next Steps After Testing

### If Everything Works:
1. ✅ Document any additional test cases
2. ✅ Consider adding persona memory (save preference)
3. ✅ Monitor real user interactions
4. ✅ Collect feedback on each persona
5. ✅ Refine prompts based on usage

### If Issues Found:
1. 🔍 Check browser console for JavaScript errors
2. 🔍 Check backend logs for Python errors
3. 🔍 Verify environment variables are set
4. 🔍 Test API endpoint directly (Postman/curl)
5. 🔍 Compare response to expected workflow

---

## Testing Shortcuts

### Test All Three Quickly:
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend  
npm run dev

# Browser: http://localhost:3000
# 1. Select Patient → Ask "Tell me about aspirin"
# 2. Clear → Select Physician → Ask "Safety analysis for aspirin"
# 3. Clear → Select Researcher → Ask "Analyze aspirin vs NSAIDs for TPP"
```

### Verify Prompt Being Used:
Add this to backend logs temporarily:
```python
print(f"[DEBUG] Using prompt for mode: {user_mode}")
print(f"[DEBUG] Prompt length: {len(system_prompt)}")
```

---

## Success Criteria

You'll know it's working when:
- ✅ Each persona has dramatically different tone
- ✅ Patient mode is warm and simple
- ✅ Physician mode has prohibitions and clinical depth
- ✅ Researcher mode requests strategic context
- ✅ All personas cite sources appropriately
- ✅ No Simple/Technical toggle visible
- ✅ Responses follow structured workflows

---

## Ready to Ship Checklist

Before deploying to production:
- [ ] All three personas tested with multiple queries
- [ ] References displaying correctly for each mode
- [ ] Emergency guidance present in Patient mode
- [ ] Prohibitions stated in Physician mode
- [ ] Two-phase structure in Researcher mode
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] Persona persists across messages in session
- [ ] Clear chat resets persona selection
- [ ] Mobile responsive design tested

---

## You're Done! 🎉

Your chatbot now has three specialized expert brains instead of one generic brain. Each persona follows professional protocols and provides exactly the right type of information for that audience.

**The brain doesn't just answer questions anymore - it follows expert workflows.**
