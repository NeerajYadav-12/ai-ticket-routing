import logging
from .base import ClassifierProvider
from .rule_provider import RuleBasedProvider

log = logging.getLogger("classifier")


def get_provider() -> ClassifierProvider:
    choice = (__import__("os").getenv("CLASSIFIER_PROVIDER") or "local").lower()
    if choice == "openai":
        try:
            from .openai_provider import OpenAIProvider
            provider = OpenAIProvider()
            if not provider.api_key:
                raise RuntimeError("OPENAI_API_KEY not set")
            return provider
        except Exception as e:  # fall back
            log.warning("OpenAI provider unavailable (%s); falling back to rules", e)
    elif choice == "local":
        try:
            from .local_provider import LocalZeroShotProvider
            return LocalZeroShotProvider()
        except Exception as e:
            log.warning("Local zero-shot model unavailable (%s); falling back to rules", e)
    return RuleBasedProvider()
