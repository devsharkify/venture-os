"""Stub. Replace with a real LLM provider call when you wire one."""


class UserMessage:
    def __init__(self, text: str = ""):
        self.text = text


class LlmChat:
    def __init__(self, api_key: str = "", session_id: str = "", system_message: str = ""):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self._model_provider = None
        self._model_name = None

    def with_model(self, provider: str, name: str):
        self._model_provider = provider
        self._model_name = name
        return self

    async def send_message(self, msg: UserMessage):
        raise NotImplementedError(
            "emergentintegrations is a stub. Wire a real LLM provider "
            "(google-generativeai for Gemini, openai for GPT, etc.) and "
            "swap the import."
        )
