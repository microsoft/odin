from typing import Dict


class Conversation:
    def __init__(self, conversation_id, claim_id, messages: list[Dict[str, str]]):
        self.conversation_id = conversation_id
        self.claim_id = claim_id
        # messages should be https://python.langchain.com/api_reference/core/messages/langchain_core.messages.base.BaseMessage.html#basemessage
        self.messages = messages
