import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Handle 401 Logout
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      if (window.location.pathname !== '/login') {
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

// Helper to safely format error messages from FastAPI (including 422 array details)
const fieldNameMap: Record<string, string> = {
  resolution_note: '조치 내용',
  title: '제목',
  content: '상세 내용',
  category: '분류',
  priority: '우선순위',
  reason: '사유',
  note: '사유',
  rating: '만족도 점수',
  rating_comment: '만족도 한줄평',
};

function translatePydanticMsg(field: string, msg: string): string {
  const label = fieldNameMap[field] || '';
  const minMatch = msg.match(/at least (\d+) characters/i);
  if (minMatch) {
    return `${label ? `${label}은(는) ` : ''}최소 ${minMatch[1]}자 이상 입력해 주세요.`;
  }
  const maxMatch = msg.match(/at most (\d+) characters/i);
  if (maxMatch) {
    return `${label ? `${label}은(는) ` : ''}최대 ${maxMatch[1]}자 이하로 입력해 주세요.`;
  }
  if (/field required/i.test(msg)) {
    return `${label ? `${label}을(를) ` : '필수 항목을 '}입력해 주세요.`;
  }
  return label ? `${label}: ${msg}` : msg;
}

export function getErrorMessage(error: any, fallback = '오류가 발생했습니다.'): string {
  if (!error) return fallback;
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d: any) => {
        const field = Array.isArray(d.loc) && d.loc.length > 0 ? String(d.loc[d.loc.length - 1]) : '';
        return translatePydanticMsg(field, String(d.msg || ''));
      })
      .join(', ');
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  return error.message || fallback;
}
