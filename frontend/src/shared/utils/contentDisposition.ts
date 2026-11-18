export function parseContentDispositionFilename(header?: string | null): string | null {
  if (!header || !header.trim()) {
    return null;
  }

  const utf8Match = header.match(/filename\*\s*=\s*(?:UTF-8''|utf-8'')([^;\s]+)/i);
  if (utf8Match && utf8Match[1]) {
    try {
      const decoded = decodeURIComponent(utf8Match[1].replace(/^["']|["']$/g, '')).trim();
      if (decoded) return decoded;
    } catch {
      // Ignore malformed URI encoding and fall back to standard filename parameter
    }
  }

  const quotedMatch = header.match(/filename\s*=\s*"([^"]*)"/i);
  if (quotedMatch) {
    const name = quotedMatch[1].trim();
    return name || null;
  }

  const unquotedMatch = header.match(/filename\s*=\s*([^;\s]+)/i);
  if (unquotedMatch) {
    const name = unquotedMatch[1].trim();
    return name || null;
  }

  return null;
}

export function defaultCsvFilename(now: Date = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `tickets_${y}${m}${d}.csv`;
}
