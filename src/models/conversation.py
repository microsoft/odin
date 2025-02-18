from typing import Dict


class Conversation:
    def __init__(
        self,
        id: str,
        claim_id: str,
        user_id: str,
        user_group_id: str,
        messages: list[Dict[str, str]],
    ):
        self.id = id
        self.claim_id = claim_id
        self.user_id = user_id
        self.user_group_id = user_group_id
        # messages should be https://python.langchain.com/api_reference/core/messages/langchain_core.messages.base.BaseMessage.html#basemessage
        self.messages = messages

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "user_id": self.user_id,
            "user_group_id": self.user_group_id,
            "messages": self.messages
        }
