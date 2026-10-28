import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../../../stores/authStore';
import { ticketApi } from '../../../api/ticketApi';
import { workflowApi } from '../../../api/workflowApi';
import { getErrorMessage } from '../../../api/client';
import { TicketDetail } from '../types/ticket';
import { TicketPermissions } from '../types/ticketModal';

export function useTicketDetail(ticketId: number | null, isOpen: boolean) {
  const { user } = useAuthStore();
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState('');
  const [togglingFaq, setTogglingFaq] = useState(false);

  const fetchDetail = useCallback(async (id: number) => {
    setLoading(true);
    setFetchError('');
    try {
      const data = await ticketApi.getTicketDetail(id);
      setTicket(data);
    } catch (err: any) {
      setFetchError(getErrorMessage(err, '티켓 상세 정보를 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen && ticketId) {
      fetchDetail(ticketId);
    } else {
      setTicket(null);
      setFetchError('');
    }
  }, [isOpen, ticketId, fetchDetail]);

  const handleToggleFaq = async () => {
    if (!ticket || togglingFaq) return;
    setTogglingFaq(true);
    try {
      const updated = await workflowApi.toggleFaq(ticket.id);
      setTicket((prev) => (prev ? { ...prev, is_faq: updated.is_faq } : null));
    } catch (err: any) {
      alert(getErrorMessage(err, 'FAQ 추천 상태 변경에 실패했습니다.'));
    } finally {
      setTogglingFaq(false);
    }
  };

  const isAuthor = Boolean(user && ticket && ticket.author_id && (
    (Array.isArray(ticket.author_id) && ticket.author_id[0] === user.uid) ||
    ticket.author_id === user.uid
  ));

  const isOfficer = Boolean(user?.is_officer);

  const isAssignee = Boolean(user && ticket && ticket.assignee_id && (
    (Array.isArray(ticket.assignee_id) && ticket.assignee_id[0] === user.uid) ||
    ticket.assignee_id === user.uid
  ));

  const isAdmin = Boolean(user?.is_admin);
  const isOwnerOrAdmin = isAssignee || isAdmin;

  const permissions: TicketPermissions = {
    isAuthor,
    isOfficer,
    isAssignee,
    isAdmin,
    isOwnerOrAdmin,
  };

  return {
    ticket,
    setTicket,
    loading,
    fetchError,
    faqLoading: togglingFaq,
    handleToggleFaq,
    reloadTicket: () => ticketId && fetchDetail(ticketId),
    permissions,
  };
}
