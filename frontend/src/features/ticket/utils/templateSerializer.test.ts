import { describe, it, expect } from 'vitest';
import { getTemplateForCategory } from '../templates/ticketTemplates';
import {
  buildInitialTemplateValues,
  hasAnyTemplateInput,
  resolvePriorityHint,
  serializeTemplateContent,
  validateTemplateValues,
} from './templateSerializer';

describe('templateSerializer pure unit tests', () => {
  it('1. buildInitialTemplateValues sets default select options and empty text fields', () => {
    const swTpl = getTemplateForCategory('sw');
    const init = buildInitialTemplateValues(swTpl);
    expect(init.software_name).toBe('');
    expect(init.request_type).toBe('오류/버그 조치');
    expect(init.version_info).toBe('');
    expect(init.reproduction_steps).toBe('');
  });

  it('2. validateTemplateValues catches missing required fields in order with Korean message', () => {
    const accountTpl = getTemplateForCategory('account');
    const init = buildInitialTemplateValues(accountTpl);
    const res1 = validateTemplateValues(accountTpl, init);
    expect(res1.valid).toBe(false);
    expect(res1.missingKey).toBe('reason');
    expect(res1.error).toBe("'신청 사유 및 상세 내용' 항목을 입력해 주세요.");

    const filled = { ...init, reason: '월말 정산 업무 권한 필요' };
    const res2 = validateTemplateValues(accountTpl, filled);
    expect(res2.valid).toBe(true);
    expect(res2.error).toBeNull();
  });

  it('3. serializeTemplateContent formats [Label] Value lines and omits empty optional fields', () => {
    const accountTpl = getTemplateForCategory('account');
    const values = {
      target_system: 'ERP 시스템',
      request_type: '권한 신청/변경',
      permission_level: '   ',
      reason: '월말 정산 업무 지원',
    };
    const serialized = serializeTemplateContent(accountTpl, values);
    expect(serialized).toBe(
      '[대상 시스템] ERP 시스템\n[요청 유형] 권한 신청/변경\n[신청 사유 및 상세 내용] 월말 정산 업무 지원'
    );
  });

  it('4. serializeTemplateContent includes optional fields when provided', () => {
    const hwTpl = getTemplateForCategory('hw');
    const values = {
      asset_or_model: 'PC-2026-042',
      symptom: '부팅 시 블루스크린 발생',
      occurred_at: '오늘 오전 9시',
      tried_actions: '메모리 재장착',
    };
    const serialized = serializeTemplateContent(hwTpl, values);
    expect(serialized).toContain('[자산번호 또는 모델명] PC-2026-042');
    expect(serialized).toContain('[발생 증상] 부팅 시 블루스크린 발생');
    expect(serialized).toContain('[발생 시점] 오늘 오전 9시');
    expect(serialized).toContain('[조치 시도 여부] 메모리 재장착');
  });

  it('5. hasAnyTemplateInput returns false for untouched defaults and true after user edits', () => {
    const swTpl = getTemplateForCategory('sw');
    const init = buildInitialTemplateValues(swTpl);
    expect(hasAnyTemplateInput(swTpl, init)).toBe(false);

    const modified = { ...init, software_name: 'ERP' };
    expect(hasAnyTemplateInput(swTpl, modified)).toBe(true);
  });

  it('6. resolvePriorityHint triggers conditionally for account and network templates', () => {
    const accountTpl = getTemplateForCategory('account');
    const initAcc = buildInitialTemplateValues(accountTpl);
    expect(resolvePriorityHint(accountTpl, initAcc)).toBeNull();

    const lockedAcc = { ...initAcc, request_type: '계정 잠금 해제' };
    const hintAcc = resolvePriorityHint(accountTpl, lockedAcc);
    expect(hintAcc).not.toBeNull();
    expect(hintAcc?.recommendedPriority).toBe('2');

    const netTpl = getTemplateForCategory('network');
    const initNet = buildInitialTemplateValues(netTpl);
    expect(resolvePriorityHint(netTpl, initNet)).toBeNull();
    const teamNet = { ...initNet, impact_scope: '팀/부서 전체' };
    expect(resolvePriorityHint(netTpl, teamNet)?.recommendedPriority).toBe('3');
  });

  it('7. resolvePriorityHint always returns hint for hw template', () => {
    const hwTpl = getTemplateForCategory('hw');
    const initHw = buildInitialTemplateValues(hwTpl);
    expect(resolvePriorityHint(hwTpl, initHw)?.recommendedPriority).toBe('3');
  });

  it('8. etc category has empty template fields and passes validation', () => {
    const etcTpl = getTemplateForCategory('etc');
    expect(etcTpl.fields).toHaveLength(0);
    expect(validateTemplateValues(etcTpl, {}).valid).toBe(true);
  });
});
