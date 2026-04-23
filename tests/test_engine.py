"""Unit tests for the detection engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine import detect, apply_redactions

SAMPLE = """
Dear Mr. John Smith,
Email: jane.doe@example.com
Phone: (555) 867-5309
SSN: 123-45-6789
IP: 192.168.1.1
Account Number: 98765432
Date of Birth: January 15, 1990
Visit https://example.com for details.
"""

def test_email():
    findings = detect(SAMPLE, ["email"], [])
    assert any(f.tag == "[EMAIL]" for f in findings), "Email not detected"

def test_phone():
    findings = detect(SAMPLE, ["phone"], [])
    assert any(f.tag == "[PHONE]" for f in findings), "Phone not detected"

def test_ssn():
    findings = detect(SAMPLE, ["ssn"], [])
    assert any(f.tag == "[SSN]" for f in findings), "SSN not detected"

def test_name():
    findings = detect(SAMPLE, ["name"], [])
    assert any(f.tag == "[NAME]" for f in findings), "Name not detected"

def test_ip():
    findings = detect(SAMPLE, ["ip_address"], [])
    assert any(f.tag == "[IP_ADDRESS]" for f in findings), "IP not detected"

def test_custom_pattern():
    findings = detect(SAMPLE, [], [{"name": "CustomID", "pattern": r"EMP-\d+"}])
    # No match expected in sample — just ensure no crash
    assert isinstance(findings, list)

def test_apply_redactions():
    findings = detect(SAMPLE, ["email", "phone", "ssn"], [])
    redacted = apply_redactions(SAMPLE, findings)
    assert "jane.doe@example.com" not in redacted
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
    assert "[SSN]" in redacted

def test_no_false_positive_plain_number():
    text = "The count is 12345 items."
    findings = detect(text, ["ssn", "credit_card"], [])
    # Should not flag a plain 5-digit number as SSN or card
    assert len(findings) == 0, f"False positive: {findings}"

if __name__ == "__main__":
    tests = [test_email, test_phone, test_ssn, test_name, test_ip,
             test_custom_pattern, test_apply_redactions, test_no_false_positive_plain_number]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
