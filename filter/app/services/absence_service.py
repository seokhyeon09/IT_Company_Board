# -*- coding: utf-8 -*-
from datetime import date
from fastapi import HTTPException, status
from app.client.odoo_client import odoo_client
from app.core.messages import MSG_ABSENT_UNTIL_PAST
from app.schemas.absence import OfficerAbsenceResponseDTO, OfficerAbsenceUpdateDTO


class AbsenceService:
    """담당자 본인 부재 설정 조회 및 변경 서비스."""

    async def get_my_absence(self, user_id: int) -> OfficerAbsenceResponseDTO:
        result = await odoo_client.call_json(
            "/api/v1/officers/me/absence/get",
            params={},
            user_id=user_id,
        )
        return OfficerAbsenceResponseDTO(
            status="success",
            data=result.get("data", {}),
        )

    async def update_my_absence(
        self,
        dto: OfficerAbsenceUpdateDTO,
        user_id: int,
    ) -> OfficerAbsenceResponseDTO:
        if not dto.is_absent:
            params = {"is_absent": False, "absent_until": None}
        else:
            if dto.absent_until is not None and date.fromisoformat(dto.absent_until) < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=MSG_ABSENT_UNTIL_PAST,
                )
            params = {"is_absent": True, "absent_until": dto.absent_until}

        result = await odoo_client.call_json(
            "/api/v1/officers/me/absence/set",
            params=params,
            user_id=user_id,
        )
        return OfficerAbsenceResponseDTO(
            status="success",
            data=result.get("data", {}),
        )


absence_service = AbsenceService()
