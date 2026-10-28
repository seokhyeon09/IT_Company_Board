import React, { useState } from 'react';
import { X, Send, AlertCircle, Paperclip, FileText, Trash2 } from 'lucide-react';
import { apiClient, getErrorMessage } from '../../../api/client';

export interface TicketCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface AttachedFile {
  name: string;
  datas: string;
  mimetype: string;
  size: number;
}

export const TicketCreateModal: React.FC<TicketCreateModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('sw');
  const [priority, setPriority] = useState('1');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<AttachedFile[]>([]);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    if (file.size > 5 * 1024 * 1024) {
      setError('첨부파일 크기는 최대 5MB까지 지원됩니다.');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const base64Data = (reader.result as string).split(',')[1] || '';
      setAttachments((prev) => [
        ...prev,
        {
          name: file.name,
          datas: base64Data,
          mimetype: file.type || 'application/octet-stream',
          size: file.size,
        },
      ]);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('제목과 문의 내용을 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: any = {
        title: title.trim(),
        category,
        priority,
        content: content.trim(),
      };
      if (attachments.length > 0) {
        payload.attachments = attachments.map((att) => ({
          name: att.name,
          datas: att.datas,
          mimetype: att.mimetype,
        }));
      }
      await apiClient.post('/tickets', payload);

      setTitle('');
      setContent('');
      setCategory('sw');
      setPriority('1');
      setAttachments([]);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(getErrorMessage(err, '티켓 생성 중 오류가 발생했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-lg font-bold text-slate-800">새 IT 문의 접수</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              도움이 필요한 내용을 자세히 작성해주시면 담당자가 배정됩니다.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-start space-x-2 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">제목</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예: 모니터 전원이 들어오지 않습니다."
              className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">분류</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              >
                <option value="hw">하드웨어</option>
                <option value="sw">소프트웨어</option>
                <option value="network">네트워크</option>
                <option value="account">계정/권한</option>
                <option value="etc">기타</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">긴급도</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              >
                <option value="0">낮음</option>
                <option value="1">보통</option>
                <option value="2">높음</option>
                <option value="3">긴급</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">상세 내용</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="발생 증상, 시점, 에러 메시지 등을 가능한 상세히 적어주세요."
              rows={4}
              className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all resize-none"
              required
            />
          </div>

          {/* Attachment upload */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-semibold text-slate-700">첨부파일</label>
              <label className="flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer">
                <Paperclip className="w-3.5 h-3.5 mr-1" />
                파일 추가
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  accept="image/*,.log,.txt,.pdf"
                />
              </label>
            </div>

            {attachments.length > 0 && (
              <div className="space-y-1.5 mt-2">
                {attachments.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 bg-slate-50 border border-slate-200 rounded-lg text-xs"
                  >
                    <div className="flex items-center space-x-2 truncate pr-2">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <span className="truncate">{file.name}</span>
                      <span className="text-[10px] text-slate-400 shrink-0">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAttachment(idx)}
                      className="p-1 text-slate-400 hover:text-rose-500 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors cursor-pointer"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-colors cursor-pointer shadow-sm"
            >
              <Send className="w-3.5 h-3.5 mr-1.5" />
              {loading ? '접수 중...' : '문의 접수'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
