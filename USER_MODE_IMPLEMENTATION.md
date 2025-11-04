# User Mode Implementation - Complete

## Overview
Implemented a three-tier user mode system (Patient/Doctor/Researcher) with personalized response complexity and conversational AI flow.

## Changes Made

### 1. Backend - Model Service (`backend/services/groq_model_service.py`)

**Added Three Mode-Specific System Prompts:**

- **PATIENT_MODE_PROMPT**: 
  - 6th grade reading level
  - Simple, everyday language
  - Avoids medical jargon (e.g., "1 regular-strength tablet" instead of "500mg")
  - Warm, empathetic tone
  - Asks what medications patient is taking before providing analysis

- **DOCTOR_MODE_PROMPT**:
  - 12th grade+ reading level
  - Appropriate medical terminology
  - Standard dosing units (mg, mg/kg, ml)
  - Clinical context and evidence-based recommendations
  - Asks about patient regimen, comorbidities, renal/hepatic function

- **RESEARCHER_MODE_PROMPT**:
  - Full technical/scientific language
  - Molecular-level mechanisms
  - Detailed pharmacological data
  - Extensive primary literature citations
  - CYP enzyme specifics, toxicokinetics, structure-activity relationships

**Added Helper Function:**
```python
def get_system_prompt(user_mode: str = 'patient') -> str
```
Returns the appropriate prompt based on user mode.

**Updated `generate_response` Method:**
- Now accepts `user_mode` parameter (defaults to 'patient')
- Selects system prompt dynamically based on mode
- Logs user_mode in debug output

### 2. Backend - Chat Router (`backend/routers/chat.py`)

**Updated `/chat` endpoint:**
- Extracts `user_mode` from incoming message (defaults to 'patient')
- Passes `user_mode` to `model_service.generate_response()`
- Example:
```python
user_mode = getattr(message, 'user_mode', 'patient') or 'patient'
answer = await model_service.generate_response(
    question=message.message,
    context=None,
    user_mode=user_mode
)
```

### 3. Backend - Schemas (`backend/schemas.py`)

**Updated `ChatMessage` model:**
```python
user_mode: Optional[str] = Field('patient', description="User mode: patient, doctor, or researcher")
```

### 4. Frontend - API Service (`services/api.ts`)

**Updated `sendMessage` function:**
```typescript
async sendMessage(
  message: string, 
  sessionId?: string, 
  userMode?: 'patient' | 'doctor' | 'researcher'
): Promise<ChatResponse>
```
- Accepts `userMode` parameter
- Passes it to backend in request body as `user_mode`
- Defaults to 'patient' if not provided

### 5. Frontend - Main Page (`pages/index.tsx`)

**Added State Management:**
```typescript
const [userMode, setUserMode] = useState<'patient' | 'doctor' | 'researcher'>('patient');
```

**Updated `handleSend`:**
- Passes `userMode` to `apiService.sendMessage()`

**Updated WelcomeMessage:**
- Passes `userMode` and `onModeChange={setUserMode}` props

### 6. Frontend - UI Components (`components/UIComponents.tsx`)

**Updated `WelcomeMessage` component:**

**Added ModePill Component:**
- Three clickable pills: Patient 👤, Doctor ⚕️, Researcher 🔬
- Active mode shows gradient background with emerald glow
- Inactive modes show slate background with hover effects

**Updated Card Prompts:**
- Changed from specific questions to conversational triggers:
  - "I'd like to learn about drug interactions"
  - "I have questions about chemical safety"
  - "I want to know about toxicity and safety"
- AI will ask follow-up questions instead of providing canned responses

**Mode-Specific Welcome Text:**
```typescript
const getModeDescription = () => {
  switch(userMode) {
    case 'patient':
      return "I'll explain everything in simple, easy-to-understand language...";
    case 'doctor':
      return "I'll provide clinical guidance with appropriate medical terminology...";
    case 'researcher':
      return "I'll deliver comprehensive technical analysis...";
  }
}
```

## User Experience Flow

### Patient Mode
1. User selects "Patient" pill
2. Clicks a category card (e.g., "Drug Interactions")
3. AI responds: "I'd be happy to help you learn about drug interactions! To give you the most helpful information, could you tell me: Are you currently taking any other medications?"
4. User provides drug names
5. AI explains in simple terms (e.g., "no more than 8 regular tablets in 24 hours" instead of "4000mg")

### Doctor Mode
1. User selects "Doctor" pill
2. Clicks a category card
3. AI responds: "I can provide comprehensive information. To ensure clinically relevant guidance, could you share: What is the patient's current medication list? Are there any hepatic or renal concerns?"
4. User provides clinical context
5. AI delivers evidence-based recommendations with dosing in mg/kg, CYP enzyme details, etc.

### Researcher Mode
1. User selects "Researcher" pill
2. Clicks a category card
3. AI responds: "I can provide detailed toxicological and pharmacological data. What specific aspects are you investigating? (e.g., NAPQI-mediated hepatotoxicity, CYP2E1 metabolism, glutathione depletion kinetics)"
4. User specifies research focus
5. AI provides molecular mechanisms, Km/Vmax values, extensive literature citations

## Citation Requirements (All Modes)

All modes maintain inline citation requirements:
- Inline citations [1], [2], [3] after factual claims
- `## REFERENCES` section at the end
- APA-style formatting
- Mode-specific citation depth:
  - **Patient**: FDA, Mayo Clinic, reputable medical sites
  - **Doctor**: Clinical journals, guidelines, PMIDs
  - **Researcher**: Primary research literature with full bibliographic data

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Mode pills appear on welcome screen
- [ ] Clicking pill updates selected mode (visual feedback)
- [ ] Sending message in Patient mode gets 6th-grade response
- [ ] Sending message in Doctor mode gets clinical terminology
- [ ] Sending message in Researcher mode gets technical detail
- [ ] AI asks "what drugs are you taking?" in conversational flow
- [ ] All responses include inline citations [1], [2], [3]
- [ ] References section appears at bottom of responses
- [ ] User mode is logged to database (check via /admin)

## Database Logging

The `user_mode` field is now part of `ChatMessage` schema and will be logged to the database with each interaction, allowing admins to:
- Track which mode is used most frequently
- Analyze user expertise distribution
- Improve mode-specific prompts based on actual usage

## Next Steps (Optional Enhancements)

1. **Persistent Mode Selection**: Save user's preferred mode to localStorage
2. **Mode Indicator**: Show current mode in chat header during conversation
3. **Mode-Specific Examples**: Add tooltips showing example responses for each mode
4. **Analytics Dashboard**: Show mode usage statistics in admin panel
5. **Fine-tuning**: Collect user feedback on response complexity and adjust prompts
