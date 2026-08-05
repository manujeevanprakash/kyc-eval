import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# Model
MODEL = os.getenv("MODEL", "groq/openai/gpt-oss-120b")

# Paths
TRACES_DIR = "traces"


# Regulatory basis per finding.
#
# The citation names the obligation the decision was made under, not the
# obligation to keep a record of it. An examiner asking why a client was
# treated a certain way should read the rule that required it.
#
# Note what is absent. OSFI E-23 governs models. The four agents below are
# deterministic and apply rules rather than statistical methods, so they
# cite the KYC and AML obligation they are executing. Only the Case Summary
# agent uses an LLM, and it is the only component that cites E-23.
REGULATORY_BASIS = {
    # Identity
    "IDENTITY_VERIFIED":
        "PCMLTFA - identity verification required before account opening",
    "IDENTITY_INCOMPLETE":
        "PCMLTFA - identity verification required before account opening",

    # Screening - sanctions
    "SANCTIONS_MATCH_CONFIRMED":
        "PCMLTFA s.9.6 - dealings prohibited with a listed person; "
        "property must be reported via LPEPR",
    "SANCTIONS_POTENTIAL_MATCH":
        "PCMLTFA s.9.6 - candidate match requires adjudication before "
        "onboarding; disclosure to the client is prohibited",

    # Screening - PEP and cross-border
    "PEP_CONFIRMED":
        "FINTRAC - PEP determination required at onboarding; enhanced "
        "due diligence mandatory once confirmed",
    "PEP_DETECTED_NOT_DECLARED":
        "FINTRAC - PEP determination required at onboarding; enhanced "
        "due diligence mandatory once confirmed",
    "PEP_DECLARED_NOT_DETECTED":
        "FINTRAC - PEP determination required at onboarding; enhanced "
        "due diligence mandatory once confirmed",
    "CROSS_BORDER_FLAGGED":
        "PCMLTFA - electronic funds transfer reporting required for "
        "cross-border transfers of CAD 10,000 or more",
    "NO_SCREENING_INDICATORS":
        "PCMLTFA s.9.6 - sanctions screening performed, no match returned",

    # Wealth and funds
    "WEALTH_SUPPORTED":
        "PCMLTFA - source of wealth and source of funds verification "
        "required for high-net-worth clients",
    "WEALTH_EVIDENCE_INCOMPLETE":
        "PCMLTFA - source of wealth and source of funds verification "
        "required for high-net-worth clients",
    "WEALTH_SUPPORTED_CRYPTO_PRESENT":
        "PCMLTFA virtual currency amendments - source of virtual currency "
        "must be verified and transactions screened",
    "CRYPTO_SOURCE_NOT_ESTABLISHED":
        "PCMLTFA virtual currency amendments - source of virtual currency "
        "must be verified and transactions screened",

    # Business structure
    "BUSINESS_SALE_SUPPORTED":
        "FINTRAC - beneficial ownership confirmation; 25 percent control "
        "threshold applies to corporate structures",
    "BUSINESS_DOCUMENTS_MISSING":
        "FINTRAC - beneficial ownership confirmation; 25 percent control "
        "threshold applies to corporate structures",
    "REGISTRY_MATCH_NOT_FOUND":
        "FINTRAC - beneficial ownership confirmation; 25 percent control "
        "threshold applies to corporate structures",
    "SALE_AMOUNT_INCONSISTENT":
        "FINTRAC - beneficial ownership confirmation; 25 percent control "
        "threshold applies to corporate structures",

    # Risk engine outcomes
    "LOW":
        "FINTRAC - risk-based approach; a client risk rating is required "
        "for every business relationship",
    "MEDIUM":
        "FINTRAC - risk-based approach; a client risk rating is required "
        "for every business relationship",
    "HIGH":
        "FINTRAC - enhanced due diligence required for high-risk clients",
    "CANNOT_CLASSIFY":
        "FINTRAC - a client risk rating cannot be assigned until the "
        "required information is obtained",
}

# The only component in this workflow that uses a model.
E23_EXPLAINABILITY = (
    "OSFI E-23 - AI-assisted output must be explainable, documented "
    "and independently reviewable"
)