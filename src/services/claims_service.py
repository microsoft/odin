from models.claim import Claim


class ClaimsService:
    def __init__(self):
        self.claims = [
            Claim(claim_id="33c1828d-a26a-4eea-8581-0088357b58b9", description="Claim about a bad back due to many hours of sitting", amount=100.0, status="Approved"),
            Claim(claim_id="8f7ae2b0-e6b6-4596-b309-fe8fb7f58f9c", description="Claim about an awful haircut", amount=200.0, status="Pending"),
            Claim(claim_id="281aaa3b-f616-46e7-91ef-0d4e6f09047f", description="Claim about inventing the question mark", amount=300.0, status="Denied"),
            Claim(claim_id="194ccf91-324d-484a-b849-d0294d099e09", description="Claim to Iron Throne of Westeros", amount=400.0, status="Pending")
        ]

    def get_all(self) -> list[Claim]:
        return self.claims

    def get_by_id(self, claim_id: str) -> Claim:
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim

    def upsert(self, claim: Claim) -> None:
        for i, existing_claim in enumerate(self.claims):
            if existing_claim.claim_id == claim.claim_id:
                self.claims[i] = claim
                return
        self.claims.append(claim)

    def delete(self, claim_id: str) -> None:
        self.claims = [claim for claim in self.claims if claim.claim_id != claim_id]


claims_service = ClaimsService()

__all__ = [claims_service]
