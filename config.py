"""
Config — API keys, model selection, and regulatory basis per finding.

Every agent attaches a regulatory_basis to its record. That basis is
the obligation the finding creates, not the obligation to keep a
record of it.

The four deterministic agents apply rules, so they cite the requirement
they are executing. The Case Summary Agent is the only component that
uses a model, so it is the only one that cites the model governance
obligation.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model
MODEL = "groq/openai/gpt-oss-120b"

# Trace output
TRACES_DIR = "traces"

# Explainability — used by the Case Summary Agent
E23_EXPLAINABILITY = (
    "OSFI E-23 - AI-assisted decisions must be explainable and documented"
)

# The obligation each finding creates. Looked up by every agent after
# it decides what to return. If a finding is missing from this dict
# the agent will raise a KeyError, which is better than silently
# recording nothing.
REGULATORY_BASIS = {
    # Identity
    "IDENTITY_VERIFIED": (
        "PCMLTFA - identity verification required before account opening"
    ),
    "IDENTITY_INCOMPLETE": (
        "PCMLTFA - identity verification required before account opening; "
        "cannot proceed with incomplete information"
    ),

    # Screening — sanctions
    "SANCTIONS_MATCH_CONFIRMED": (
        "PCMLTFA - dealing with a listed person is prohibited; "
        "hard stop, no discretion"
    ),
    "SANCTIONS_POTENTIAL_MATCH": (
        "PCMLTFA - potential match must be adjudicated before onboarding; "
        "do not contact the client"
    ),

    # Screening — PEP
    "PEP_CONFIRMED": (
        "FINTRAC - PEP determination required at onboarding; "
        "enhanced due diligence mandatory once confirmed"
    ),
    "PEP_DETECTED_NOT_DECLARED": (
        "FINTRAC - PEP detected but not declared by the client; "
        "requires compliance officer review"
    ),
    "PEP_DECLARED_NOT_DETECTED": (
        "FINTRAC - client declared PEP status but no registry match found; "
        "compliance officer should verify the declaration"
    ),
    "NO_SCREENING_INDICATORS": (
        "PCMLTFA - screening completed with no indicators found"
    ),

    # Wealth and funds
    "WEALTH_SUPPORTED": (
        "PCMLTFA - source of wealth and funds verification completed"
    ),
    "WEALTH_SUPPORTED_CRYPTO_PRESENT": (
        "PCMLTFA - wealth supported; crypto funds declared with exchange "
        "records present but crypto origin requires compliance officer review"
    ),
    "WEALTH_SUPPORTED_CROSS_BORDER": (
        "Cross-border transfers increase exposure and require "
        "compliance officer review"
    ),
    "WEALTH_EVIDENCE_INCOMPLETE": (
        "PCMLTFA - source of wealth and funds verification cannot be "
        "completed; required documents missing"
    ),
    "CRYPTO_SOURCE_NOT_ESTABLISHED": (
        "PCMLTFA - crypto funds declared but exchange records not "
        "provided; source of crypto funds cannot be established"
    ),

    # Business — sale
    "BUSINESS_SALE_SUPPORTED": (
        "Business sale confirmed by the corporate registry"
    ),
    "BUSINESS_SALE_UNCONFIRMED": (
        "Corporate registry does not confirm the declared sale"
    ),
    "BUSINESS_SALE_AMOUNT_INCONSISTENT": (
        "Declared sale amount does not match the registry record"
    ),

    # Business — ownership
    "BUSINESS_OWNERSHIP_CONFIRMED": (
        "Business ownership confirmed by the corporate registry"
    ),
    "BUSINESS_OWNERSHIP_INCOME_MISSING": (
        "Ownership confirmed but no evidence of how the client "
        "received money from the business"
    ),

    # Business — errors
    "BUSINESS_NOT_IN_REGISTRY": (
        "Business claim cannot be confirmed without a registry entry"
    ),
    "BUSINESS_REGISTRY_MISMATCH": (
        "Declared company does not match the corporate registry"
    ),
    "BUSINESS_STATUS_UNKNOWN": (
        "Business wealth declared with an unrecognised status"
    ),

    # Risk engine
    "LOW": "Low risk - standard onboarding procedures apply",
    "MEDIUM": "Medium risk - enhanced monitoring recommended",
    "HIGH": "High risk - enhanced due diligence required",
    "CANNOT_CLASSIFY": (
        "Insufficient information to classify risk; "
        "missing documents or declarations must be obtained"
    ),

    # Case summary
    "SUMMARY_GENERATED": E23_EXPLAINABILITY,
}