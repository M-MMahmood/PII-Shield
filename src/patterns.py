"""
PII detection patterns — high precision / conservative by default.
All patterns are compiled regex. False positive rate is minimized by using
strict anchors, boundaries, and length checks.
"""
import re

# --------------------------------------------------------------------------- #
#  Built-in category definitions                                               #
# --------------------------------------------------------------------------- #

BUILTIN_CATEGORIES = [
    {
        "id": "email",
        "label": "Email addresses",
        "tag": "[EMAIL]",
        "enabled": True,
        "patterns": [
            re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')
        ],
    },
    {
        "id": "phone",
        "label": "Phone numbers",
        "tag": "[PHONE]",
        "enabled": True,
        "patterns": [
            # US/international formats: (555) 555-5555, 555-555-5555, +1 555 555 5555
            re.compile(r'(?<!\w)(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(?!\w)'),
        ],
    },
    {
        "id": "ssn",
        "label": "SSN / National ID",
        "tag": "[SSN]",
        "enabled": True,
        "patterns": [
            # US SSN: 123-45-6789 or 123 45 6789
            re.compile(r'\b(?!000|666|9\d{2})\d{3}[-\s](?!00)\d{2}[-\s](?!0000)\d{4}\b'),
        ],
    },
    {
        "id": "credit_card",
        "label": "Credit / debit card numbers",
        "tag": "[CARD_NUMBER]",
        "enabled": True,
        "patterns": [
            # 13-19 digit card numbers with optional separators
            re.compile(r'\b(?:\d[ \-]?){13,19}\b'),
        ],
    },
    {
        "id": "dob",
        "label": "Dates of birth",
        "tag": "[DATE_OF_BIRTH]",
        "enabled": True,
        "patterns": [
            # Explicit DOB phrases: "DOB: 01/15/1990" or "Date of Birth: January 15, 1990"
            re.compile(
                r'(?i)(?:date\s+of\s+birth|dob|birth\s+date)\s*[:\-]?\s*'
                r'(?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}'
                r'|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?'
                r'|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+\d{1,2},?\s+\d{4})'
            ),
        ],
    },
    {
        "id": "bank_account",
        "label": "Bank / account numbers",
        "tag": "[BANK_ACCOUNT]",
        "enabled": True,
        "patterns": [
            # Explicit "Account number: XXXXXXXX" or "Routing: XXXXXXXXX"
            re.compile(r'(?i)(?:account\s+(?:number|no\.?|#)\s*[:\-]?\s*)(\d[\d\s\-]{5,20}\d)'),
            re.compile(r'(?i)(?:routing\s+(?:number|no\.?|#)\s*[:\-]?\s*)(\d{9})'),
        ],
    },
    {
        "id": "ip_address",
        "label": "IP addresses",
        "tag": "[IP_ADDRESS]",
        "enabled": True,
        "patterns": [
            # IPv4
            re.compile(
                r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}'
                r'(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
            ),
            # IPv6 (simplified)
            re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),
        ],
    },
    {
        "id": "zip",
        "label": "ZIP / postal codes",
        "tag": "[ZIP_CODE]",
        "enabled": True,
        "patterns": [
            # US ZIP: 12345 or 12345-6789 (with context boundary to reduce FP)
            re.compile(r'(?i)(?:zip\s*(?:code)?\s*[:\-]?\s*|postal\s*code\s*[:\-]?\s*)(\d{5}(?:-\d{4})?)'),
            # Canadian postal
            re.compile(r'\b[ABCEGHJ-NPRSTVXY]\d[A-Z]\s?\d[A-Z]\d\b'),
        ],
    },
    {
        "id": "url",
        "label": "URLs",
        "tag": "[URL]",
        "enabled": True,
        "patterns": [
            re.compile(r'\bhttps?://[^\s<>"\']{4,}\b'),
        ],
    },
    {
        "id": "name",
        "label": "Full names",
        "tag": "[NAME]",
        "enabled": True,
        "patterns": [
            # Name preceded by salutation or "name:" label — high precision only
            re.compile(
                r'(?i)(?:^|\b)(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+'
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
            ),
            re.compile(
                r'(?i)(?:name\s*[:\-]\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})'
            ),
        ],
    },
    {
        "id": "address",
        "label": "Street addresses",
        "tag": "[ADDRESS]",
        "enabled": True,
        "patterns": [
            # "123 Main Street", "456 Oak Ave Apt 7"
            re.compile(
                r'\b\d{1,5}\s+[A-Z][a-zA-Z0-9\s]{3,40}'
                r'(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|'
                r'Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter)\b',
                re.IGNORECASE
            ),
        ],
    },
]

CATEGORY_IDS = [c["id"] for c in BUILTIN_CATEGORIES]
