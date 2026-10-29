import { TicketCategory } from '../../../shared/types/common';
import { TicketTemplate } from '../types/ticketTemplate';

export const TICKET_TEMPLATES: Record<TicketCategory, TicketTemplate> = {
  sw: {
    category: 'sw',
    titlePlaceholder: '예: ERP 월간 결산 보고서 PDF 변환 시 폰트 깨짐 오류',
    description: '문제가 발생한 프로그램명과 재현 절차를 입력해 주시면 빠르게 확인됩니다.',
    fields: [
      {
        key: 'software_name',
        label: '소프트웨어명',
        type: 'text',
        required: true,
        placeholder: '예: 사내 그룹웨어 / ERP / Chrome / MS Office',
      },
      {
        key: 'request_type',
        label: '요청 유형',
        type: 'select',
        required: true,
        options: [
          { value: '오류/버그 조치', label: '오류/버그 조치' },
          { value: '신규 설치 요청', label: '신규 설치 요청' },
          { value: '라이선스/인증 만료', label: '라이선스/인증 만료' },
          { value: '버전 업데이트', label: '버전 업데이트' },
        ],
      },
      {
        key: 'version_info',
        label: '버전 및 환경 정보',
        type: 'text',
        required: false,
        placeholder: '예: Windows 11 / Chrome v128 (선택)',
      },
      {
        key: 'reproduction_steps',
        label: '증상 및 재현 절차',
        type: 'textarea',
        required: true,
        placeholder: '어떤 메뉴에서 어떤 동작을 할 때 오류가 나는지 순서대로 적어주세요.',
      },
    ],
  },
  hw: {
    category: 'hw',
    titlePlaceholder: '예: 보조 모니터 전원이 들어오지 않고 화면이 깜빡입니다.',
    description: '장비 모델 또는 자산번호와 증상을 입력해 주세요.',
    fields: [
      {
        key: 'asset_or_model',
        label: '자산번호 또는 모델명',
        type: 'text',
        required: true,
        placeholder: '예: PC-2026-042 / ThinkPad X1 / 27인치 모니터',
      },
      {
        key: 'symptom',
        label: '발생 증상',
        type: 'textarea',
        required: true,
        placeholder: '전원 불량, 화면 왜곡, 소음 등 구체적인 증상을 적어주세요.',
      },
      {
        key: 'occurred_at',
        label: '발생 시점',
        type: 'text',
        required: false,
        placeholder: '예: 금일 오전 9시 출근 직후 (선택)',
      },
      {
        key: 'tried_actions',
        label: '조치 시도 여부',
        type: 'text',
        required: false,
        placeholder: '예: 재부팅 및 케이블 재연결 시도했으나 동일 (선택)',
      },
    ],
    priorityHint: {
      recommendedPriority: '3',
      message: '[긴급도 안내] 장비 고장으로 대체 기기 없이 업무가 전면 중단된 경우 긴급도를 [긴급]으로 선택해 주세요.',
    },
  },
  network: {
    category: 'network',
    titlePlaceholder: '예: 본사 4층 대회의실 Wi-Fi 간헐적 끊김 및 패킷 손실 점검',
    description: '네트워크 구분과 영향 범위를 선택해 주시면 우선순위에 맞춰 대응합니다.',
    fields: [
      {
        key: 'issue_type',
        label: '문제 유형',
        type: 'select',
        required: true,
        options: [
          { value: '사내 유선망', label: '사내 유선망' },
          { value: '사내 Wi-Fi', label: '사내 Wi-Fi' },
          { value: 'SSL-VPN (재택)', label: 'SSL-VPN (재택)' },
          { value: '외부 인터넷 접속', label: '외부 인터넷 접속' },
        ],
      },
      {
        key: 'impact_scope',
        label: '영향 범위',
        type: 'select',
        required: true,
        options: [
          { value: '본인 PC만 발생', label: '본인 PC만 발생' },
          { value: '같은 자리/회의실', label: '같은 자리/회의실' },
          { value: '팀/부서 전체', label: '팀/부서 전체' },
          { value: '전사 공통', label: '전사 공통' },
        ],
      },
      {
        key: 'location_or_ip',
        label: '위치 또는 IP 주소',
        type: 'text',
        required: false,
        placeholder: '예: 본사 4층 대회의실 / 10.10.20.15 / 자택 (선택)',
      },
      {
        key: 'error_detail',
        label: '오류 메시지 및 상세 증상',
        type: 'textarea',
        required: true,
        placeholder: '에러 코드(예: 809 타임아웃)나 연결 끊김 현상을 적어주세요.',
      },
    ],
    priorityHint: {
      whenField: 'impact_scope',
      whenValues: ['팀/부서 전체', '전사 공통'],
      recommendedPriority: '3',
      message: '[긴급도 안내] 팀/부서 전체 이상 범위의 네트워크 장애는 긴급도를 [긴급]으로 선택하는 것을 권장합니다.',
    },
  },
  account: {
    category: 'account',
    titlePlaceholder: '예: ERP 재무회계 결산 모듈 조회 권한 신청',
    description: '대상 시스템과 요청 유형, 신청 사유를 정확히 입력해 주세요.',
    fields: [
      {
        key: 'target_system',
        label: '대상 시스템',
        type: 'select',
        required: true,
        options: [
          { value: 'ERP 시스템', label: 'ERP 시스템' },
          { value: '그룹웨어/메일', label: '그룹웨어/메일' },
          { value: '사내 SSO 포털', label: '사내 SSO 포털' },
          { value: 'VPN/원격접속', label: 'VPN/원격접속' },
          { value: 'DB/서버 인프라', label: 'DB/서버 인프라' },
          { value: '기타 사내 시스템', label: '기타 사내 시스템' },
        ],
      },
      {
        key: 'request_type',
        label: '요청 유형',
        type: 'select',
        required: true,
        options: [
          { value: '권한 신청/변경', label: '권한 신청/변경' },
          { value: '계정 잠금 해제', label: '계정 잠금 해제' },
          { value: '비밀번호 초기화', label: '비밀번호 초기화' },
          { value: '신규 계정 발급', label: '신규 계정 발급' },
        ],
      },
      {
        key: 'permission_level',
        label: '요청 권한 수준',
        type: 'text',
        required: false,
        placeholder: '예: 조회 전용 / 읽기·쓰기 / 24시간 임시 권한 (선택)',
      },
      {
        key: 'reason',
        label: '신청 사유 및 상세 내용',
        type: 'textarea',
        required: true,
        placeholder: '업무 목적, 대상 계정 ID, 필요 기간 등을 구체적으로 적어주세요.',
      },
    ],
    priorityHint: {
      whenField: 'request_type',
      whenValues: ['계정 잠금 해제', '비밀번호 초기화'],
      recommendedPriority: '2',
      message: '[긴급도 안내] 계정 잠금이나 비밀번호 초기화로 로그인이 불가한 경우 긴급도를 [높음] 이상으로 권장합니다.',
    },
  },
  etc: {
    category: 'etc',
    titlePlaceholder: '예: 5층 중회의실 프로젝터 리모컨 및 HDMI 젠더 확인 요청',
    description: '기타 일반 문의 사항을 자유롭게 작성해 주세요.',
    fields: [],
  },
};

export function getTemplateForCategory(category: string): TicketTemplate {
  const key = (category in TICKET_TEMPLATES ? category : 'etc') as TicketCategory;
  return TICKET_TEMPLATES[key];
}
