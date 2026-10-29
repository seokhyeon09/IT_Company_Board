/**
 * 시간(hour) 단위 MTTR 수치를 사용자 친화적인 한국어 문자열로 포맷한다.
 * - 0 이하 또는 측정 건수가 0이면 fallback 문구('집계 데이터 없음' 또는 '-') 반환
 * - 1시간 미만이면 분 단위('30분')
 * - 24시간 미만이면 소수 1자리 시간('2.5시간')
 * - 24시간 이상이면 일 + 시간('1일 4.0시간')
 */
export function formatResolutionHours(
  hours?: number | null,
  measuredCount?: number,
  emptyLabel: string = '집계 데이터 없음'
): string {
  if (measuredCount !== undefined && measuredCount <= 0) {
    return emptyLabel;
  }
  if (hours === undefined || hours === null || hours <= 0) {
    return emptyLabel;
  }
  if (hours < 1) {
    const mins = Math.max(1, Math.round(hours * 60));
    return `${mins}분`;
  }
  if (hours < 24) {
    return `${Number(hours.toFixed(1))}시간`;
  }
  const days = Math.floor(hours / 24);
  const remHours = Number((hours - days * 24).toFixed(1));
  return remHours > 0 ? `${days}일 ${remHours}시간` : `${days}일`;
}
