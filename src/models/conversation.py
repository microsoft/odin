class Conversation:
    def __init__(self, conversation_id, claim_id, messages):
        self.conversation_id = conversation_id
        self.claim_id = claim_id
        # messages should be https://python.langchain.com/api_reference/core/messages/langchain_core.messages.base.BaseMessage.html#basemessage
        self.messages = messages
