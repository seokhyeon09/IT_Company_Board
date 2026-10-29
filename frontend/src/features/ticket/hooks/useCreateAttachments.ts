import React, { useState } from 'react';
import { readFileAsBase64 } from '../../../shared/utils/fileUtils';
import { AttachedFileItem } from '../types/ticketTemplate';

const MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024;

export function useCreateAttachments(onError: (msg: string) => void) {
  const [attachments, setAttachments] = useState<AttachedFileItem[]>([]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    e.target.value = '';

    if (file.size > MAX_ATTACHMENT_BYTES) {
      onError('첨부파일 크기는 최대 5MB까지 지원됩니다.');
      return;
    }

    try {
      const base64Data = await readFileAsBase64(file);
      setAttachments((prev) => [
        ...prev,
        {
          name: file.name,
          datas: base64Data,
          mimetype: file.type || 'application/octet-stream',
          size: file.size,
        },
      ]);
    } catch {
      onError('첨부파일을 읽는 중 오류가 발생했습니다.');
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAttachments = () => {
    setAttachments([]);
  };

  return {
    attachments,
    handleFileChange,
    removeAttachment,
    clearAttachments,
  };
}
