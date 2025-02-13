class Claim:
    def __init__(self, claim_id, description, amount, status):
        self.claim_id = claim_id
        self.description = description
        self.amount = amount
        self.status = status

    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "description": self.description,
            "amount": self.amount,
            "status": self.status,
        }
