export interface ThreadItem {
  id: number;
  type: 'inquiry' | 'resolution' | 'pending_request' | 'pending_response';
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
}

export interface OfficerSimpleItem {
  id: number;
  name: string;
  login: string;
}

export interface OfficerStatItem {
  officer_id: number;
  officer_name: string;
  officer_email: string;
  total_assigned: number;
  in_progress_count: number;
  resolved_count: number;
  overdue_count: number;
  sla_compliance_rate: number;
  avg_rating: number;
  rating_count: number;
}

export interface CategoryStatItem {
  category: string;
  label: string;
  count: number;
  percentage: number;
}

export interface OfficerStatsData {
  officers: OfficerStatItem[];
  category_breakdown: CategoryStatItem[];
  unassigned_count: number;
  total_active_tickets: number;
  overall_avg_rating: number;
  overall_sla_rate: number;
}

export interface TicketDetail {
  id: number;
  ticket_number: string;
  title: string;
  category: string;
  content: string;
  status: string;
  priority: string;
  deadline?: string;
  is_overdue: boolean;
  author_id?: any;
  author_name?: string;
  assignee_id?: any;
  assignee_name?: string;
  create_date?: string;
  write_date?: string;
  is_faq: boolean;
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
