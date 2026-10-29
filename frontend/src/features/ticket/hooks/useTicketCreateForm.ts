import React, { useState } from 'react';
import { apiClient, getErrorMessage } from '../../../api/client';
import { TicketCategory, TicketPriority } from '../../../shared/types/common';
import { getTemplateForCategory } from '../templates/ticketTemplates';
import {
  buildInitialTemplateValues,
  hasAnyTemplateInput,
  resolvePriorityHint,
  serializeTemplateContent,
  validateTemplateValues,
} from '../utils/templateSerializer';
import { useCreateAttachments } from './useCreateAttachments';

interface UseTicketCreateFormProps {
  onSuccess: () => void;
  onClose: () => void;
}

export function useTicketCreateForm({ onSuccess, onClose }: UseTicketCreateFormProps) {
  const [title, setTitle] = useState('');
  const [category, setCategoryState] = useState<TicketCategory>('sw');
  const [priority, setPriority] = useState<TicketPriority>('1');
  const [isFreeText, setIsFreeText] = useState(false);
  const [contentState, setContentState] = useState<{
    freeContent: string;
    templateValues: Record<string, string>;
    notice: string | null;
  }>({
    freeContent: '',
    templateValues: buildInitialTemplateValues(getTemplateForCategory('sw')),
    notice: null,
  });
  const [submitState, setSubmitState] = useState<{
    loading: boolean;
    error: string | null;
  }>({
    loading: false,
    error: null,
  });

  const setError = (msg: string | null) => {
    setSubmitState((prev) => ({ ...prev, error: msg }));
  };

  const { attachments, handleFileChange, removeAttachment, clearAttachments } =
    useCreateAttachments(setError);

  const currentTemplate = getTemplateForCategory(category);
  const useTemplateMode = !isFreeText && currentTemplate.fields.length > 0;
  const activePriorityHint = useTemplateMode
    ? resolvePriorityHint(currentTemplate, contentState.templateValues)
    : null;

  const handleCategoryChange = (nextCategoryRaw: string) => {
    const nextCategory = (nextCategoryRaw as TicketCategory) || 'etc';
    const nextTemplate = getTemplateForCategory(nextCategory);
    const hadInput = hasAnyTemplateInput(currentTemplate, contentState.templateValues);

    setCategoryState(nextCategory);
    setContentState((prev) => ({
      ...prev,
      templateValues: buildInitialTemplateValues(nextTemplate),
      notice:
        !isFreeText && hadInput
          ? '분류가 변경되어 이전 템플릿 입력 항목이 초기화되었습니다.'
          : null,
    }));
    setError(null);
  };

  const updateTemplateField = (key: string, value: string) => {
    setContentState((prev) => ({
      ...prev,
      templateValues: { ...prev.templateValues, [key]: value },
      notice: null,
    }));
    if (submitState.error) setError(null);
  };

  const setFreeContent = (value: string) => {
    setContentState((prev) => ({ ...prev, freeContent: value, notice: null }));
    if (submitState.error) setError(null);
  };

  const toggleFreeTextMode = () => {
    setIsFreeText((prev) => !prev);
    setError(null);
  };

  const resetForm = () => {
    setTitle('');
    setCategoryState('sw');
    setPriority('1');
    setIsFreeText(false);
    setContentState({
      freeContent: '',
      templateValues: buildInitialTemplateValues(getTemplateForCategory('sw')),
      notice: null,
    });
    setSubmitState({ loading: false, error: null });
    clearAttachments();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('문의 제목을 입력해 주세요.');
      return;
    }

    let finalContent = '';
    if (useTemplateMode) {
      const check = validateTemplateValues(currentTemplate, contentState.templateValues);
      if (!check.valid) {
        setError(check.error || '필수 항목을 모두 입력해 주세요.');
        return;
      }
      finalContent = serializeTemplateContent(currentTemplate, contentState.templateValues);
    } else {
      finalContent = contentState.freeContent.trim();
      if (!finalContent) {
        setError('제목과 문의 내용을 모두 입력해주세요.');
        return;
      }
    }

    setSubmitState({ loading: true, error: null });
    try {
      const payload: Record<string, any> = {
        title: title.trim(),
        category,
        priority,
        content: finalContent,
      };
      if (attachments.length > 0) {
        payload.attachments = attachments.map((att) => ({
          name: att.name,
          datas: att.datas,
          mimetype: att.mimetype,
        }));
      }
      await apiClient.post('/tickets', payload);
      resetForm();
      onSuccess();
      onClose();
    } catch (err: any) {
      setSubmitState({
        loading: false,
        error: getErrorMessage(err, '티켓 생성 중 오류가 발생했습니다.'),
      });
    }
  };

  return {
    title,
    setTitle,
    category,
    handleCategoryChange,
    priority,
    setPriority: (val: string) => setPriority(val as TicketPriority),
    isFreeText,
    toggleFreeTextMode,
    useTemplateMode,
    currentTemplate,
    templateValues: contentState.templateValues,
    updateTemplateField,
    freeContent: contentState.freeContent,
    setFreeContent,
    notice: contentState.notice,
    activePriorityHint,
    loading: submitState.loading,
    error: submitState.error,
    attachments,
    handleFileChange,
    removeAttachment,
    handleSubmit,
  };
}
