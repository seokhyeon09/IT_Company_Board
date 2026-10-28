export function formatHtmlContent(raw: string | undefined | null): string {
  if (!raw) return '';
  let text = String(raw);
  // Decode HTML entities (2 passes for double escaping)
  for (let i = 0; i < 2; i++) {
    text = text
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&amp;/g, '&');
  }
  return text
    .replace(/<br\s*[\/]?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .trim();
}
