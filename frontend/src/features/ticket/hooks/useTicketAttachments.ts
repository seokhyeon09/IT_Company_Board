import { useState } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { TicketDetail, Attachment } from '../types/ticket';
import { readFileAsBase64, downloadBase64File } from '../../../shared/utils/fileUtils';

interface UseTicketAttachmentsProps {
  ticket: TicketDetail | null;
  onSuccess?: () => void;
  reloadTicket: () => void;
}

export function useTicketAttachments({
  ticket,
  onSuccess,
  reloadTicket,
}: UseTicketAttachmentsProps) {
  const [uploadingAttachment, setUploadingAttachment] = useState(false);
  const [downloadingAttachmentId, setDownloadingAttachmentId] = useState<number | null>(null);
  const [attachmentError, setAttachmentError] = useState<string | null>(null);

  const handleUploadAttachment = async (file: File) => {
    if (!ticket) return;
    setAttachmentError(null);

    // 5MB 용량 검증
    if (file.size > 5 * 1024 * 1024) {
      setAttachmentError('파일 크기는 최대 5MB까지 첨부할 수 있습니다.');
      return;
    }

    setUploadingAttachment(true);
    try {
      const base64Data = await readFileAsBase64(file);
      await ticketApi.uploadAttachment(ticket.id, {
        name: file.name,
        datas: base64Data,
        mimetype: file.type || 'application/octet-stream',
      });
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setAttachmentError(getErrorMessage(err, '파일 첨부에 실패했습니다.'));
    } finally {
      setUploadingAttachment(false);
    }
  };

  const handleDownloadAttachment = async (att: Attachment) => {
    if (!ticket || downloadingAttachmentId) return;
    setAttachmentError(null);
    setDownloadingAttachmentId(att.id);
    try {
      const data = await ticketApi.getAttachment(ticket.id, att.id);
      downloadBase64File(data.datas, data.name || att.name, data.mimetype || att.mimetype);
    } catch (err: any) {
      setAttachmentError(getErrorMessage(err, '첨부파일 다운로드에 실패했습니다.'));
    } finally {
      setDownloadingAttachmentId(null);
    }
  };

  return {
    uploadingAttachment,
    downloadingAttachmentId,
    attachmentError,
    clearAttachmentError: () => setAttachmentError(null),
    handleUploadAttachment,
    handleDownloadAttachment,
  };
}
