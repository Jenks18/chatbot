# Roadmap: OpenEvidence Features

## Introducing OpenEvidence Visits

OpenEvidence Visits is a planned HIPAA-compliant feature that can record patient encounters, write comprehensive documentation, and surface key evidence relevant to patient details. It is designed to ease administrative burden, proactively identify clinical insights, and support clinicians—free for verified U.S. healthcare professionals.

To access OpenEvidence Visits, users will need to create an account and verify their healthcare professional credentials. Once verified, features will include:

- Secure recording of visit audio/text with patient consent
- Auto-generated clinical notes and SOAP-style summaries
- Extraction and surfacing of evidence (peer-reviewed articles, guidelines, drug labels) tailored to the patient context
- Integration with chat logs: user/clinician chats can be associated with patient encounters for audit and continuity
- Exportable documentation in common formats (PDF, HL7 FHIR bundles)

Privacy & compliance notes:
- Visits will be encrypted at rest and in transit
- Verification workflows will be required for U.S. clinician accounts
- Audit logs will record access and export events

How it ties to the product roadmap:
- Q1: MVP of visit recording + note generation (internal beta)
- Q2: Evidence surfacing integrated into visit summary (pilot with hospital partners)
- Q3: Verified accounts + clinician dashboard + export options

Usage model and onboarding:
- Free for verified U.S. healthcare professionals
- Account creation + credential verification required to enable 'Visits'
- Chat logs and visit data will be linked to accounts for audit / continuity; admin controls will let organizations opt in/out

Developer note: implement a backend service for secure storage and ACLs, update the `ChatLog` model to optionally associate a `visit_id`, and expose admin endpoints to manage verified accounts and exports.

---

If you'd like, I can add a UI mockup for onboarding screens and a small API schema for the `visits` endpoints (create visit, append transcript, finalize visit, export).