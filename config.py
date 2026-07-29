import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# Model
MODEL = "groq/llama-3.1-8b-instant"

# Paths
TRACES_DIR = "traces"

# Compliance rules reference
COMPLIANCE_RULES = {
  "pep_screening": "FINTRAC - PEP determination mandatory at onboarding",
    "sanctions_screening": "PCMLTFA s.9.6 - sanctions screening required before account opening",
    "source_of_funds": "PCMLTFA - source of funds verification required for HNW clients",
    "ai_explainability": "OSFI E-23 - AI-assisted decisions must be explainable and documented",
}