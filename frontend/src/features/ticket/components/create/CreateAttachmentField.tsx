import React from 'react';
import { Paperclip, FileText, Trash2 } from 'lucide-react';
import { AttachedFileItem } from '../../types/ticketTemplate';

interface CreateAttachmentFieldProps {
  attachments: AttachedFileItem[];
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveAttachment: (index: number) => void;
}

export const CreateAttachmentField: React.FC<CreateAttachmentFieldProps> = ({
  attachments,
  onFileChange,
  onRemoveAttachment,
}) => {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-xs font-semibold text-slate-700">
          첨부파일 <span className="text-[11px] font-normal text-slate-400">(최대 5MB)</span>
        </label>
        <label className="flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer">
          <Paperclip className="w-3.5 h-3.5 mr-1" />
          파일 추가
          <input
            type="file"
            onChange={onFileChange}
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
                onClick={() => onRemoveAttachment(idx)}
                className="p-1 text-slate-400 hover:text-rose-500 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
