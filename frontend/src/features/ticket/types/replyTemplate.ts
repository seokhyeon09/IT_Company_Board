import { TicketCategory } from '../../../shared/types/common';

export type ReplyTemplateCategory = '' | TicketCategory;

export interface ReplyTemplate {
  id: number;
  name: string;
  category: ReplyTemplateCategory;
  body: string;
  is_mine: boolean;
  write_date: string;
}

export interface ReplyTemplateInput {
  name: string;
  category: ReplyTemplateCategory;
  body: string;
}

export interface ReplyTemplateVars {
  requester_name?: string;
  ticket_number?: string;
  officer_name?: string;
}

export interface TemplateContext {
  category: string;
  ticketNumber: string;
  requesterName?: string;
}
