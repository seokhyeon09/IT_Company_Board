# -*- coding: utf-8 -*-
from app.client.odoo_client import odoo_client
from app.schemas.bulk import BulkTicketResponseDTO, TicketBulkRequestDTO
from app.schemas.note import InternalNoteCreateDTO, InternalNoteResponseDTO


class BulkNoteService:
    """티켓 일괄 처리 및 담당자 내부 메모 서비스."""

    async def bulk_action(self, dto: TicketBulkRequestDTO, user_id: int) -> BulkTicketResponseDTO:
        params = dto.model_dump(exclude_none=True)
        result = await odoo_client.call_json(
            "/api/v1/tickets/bulk",
            params=params,
            user_id=user_id,
            timeout=30.0,
        )
        return BulkTicketResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def add_internal_note(
        self,
        ticket_id: int,
        dto: InternalNoteCreateDTO,
        user_id: int,
    ) -> InternalNoteResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/tickets/notes/add",
            params={"ticket_id": ticket_id, "content": dto.content},
            user_id=user_id,
        )
        return InternalNoteResponseDTO(
            status="success",
            data=result.get("data", {}),
        )


bulk_note_service = BulkNoteService()
