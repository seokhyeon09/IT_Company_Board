import { describe, it, expect } from 'vitest';
import { defaultCsvFilename, parseContentDispositionFilename } from './contentDisposition';

describe('parseContentDispositionFilename', () => {
  it('따옴표가 있는 filename을 추출한다', () => {
    expect(parseContentDispositionFilename('attachment; filename="tickets_20261118.csv"')).toBe(
      'tickets_20261118.csv'
    );
  });

  it('따옴표가 없는 filename을 추출한다', () => {
    expect(parseContentDispositionFilename('attachment; filename=tickets_20261118.csv')).toBe(
      'tickets_20261118.csv'
    );
  });

  it('헤더가 없거나 filename 파라미터가 없으면 null을 반환한다', () => {
    expect(parseContentDispositionFilename(undefined)).toBeNull();
    expect(parseContentDispositionFilename(null)).toBeNull();
    expect(parseContentDispositionFilename('')).toBeNull();
    expect(parseContentDispositionFilename('attachment')).toBeNull();
  });

  it('filename 값이 비어 있으면 null을 반환한다', () => {
    expect(parseContentDispositionFilename('attachment; filename=""')).toBeNull();
    expect(parseContentDispositionFilename('attachment; filename="   "')).toBeNull();
    expect(parseContentDispositionFilename('attachment; filename=')).toBeNull();
  });
});

describe('defaultCsvFilename', () => {
  it('tickets_YYYYMMDD.csv 기본 파일명을 생성한다', () => {
    expect(defaultCsvFilename(new Date(2026, 10, 18))).toBe('tickets_20261118.csv');
  });
});
