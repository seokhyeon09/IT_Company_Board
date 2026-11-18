# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from app.schemas.merge import (
    MergeCandidatesResponseDTO,
    TicketMergeRequestDTO,
    TicketMergeResponseDTO,
)


class MergeService:
    """중복 문의 병합 및 후보 추천 서비스."""

    async def merge_ticket(
        self,
        ticket_id: int,
        dto: TicketMergeRequestDTO,
        user_id: int,
    ) -> TicketMergeResponseDTO:
        params = {"ticket_id": ticket_id, **dto.model_dump(exclude_none=True)}
        result = await odoo_client.call_json(
            "/api/v1/tickets/merge",
            params=params,
            user_id=user_id,
        )
        return TicketMergeResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def get_candidates(
        self,
        ticket_id: int,
        user_id: int,
        limit: int = 5,
    ) -> MergeCandidatesResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/tickets/merge-candidates",
            params={"ticket_id": ticket_id, "limit": limit},
            user_id=user_id,
        )
        return MergeCandidatesResponseDTO(
            status="success",
            data=result.get("data", {}),
        )


merge_service = MergeService()
