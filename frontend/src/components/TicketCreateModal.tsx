import React, { useState } from 'react';
import { X, Send, AlertCircle, Paperclip, FileText, Trash2 } from 'lucide-react';
import { apiClient, getErrorMessage } from '../api/client';

interface TicketCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const TicketCreateModal: React.FC<TicketCreateModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('sw');
  const [priority, setPriority] = useState('1');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  interface AttachedFile {
    name: string;
    datas: string;
    mimetype: string;
    size: number;
  }
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
      await apiClient.post('/tickets', {
        title,
        category,
        priority,
        content,
        attachments: attachments.length > 0 ? attachments : undefined,
      });
      setTitle('');
      setContent('');
      setAttachments([]);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(getErrorMessage(err, '문의 등록 중 오류가 발생했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900">새 IT 문의 접수</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-md">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">문의 제목</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예: 모니터 화면이 깜빡입니다"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">분류</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="hw">하드웨어 (PC, 모니터)</option>
                <option value="sw">소프트웨어 (OS, 오피스)</option>
                <option value="network">네트워크 / 인터넷</option>
                <option value="account">계정 / 권한 요청</option>
                <option value="etc">기타 일반 문의</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">긴급도 (SLA)</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="0">낮음 (3일 이내 조치)</option>
                <option value="1">보통 (2일 이내 조치)</option>
                <option value="2">높음 (24시간 이내 조치)</option>
                <option value="3">긴급 (4시간 이내 조치)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">문의 상세 내용</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={4}
              placeholder="발생 증상 및 조치 요청 사항을 상세히 기술해주세요."
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

                    {/* Attachments Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold text-slate-700">첨부파일 (스크린샷, 에러로그)</label>
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
              <div className="space-y-1.5 max-h-32 overflow-y-auto">
                {attachments.map((att, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 bg-slate-50 border border-slate-200 rounded-lg text-xs"
                  >
                    <div className="flex items-center space-x-2 truncate">
                      <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate font-medium text-slate-700">{att.name}</span>
                      <span className="text-[10px] text-slate-400">({(att.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAttachment(idx)}
                      className="p-1 text-slate-400 hover:text-rose-600 rounded"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm disabled:opacity-50"
            >
              <Send className="w-4 h-4 mr-1.5" />
              {loading ? '접수 중...' : '문의 등록'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
