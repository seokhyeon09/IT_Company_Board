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
}
