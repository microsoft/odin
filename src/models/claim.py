from decimal import Decimal


class Claim:
    def __init__(
        self,
        user_id: str,
        claim_id: str,
        description: str,
        amount: Decimal,
        status: str,
    ):
        self.user_id = user_id
        self.claim_id = claim_id
        self.description = description
        self.amount = amount
        self.status = status

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "claim_id": self.claim_id,
            "description": self.description,
            "amount": self.amount,
            "status": self.status,
        }
