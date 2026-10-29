import { useState, useEffect } from 'react';
import { apiClient } from '../../../api/client';
import { SuggestedFaqTicket } from '../types/ticketTemplate';

export function useSimilarFaqs(isOpen: boolean, category: string, title: string) {
  const [suggestedFaqs, setSuggestedFaqs] = useState<SuggestedFaqTicket[]>([]);

  useEffect(() => {
    if (!isOpen) {
      setSuggestedFaqs([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const params: Record<string, any> = {
          is_faq: true,
          category,
          limit: 3,
        };
        if (title.trim().length >= 2) {
          params.search = title.trim();
        }
        const res = await apiClient.get('/tickets', { params });
        setSuggestedFaqs(res.data.data || []);
      } catch {
        setSuggestedFaqs([]);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [isOpen, category, title]);

  return { suggestedFaqs };
}
