import { describe, it, expect } from 'vitest';
import {
  applyTemplateVariables,
  appendText,
  extractRequesterName,
  buildTemplateContext,
} from './replyTemplateText';

describe('applyTemplateVariables', () => {
  it('지원하는 모든 변수를 치환한다', () => {
    const body =
      '안녕하세요 {{requester_name}}님. 티켓 {{ticket_number}} 처리 완료했습니다. 담당자 {{officer_name}} 드림.';
    expect(
      applyTemplateVariables(body, {
        requester_name: '홍길동',
        ticket_number: 'T-2026-0001',
        officer_name: '김담당',
      })
    ).toBe('안녕하세요 홍길동님. 티켓 T-2026-0001 처리 완료했습니다. 담당자 김담당 드림.');
  });

  it('일부 변수만 전달되면 누락된 자리표시자는 그대로 둔다', () => {
    const body = '{{requester_name}}님, {{ticket_number}} 담당자 {{officer_name}}입니다.';
    expect(
      applyTemplateVariables(body, {
        requester_name: '이영희',
        ticket_number: '',
      })
    ).toBe('이영희님, {{ticket_number}} 담당자 {{officer_name}}입니다.');
  });

  it('모든 변수가 누락되면 자리표시자를 빈 문자열로 만들지 않고 유지한다', () => {
    const body = '{{requester_name}} / {{ticket_number}} / {{officer_name}}';
    expect(applyTemplateVariables(body, {})).toBe(body);
  });

  it('중괄호 내부 공백이 있는 변수도 치환한다', () => {
    const body = '{{ requester_name }}님 ({{  ticket_number  }}) - {{ officer_name }}';
    expect(
      applyTemplateVariables(body, {
        requester_name: '박민수',
        ticket_number: 'T-10',
        officer_name: '최엔지니어',
      })
    ).toBe('박민수님 (T-10) - 최엔지니어');
  });

  it('지원하지 않는 변수는 그대로 둔다', () => {
    const body = '{{requester_name}}님, {{unknown_var}} 및 {{ date }} 확인 바랍니다.';
    expect(
      applyTemplateVariables(body, {
        requester_name: '홍길동',
      })
    ).toBe('홍길동님, {{unknown_var}} 및 {{ date }} 확인 바랍니다.');
  });
});

describe('appendText', () => {
  it('현재 입력칸이 비어 있거나 공백만 있으면 삽입 텍스트만 반환한다', () => {
    expect(appendText('', '상용구 본문')).toBe('상용구 본문');
    expect(appendText('   \n\t  ', '상용구 본문')).toBe('상용구 본문');
  });

  it('기존 내용이 있으면 빈 줄 하나를 두고 이어 붙인다', () => {
    expect(appendText('기존 조치 내용입니다.', '추가 안내입니다.')).toBe(
      '기존 조치 내용입니다.\n\n추가 안내입니다.'
    );
  });

  it('기존 내용 끝의 공백과 개행을 정리한 뒤 이어 붙인다', () => {
    expect(appendText('기존 조치 내용입니다.\n\n   ', '추가 안내입니다.')).toBe(
      '기존 조치 내용입니다.\n\n추가 안내입니다.'
    );
  });
});

describe('buildTemplateContext / extractRequesterName', () => {
  it('author_name이 없으면 author_id 배열 두 번째 값을 사용한다', () => {
    expect(
      extractRequesterName({ author_name: undefined, author_id: [7, '김사원'] })
    ).toBe('김사원');
    expect(
      buildTemplateContext({
        category: 'network',
        ticket_number: 'T-2026-0099',
        author_name: '',
        author_id: [7, '김사원'],
      })
    ).toEqual({
      category: 'network',
      ticketNumber: 'T-2026-0099',
      requesterName: '김사원',
    });
  });
});
