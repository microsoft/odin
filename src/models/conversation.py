class Conversation:
    def __init__(self, id, claim_id, messages):
        self.id = id
        self.claim_id = claim_id
        # messages should be https://python.langchain.com/api_reference/core/messages/langchain_core.messages.base.BaseMessage.html#basemessage
        self.messages = messages
