import { Ticket } from '../types/ticket';
import { ReplyTemplateVars, TemplateContext } from '../types/replyTemplate';

const VARIABLE_PATTERN = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g;

/**
 * Replaces supported template placeholders while preserving missing or unknown variables.
 */
export function applyTemplateVariables(body: string, vars: ReplyTemplateVars): string {
  const varMap: Record<string, string | undefined> = {
    requester_name: vars.requester_name,
    ticket_number: vars.ticket_number,
    officer_name: vars.officer_name,
  };

  return body.replace(VARIABLE_PATTERN, (match, key: string) => {
    if (!Object.prototype.hasOwnProperty.call(varMap, key)) {
      return match;
    }
    const value = varMap[key];
    return value ? value : match;
  });
}

/**
 * Appends template text after existing content separated by a blank line, trimming trailing whitespace.
 */
export function appendText(current: string, insertion: string): string {
  const trimmedCurrent = current.replace(/\s+$/, '');
  if (!trimmedCurrent) {
    return insertion;
  }
  if (!insertion) {
    return trimmedCurrent;
  }
  return `${trimmedCurrent}\n\n${insertion}`;
}

export function extractRequesterName(
  ticket: Pick<Ticket, 'author_name' | 'author_id'>
): string | undefined {
  if (ticket.author_name && ticket.author_name.trim()) {
    return ticket.author_name;
  }
  if (Array.isArray(ticket.author_id) && ticket.author_id.length >= 2 && ticket.author_id[1]) {
    return String(ticket.author_id[1]);
  }
  return undefined;
}

export function buildTemplateContext(
  ticket: Pick<Ticket, 'category' | 'ticket_number' | 'author_name' | 'author_id'>
): TemplateContext {
  return {
    category: ticket.category,
    ticketNumber: ticket.ticket_number,
    requesterName: extractRequesterName(ticket),
  };
}
