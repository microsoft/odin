from models.claim import Claim


class ClaimsService:
    def __init__(self):
        self.claims = [
            Claim(claim_id=1, description="Claim 1", amount=100.0, status="Pending"),
            Claim(claim_id=2, description="Claim 2", amount=200.0, status="Approved"),
            Claim(claim_id=3, description="Claim 3", amount=300.0, status="Denied"),
            Claim(claim_id=4, description="Claim 4", amount=400.0, status="Pending"),
            Claim(claim_id=5, description="Claim 5", amount=500.0, status="Approved"),
            Claim(claim_id=6, description="Claim 6", amount=600.0, status="Denied"),
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

__all__ = ["claims_service"]
