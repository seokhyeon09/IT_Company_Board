# -*- coding: utf-8 -*-
from typing import Optional
from app.client.odoo_client import odoo_client
from app.schemas.reply_template import (
    ReplyTemplateCreateDTO,
    ReplyTemplateDeleteResponseDTO,
    ReplyTemplateListResponseDTO,
    ReplyTemplateResponseDTO,
    ReplyTemplateUpdateDTO,
)


class ReplyTemplateService:
    """IT 담당자 답변 상용구 CRUD 서비스."""

    async def list_templates(
        self,
        user_id: int,
        category: Optional[str] = None,
    ) -> ReplyTemplateListResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/reply-templates/list",
            params={"category": category},
            user_id=user_id,
        )
        return ReplyTemplateListResponseDTO(
            status="success",
            data=result.get("data", []),
        )

    async def create_template(
        self,
        dto: ReplyTemplateCreateDTO,
        user_id: int,
    ) -> ReplyTemplateResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/reply-templates/create",
            params=dto.model_dump(),
            user_id=user_id,
        )
        return ReplyTemplateResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def update_template(
        self,
        template_id: int,
        dto: ReplyTemplateUpdateDTO,
        user_id: int,
    ) -> ReplyTemplateResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/reply-templates/update",
            params={"template_id": template_id, **dto.model_dump()},
            user_id=user_id,
        )
        return ReplyTemplateResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def delete_template(
        self,
        template_id: int,
        user_id: int,
    ) -> ReplyTemplateDeleteResponseDTO:
        await odoo_client.call_json(
            "/api/v1/reply-templates/delete",
            params={"template_id": template_id},
            user_id=user_id,
        )
        return ReplyTemplateDeleteResponseDTO(status="success")


reply_template_service = ReplyTemplateService()
