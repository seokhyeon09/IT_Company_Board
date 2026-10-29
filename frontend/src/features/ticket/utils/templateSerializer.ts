import {
  PriorityHint,
  TemplateValidationResult,
  TicketTemplate,
} from '../types/ticketTemplate';

export function buildInitialTemplateValues(
  template: TicketTemplate | null | undefined
): Record<string, string> {
  if (!template || !template.fields.length) {
    return {};
  }
  const initial: Record<string, string> = {};
  for (const field of template.fields) {
    if (field.type === 'select' && field.options && field.options.length > 0) {
      initial[field.key] = field.options[0].value;
    } else {
      initial[field.key] = '';
    }
  }
  return initial;
}

export function validateTemplateValues(
  template: TicketTemplate | null | undefined,
  values: Record<string, string>
): TemplateValidationResult {
  if (!template || !template.fields.length) {
    return { valid: true, error: null, missingKey: null };
  }
  for (const field of template.fields) {
    const raw = values[field.key] ?? '';
    if (field.required && !raw.trim()) {
      return {
        valid: false,
        error: `'${field.label}' 항목을 입력해 주세요.`,
        missingKey: field.key,
      };
    }
  }
  return { valid: true, error: null, missingKey: null };
}

export function serializeTemplateContent(
  template: TicketTemplate,
  values: Record<string, string>
): string {
  const lines: string[] = [];
  for (const field of template.fields) {
    const val = (values[field.key] ?? '').trim();
    if (val) {
      lines.push(`[${field.label}] ${val}`);
    }
  }
  return lines.join('\n');
}

export function hasAnyTemplateInput(
  template: TicketTemplate | null | undefined,
  values: Record<string, string>
): boolean {
  if (!template || !template.fields.length) {
    return false;
  }
  const defaults = buildInitialTemplateValues(template);
  return template.fields.some((field) => {
    const current = (values[field.key] ?? '').trim();
    const initial = (defaults[field.key] ?? '').trim();
    return current !== '' && current !== initial;
  });
}

export function resolvePriorityHint(
  template: TicketTemplate | null | undefined,
  values: Record<string, string>
): PriorityHint | null {
  if (!template || !template.priorityHint) {
    return null;
  }
  const hint = template.priorityHint;
  if (hint.whenField && hint.whenValues && hint.whenValues.length > 0) {
    const currentVal = values[hint.whenField] ?? '';
    return hint.whenValues.includes(currentVal) ? hint : null;
  }
  return hint;
}
