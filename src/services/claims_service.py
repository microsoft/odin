from models.claim import Claim


class ClaimsService:
    def __init__(self):
        self.claims = [
            Claim(
                user_id="00000000-0000-0000-0000-000000000000",
                claim_id="33c1828d-a26a-4eea-8581-0088357b58b9",
                description="Claim about a bad back due to many hours of sitting",
                amount=100.0,
                status="Approved",
            ),
            Claim(
                user_id="00000000-0000-0000-0000-000000000000",
                claim_id="8f7ae2b0-e6b6-4596-b309-fe8fb7f58f9c",
                description="Claim about an awful haircut",
                amount=200.0,
                status="Pending",
            ),
            Claim(
                user_id="00000000-0000-0000-0000-000000000000",
                claim_id="281aaa3b-f616-46e7-91ef-0d4e6f09047f",
                description="Claim about inventing the question mark",
                amount=300.0,
                status="Denied",
            ),
            Claim(
                user_id="00000000-0000-0000-0000-000000000000",
                claim_id="194ccf91-324d-484a-b849-d0294d099e09",
                description="Claim to Iron Throne of Westeros",
                amount=400.0,
                status="Pending",
            )
        ]

    def get_all(self, user_id: str) -> list[Claim]:
        return [claim for claim in self.claims if claim.user_id == user_id]

    def get_by_id(self, user_id: str, claim_id: str) -> Claim:
        for claim in self.claims:
            if claim.claim_id == claim_id and claim.user_id == user_id:
                return claim

    def upsert(self, claim: Claim) -> None:
        for i, existing_claim in enumerate(self.claims):
            if (
                existing_claim.claim_id == claim.claim_id
                and existing_claim.user_id == claim.user_id
            ):
                self.claims[i] = claim
                return
        self.claims.append(claim)

    def delete(self, user_id, claim_id: str) -> None:
        self.claims = [
            claim
            for claim in self.claims
            if claim.claim_id != claim_id and claim.user_id == user_id
        ]


claims_service = ClaimsService()

__all__ = [claims_service]
