"""
Providers with Trial Credits

Information about providers that offer trial credits (not completely free).
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class TrialCreditProvider:
    """Information about a provider with trial credits."""
    name: str
    credits: str
    duration: str
    models: List[str]
    requires_phone_verification: bool = False
    website: str = ""
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "credits": self.credits,
            "duration": self.duration,
            "models": self.models,
            "requires_phone_verification": self.requires_phone_verification,
            "website": self.website,
            "notes": self.notes,
        }


# Providers with Trial Credits
TRIAL_CREDIT_PROVIDERS = [
    TrialCreditProvider(
        name="Fireworks",
        credits="$1",
        duration="One-time",
        models=["Various open models"],
        requires_phone_verification=False,
        website="https://fireworks.ai",
        notes="One-time credit for new users"
    ),
    TrialCreditProvider(
        name="Baseten",
        credits="$30",
        duration="One-time",
        models=["Any supported model"],
        requires_phone_verification=False,
        website="https://baseten.co",
        notes="Generous one-time credit"
    ),
    TrialCreditProvider(
        name="Nebius",
        credits="$1",
        duration="One-time",
        models=["Various open models"],
        requires_phone_verification=False,
        website="https://nebius.com",
        notes="One-time credit for new users"
    ),
    TrialCreditProvider(
        name="Novita",
        credits="$0.5",
        duration="1 year",
        models=["Various open models"],
        requires_phone_verification=False,
        website="https://novita.ai",
        notes="Small but long-lasting credit"
    ),
    TrialCreditProvider(
        name="AI21",
        credits="$10",
        duration="3 months",
        models=["Jamba family"],
        requires_phone_verification=False,
        website="https://ai21.com",
        notes="Good for testing Jamba models"
    ),
    TrialCreditProvider(
        name="Upstage",
        credits="$10",
        duration="3 months",
        models=["Solar Pro/Mini"],
        requires_phone_verification=False,
        website="https://upstage.ai",
        notes="Good for testing Solar models"
    ),
    TrialCreditProvider(
        name="NLP Cloud",
        credits="$15",
        duration="One-time",
        models=["Various open models"],
        requires_phone_verification=True,
        website="https://nlpcloud.com",
        notes="Requires phone verification"
    ),
    TrialCreditProvider(
        name="Alibaba Cloud",
        credits="1M tokens/model",
        duration="One-time",
        models=["Qwen models"],
        requires_phone_verification=False,
        website="https://alibabacloud.com",
        notes="Per model token allowance"
    ),
    TrialCreditProvider(
        name="Modal",
        credits="$5/month",
        duration="Ongoing",
        models=["Any supported model"],
        requires_phone_verification=False,
        website="https://modal.com",
        notes="Ongoing monthly credit"
    ),
    TrialCreditProvider(
        name="Modal (with payment)",
        credits="$30/month",
        duration="Ongoing",
        models=["Any supported model"],
        requires_phone_verification=False,
        website="https://modal.com",
        notes="Higher ongoing monthly credit with payment method"
    ),
    TrialCreditProvider(
        name="Inference.net",
        credits="$1",
        duration="One-time",
        models=["Various open models"],
        requires_phone_verification=False,
        website="https://inference.net",
        notes="One-time credit for new users"
    ),
    TrialCreditProvider(
        name="Inference.net (survey)",
        credits="$25",
        duration="One-time",
        models=["Various open models"],
        requires_phone_verification=False,
        website="https://inference.net",
        notes="Credit for completing survey"
    ),
    TrialCreditProvider(
        name="Hyperbolic",
        credits="$1",
        duration="One-time",
        models=["DeepSeek V3, Llama 3.3 70B, etc."],
        requires_phone_verification=False,
        website="https://hyperbolic.xyz",
        notes="One-time credit for new users"
    ),
    TrialCreditProvider(
        name="SambaNova Cloud",
        credits="$5",
        duration="3 months",
        models=["deepseek-v3.1/3.2, gemma-4-31b, etc."],
        requires_phone_verification=False,
        website="https://sambanova.ai",
        notes="Good for testing latest models"
    ),
    TrialCreditProvider(
        name="Scaleway",
        credits="1M free tokens",
        duration="One-time",
        models=["20+ models"],
        requires_phone_verification=False,
        website="https://scaleway.com",
        notes="Generous token allowance"
    ),
]


def get_provider_by_name(name: str) -> Optional[TrialCreditProvider]:
    """
    Get a trial credit provider by name.
    
    Args:
        name: Name of the provider
        
    Returns:
        TrialCreditProvider: Provider information or None if not found
    """
    for provider in TRIAL_CREDIT_PROVIDERS:
        if provider.name.lower() == name.lower():
            return provider
    return None


def get_providers_by_credit_amount(min_credits: Optional[float] = None, max_credits: Optional[float] = None) -> List[TrialCreditProvider]:
    """
    Get providers filtered by credit amount.
    
    Args:
        min_credits: Minimum credit amount
        max_credits: Maximum credit amount
        
    Returns:
        List[TrialCreditProvider]: List of matching providers
    """
    matching_providers = []
    
    for provider in TRIAL_CREDIT_PROVIDERS:
        # Extract numeric value from credits string
        credit_str = provider.credits.replace("$", "").replace("/month", "").replace("M", "000000")
        try:
            credit_value = float(credit_str.split()[0])  # Take first part if there are spaces
        except (ValueError, IndexError):
            logger.warning(f"Failed to parse credits for provider {provider.name}: {provider.credits}")
            continue
        
        if (min_credits is None or credit_value >= min_credits) and \
           (max_credits is None or credit_value <= max_credits):
            matching_providers.append(provider)
    
    return matching_providers


def get_providers_by_duration(duration: str) -> List[TrialCreditProvider]:
    """
    Get providers filtered by duration.
    
    Args:
        duration: Duration string (e.g., "One-time", "Ongoing", "3 months")
        
    Returns:
        List[TrialCreditProvider]: List of matching providers
    """
    matching_providers = []
    
    for provider in TRIAL_CREDIT_PROVIDERS:
        if provider.duration.lower() == duration.lower():
            matching_providers.append(provider)
    
    return matching_providers