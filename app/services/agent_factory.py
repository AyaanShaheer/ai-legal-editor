from app.core.config import settings
from app.core.logging import logger


def get_legal_agent():
    """
    Get legal document agent (real or mock)
    
    Returns:
        Agent instance
    """
    
    # Check if Azure OpenAI is configured with valid credentials
    has_valid_config = (
        settings.AZURE_OPENAI_API_KEY and 
        settings.AZURE_OPENAI_API_KEY != "your-key-here" and
        settings.AZURE_OPENAI_ENDPOINT and
        "YOUR-RESOURCE" not in settings.AZURE_OPENAI_ENDPOINT
    )
    
    if has_valid_config:
        try:
            from app.services.llm_agent import LegalDocumentAgent
            agent = LegalDocumentAgent()
            logger.info("✅ Using Azure OpenAI agent")
            return agent
        except Exception as e:
            logger.warning(f"⚠️  Azure OpenAI initialization failed: {str(e)}")
            logger.info("Falling back to mock agent")
    else:
        logger.info("⚠️  Azure OpenAI not configured (using placeholder values)")
    
    # Use mock agent
    from app.services.llm_agent_mock import MockLegalDocumentAgent
    logger.info("✅ Using Mock LLM agent (no API calls)")
    return MockLegalDocumentAgent()
