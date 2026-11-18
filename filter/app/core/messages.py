# -*- coding: utf-8 -*-
"""User-facing gateway error message constants (Korean)."""

MSG_LOGIN_FAILED = "아이디 또는 비밀번호가 올바르지 않습니다."
MSG_AUTH_INVALID = "인증이 만료되었거나 유효하지 않습니다. 다시 로그인해 주세요."
MSG_OFFICER_REQUIRED = "IT 담당자 이상 권한이 필요한 작업입니다."

MSG_BACKEND_ERROR = "백엔드 서버 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
MSG_BACKEND_UNAVAILABLE = "백엔드 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."
MSG_BACKEND_TIMEOUT = "백엔드 서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."
MSG_CONFLICT_DEFAULT = "다른 사용자가 먼저 수정했습니다. 새로고침 후 다시 시도해 주세요."
MSG_RPC_ERROR_DEFAULT = "요청을 처리하지 못했습니다."
MSG_INTERNAL_ERROR = "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
MSG_ABSENT_UNTIL_PAST = "부재 종료일은 오늘 이후 날짜여야 합니다."
MSG_ABSENT_UNTIL_INVALID = "부재 종료일 형식이 올바르지 않습니다. (YYYY-MM-DD)"

MSG_REPORT_DATE_INVALID = "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)"
MSG_REPORT_DATE_ORDER = "시작일이 종료일보다 늦을 수 없습니다."
MSG_REPORT_RANGE_EXCEEDED = "조회 기간은 최대 366일입니다."
MSG_REPORT_UNIT_INVALID = "집계 단위는 week 또는 month여야 합니다."
MSG_REPORT_CATEGORY_INVALID = "유효하지 않은 분야입니다."

MSG_BULK_EMPTY_TICKETS = "선택된 문의가 없습니다."
MSG_BULK_MAX_TICKETS = "한 번에 최대 50건까지 처리할 수 있습니다."
MSG_BULK_INVALID_ID = "선택된 문의 ID가 올바르지 않습니다."
MSG_BULK_INVALID_ACTION = "지원하지 않는 일괄 작업입니다."
MSG_BULK_OFFICER_REQUIRED = "담당자를 선택해 주세요."
MSG_BULK_REASON_TOO_LONG = "인계 사유는 최대 500자까지 입력할 수 있습니다."
MSG_BULK_NOTE_TOO_LONG = "종결 메모는 최대 2000자까지 입력할 수 있습니다."

MSG_NOTE_EMPTY = "내용을 입력해 주세요."
MSG_NOTE_TOO_LONG = "메모는 최대 2000자까지 입력할 수 있습니다."

MSG_MERGE_TARGET_REQUIRED = "병합 대상 문의를 선택해 주세요."
MSG_MERGE_REASON_TOO_LONG = "병합 사유는 최대 500자까지 입력할 수 있습니다."
