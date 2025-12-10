"""
Quick test to verify Instructor + Groq integration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.groq_service import groq_service

async def test_patient_mode():
    """Test patient mode response formatting"""
    print("=" * 60)
    print("TEST 1: Patient Mode - Educational Response")
    print("=" * 60)
    
    response = await groq_service.generate_response(
        query="What is aspirin?",
        user_mode="patient",
        max_tokens=1500
    )
    
    print(response)
    print("\n")
    
    # Check for proper formatting
    checks = {
        "No markdown headers (##)": "##" not in response,
        "No bold markdown (**)": "**" not in response,
        "Has References section": "References:" in response or "references:" in response.lower(),
        "Has inline citations [1]": "[1]" in response,
        "Has Key Points section": "Key Points:" in response or "key points:" in response.lower(),
        "Has bullet points (•)": "•" in response or "-" in response,
    }
    
    print("FORMATTING CHECKS:")
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check}")
    
    return all(checks.values())

async def test_doctor_mode():
    """Test doctor mode response formatting"""
    print("\n" + "=" * 60)
    print("TEST 2: Doctor Mode - Clinical Response")
    print("=" * 60)
    
    response = await groq_service.generate_response(
        query="Acetaminophen hepatotoxicity mechanism",
        user_mode="doctor",
        max_tokens=1500
    )
    
    print(response)
    print("\n")
    
    # Check for proper formatting
    checks = {
        "No markdown headers (##)": "##" not in response,
        "No bold markdown (**)": "**" not in response,
        "Has References section": "References:" in response or "references:" in response.lower(),
        "Has inline citations [1]": "[1]" in response,
        "Has clinical terminology": any(term in response.lower() for term in ["hepatotoxicity", "mechanism", "napqi", "glutathione"]),
    }
    
    print("FORMATTING CHECKS:")
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check}")
    
    return all(checks.values())

async def test_health():
    """Test API health"""
    print("\n" + "=" * 60)
    print("TEST 3: API Health Check")
    print("=" * 60)
    
    health = await groq_service.check_health()
    print(f"Status: {health.get('status')}")
    print(f"Model: {health.get('model')}")
    print(f"Instructor: {health.get('instructor')}")
    
    return health.get('status') == 'healthy'

async def main():
    """Run all tests"""
    print("\n🧬 TESTING INSTRUCTOR + GROQ INTEGRATION")
    print("=" * 60)
    
    try:
        # Test health first
        health_ok = await test_health()
        if not health_ok:
            print("\n❌ API health check failed. Check GROQ_API_KEY")
            return
        
        # Test patient mode
        patient_ok = await test_patient_mode()
        
        # Test doctor mode
        doctor_ok = await test_doctor_mode()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Patient Mode: {'✅ PASS' if patient_ok else '❌ FAIL'}")
        print(f"Doctor Mode: {'✅ PASS' if doctor_ok else '❌ FAIL'}")
        
        if health_ok and patient_ok and doctor_ok:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print("\n⚠️  Some tests failed. Review output above.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
