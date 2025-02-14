from models.claim import Claim


class ClaimsService:
    def __init__(self):
        self.claims = [
            Claim(claim_id='1234', description="Claim 1", amount=100.0, status="Pending"),
            Claim(claim_id='4321', description="Claim 2", amount=200.0, status="Approved"),
        ]

    def get_all(self) -> list[Claim]:
        return self.claims

    def get_by_id(self, claim_id: int) -> Claim:
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim

    def upsert(self, claim: Claim) -> None:
        for i, existing_claim in enumerate(self.claims):
            if existing_claim.claim_id == claim.claim_id:
                self.claims[i] = claim
                return
        self.claims.append(claim)

    def delete(self, claim_id: int) -> None:
        self.claims = [claim for claim in self.claims if claim.claim_id != claim_id]


claims_service = ClaimsService()

__all__ = [claims_service]
