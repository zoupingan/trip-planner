from hello_agents import HelloAgentsLLM

_llm_service = None


def get_llm() -> HelloAgentsLLM:
    global _llm_service

    if _llm_service is None:
        _llm_service = HelloAgentsLLM()
    return _llm_service
