import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiClient, getErrorMessage } from './client';

function createStorageStub() {
  const store = new Map<string, string>();
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, String(value));
    },
    removeItem: (key: string) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    },
  };
}

describe('client.ts 모듈 기본 설정', () => {
  it('VITE_API_URL 미설정 시에도 import가 동작하고 기본 baseURL을 사용한다', () => {
    expect(apiClient).toBeDefined();
    expect(apiClient.defaults.baseURL).toBe(
      import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    );
  });
});

describe('getErrorMessage', () => {
  it('error.response.data.error.message를 최우선으로 반환한다', () => {
    const err = {
      message: 'Request failed with status code 400',
      response: {
        data: {
          error: { message: '잘못된 요청입니다.' },
          detail: '무시될 상세 메시지',
        },
      },
    };
    expect(getErrorMessage(err)).toBe('잘못된 요청입니다.');
  });

  it('retry_after_seconds가 있으면 재시도 안내 문구를 덧붙인다', () => {
    const err = {
      response: {
        data: {
          error: {
            message: '요청이 너무 많습니다.',
            retry_after_seconds: 30,
          },
        },
      },
    };
    expect(getErrorMessage(err)).toBe('요청이 너무 많습니다. (30초 후 재시도 가능)');
  });

  it('detail이 문자열이면 그대로 반환한다', () => {
    const err = {
      response: {
        data: {
          detail: '접근 권한이 없습니다.',
        },
      },
    };
    expect(getErrorMessage(err)).toBe('접근 권한이 없습니다.');
  });

  it('detail이 Pydantic 422 배열이면 필드명 한글화와 문구 변환 후 쉼표로 결합한다', () => {
    const err = {
      response: {
        data: {
          detail: [
            {
              loc: ['body', 'title'],
              msg: 'String should have at least 5 characters',
            },
            {
              loc: ['body', 'rating_comment'],
              msg: 'String should have at most 500 characters',
            },
            {
              loc: ['body', 'reason'],
              msg: 'Field required',
            },
          ],
        },
      },
    };
    expect(getErrorMessage(err)).toBe(
      '제목은(는) 최소 5자 이상 입력해 주세요., 만족도 한줄평은(는) 최대 500자 이하로 입력해 주세요., 사유을(를) 입력해 주세요.'
    );
  });

  it('error가 null 또는 undefined이면 fallback 메시지를 반환한다', () => {
    expect(getErrorMessage(null)).toBe('오류가 발생했습니다.');
    expect(getErrorMessage(undefined, '커스텀 오류 문구')).toBe('커스텀 오류 문구');
  });

  it('response가 없으면 error.message를 반환하고, 그것도 없으면 fallback을 반환한다', () => {
    expect(getErrorMessage({ message: 'Network Error' })).toBe('Network Error');
    expect(getErrorMessage({}, '연결 실패')).toBe('연결 실패');
  });
});

describe('apiClient 응답 인터셉터 (401 처리)', () => {
  let reloadMock: ReturnType<typeof vi.fn>;
  let localStorageStub: ReturnType<typeof createStorageStub>;
  let sessionStorageStub: ReturnType<typeof createStorageStub>;

  const getRejectedHandler = () => {
    const handlers = (apiClient.interceptors.response as any).handlers as Array<{
      rejected?: (error: unknown) => Promise<never>;
    }>;
    const rejected = handlers[0]?.rejected;
    if (!rejected) {
      throw new Error('응답 인터셉터의 rejected 핸들러를 찾을 수 없습니다.');
    }
    return rejected;
  };

  beforeEach(() => {
    vi.useFakeTimers();
    reloadMock = vi.fn();
    localStorageStub = createStorageStub();
    sessionStorageStub = createStorageStub();
    vi.stubGlobal('localStorage', localStorageStub);
    vi.stubGlobal('sessionStorage', sessionStorageStub);
    vi.stubGlobal('window', { location: { reload: reloadMock } });
  });

  afterEach(() => {
    vi.advanceTimersByTime(1000);
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it('일반 요청 401 시 토큰을 삭제하고 session_expired를 기록하며 1회 reload 후 reject한다', async () => {
    localStorageStub.setItem('access_token', 'jwt-token');
    localStorageStub.setItem('user_info', '{"id":1}');
    const rejected = getRejectedHandler();
    const error = { response: { status: 401 }, config: { url: '/tickets' } };

    await expect(rejected(error)).rejects.toBe(error);

    expect(localStorageStub.getItem('access_token')).toBeNull();
    expect(localStorageStub.getItem('user_info')).toBeNull();
    expect(sessionStorageStub.getItem('session_expired')).toBe('1');
    expect(reloadMock).toHaveBeenCalledTimes(1);

    // 1초 이내 중복 401에는 reload를 다시 호출하지 않는다
    await expect(rejected(error)).rejects.toBe(error);
    expect(reloadMock).toHaveBeenCalledTimes(1);

    // 1초 경과 후에는 다시 reload를 호출한다
    vi.advanceTimersByTime(1000);
    await expect(rejected(error)).rejects.toBe(error);
    expect(reloadMock).toHaveBeenCalledTimes(2);
  });

  it('/auth/login 요청의 401에서는 토큰을 유지하고 reload 없이 reject만 한다', async () => {
    localStorageStub.setItem('access_token', 'jwt-token');
    localStorageStub.setItem('user_info', '{"id":1}');
    const rejected = getRejectedHandler();
    const error = { response: { status: 401 }, config: { url: '/auth/login' } };

    await expect(rejected(error)).rejects.toBe(error);

    expect(localStorageStub.getItem('access_token')).toBe('jwt-token');
    expect(localStorageStub.getItem('user_info')).toBe('{"id":1}');
    expect(sessionStorageStub.getItem('session_expired')).toBeNull();
    expect(reloadMock).not.toHaveBeenCalled();
  });

  it('500 등 다른 상태 코드는 스토리지 변경이나 reload 없이 reject한다', async () => {
    localStorageStub.setItem('access_token', 'jwt-token');
    localStorageStub.setItem('user_info', '{"id":1}');
    const rejected = getRejectedHandler();
    const error = { response: { status: 500 }, config: { url: '/tickets' } };

    await expect(rejected(error)).rejects.toBe(error);

    expect(localStorageStub.getItem('access_token')).toBe('jwt-token');
    expect(localStorageStub.getItem('user_info')).toBe('{"id":1}');
    expect(sessionStorageStub.getItem('session_expired')).toBeNull();
    expect(reloadMock).not.toHaveBeenCalled();
  });
});
