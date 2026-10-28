import { TicketCategory, TicketPriority, TicketStatus } from '../../../shared/types/common';

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  category: TicketCategory | string;
  status: TicketStatus | string;
  priority: TicketPriority | string;
  deadline?: string;
  is_overdue: boolean;
  author_id?: any;
  author_name?: string;
  assignee_id?: any;
  assignee_name?: string;
  create_date?: string;
  write_date?: string;
  is_faq: boolean;
}

export interface ThreadItem {
  id: number;
  type: 'inquiry' | 'resolution' | 'pending_request' | 'pending_response' | 'reassign';
  round: number;
  author_id?: any;
  author_name: string;
  date?: string;
  content: string;
}

export interface ResolutionNote {
  id: number;
  date?: string;
  author_name?: string;
  content: string;
}

export interface FollowUpInquiry {
  id: number;
  date?: string;
  author_name?: string;
  content: string;
}

export interface Attachment {
  id: number;
  name: string;
  mimetype: string;
  file_size?: number;
  create_date?: string;
}

export interface TicketLog {
  id: number;
  date?: string;
  author_name?: string;
  body: string;
  message_type?: string;
}

export interface RelatedTicketItem {
  id: number;
  ticket_number: string;
  title?: string;
  category?: string;
  status: string;
  is_faq: boolean;
  resolution_summary?: string;
  create_date?: string;
}

export interface EmailNotificationItem {
  id: string;
  ticket_id: number;
  ticket_number: string;
  ticket_title?: string;
  event_type: string;
  recipient_name: string;
  recipient_email: string;
  sender_email: string;
  subject: string;
  body_preview: string;
  sent_at?: string;
  status: string;
  is_read?: boolean;
}

export interface OfficerSimpleItem {
  id: number;
  name: string;
  login: string;
}

export interface TicketDetail extends Ticket {
  content: string;
  pending_reason?: string;
  resolution_note?: string;
  rating?: string;
  rating_comment?: string;
  timeline?: ThreadItem[];
  resolutions?: ResolutionNote[];
  follow_ups?: FollowUpInquiry[];
  logs?: TicketLog[];
  attachments?: Attachment[];
  related_tickets?: RelatedTicketItem[];
  email_notifications?: EmailNotificationItem[];
}
