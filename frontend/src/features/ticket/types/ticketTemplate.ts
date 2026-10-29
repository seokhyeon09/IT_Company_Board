import { TicketCategory, TicketPriority } from '../../../shared/types/common';

export type TemplateFieldType = 'text' | 'select' | 'textarea';

export interface TemplateFieldOption {
  value: string;
  label: string;
}

export interface TemplateField {
  key: string;
  label: string;
  type: TemplateFieldType;
  required: boolean;
  placeholder?: string;
  options?: TemplateFieldOption[];
}

export interface PriorityHint {
  whenField?: string;
  whenValues?: string[];
  recommendedPriority: TicketPriority;
  message: string;
}

export interface TicketTemplate {
  category: TicketCategory;
  titlePlaceholder: string;
  description: string;
  fields: TemplateField[];
  priorityHint?: PriorityHint;
}

export interface TemplateValidationResult {
  valid: boolean;
  error: string | null;
  missingKey: string | null;
}

export interface AttachedFileItem {
  name: string;
  datas: string;
  mimetype: string;
  size: number;
}

export interface SuggestedFaqTicket {
  id: number;
  ticket_number: string;
  title: string;
  category: string;
  is_faq: boolean;
}
