import React from 'react';
import { Paperclip, Loader2, Download, Image, FileText } from 'lucide-react';
import { Attachment } from '../../types/ticket';

interface TicketAttachmentsProps {
  attachments: Attachment[] | undefined;
  canUpload: boolean;
  uploadingAttachment: boolean;
  downloadingAttachmentId: number | null;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFileDownload: (att: Attachment) => void;
}

export const TicketAttachments: React.FC<TicketAttachmentsProps> = ({
  attachments,
  canUpload,
  uploadingAttachment,
  downloadingAttachmentId,
  onFileUpload,
  onFileDownload,
}) => {
  const count = attachments ? attachments.length : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <Paperclip className="w-4 h-4 text-slate-600" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            첨부파일 ({count}개)
          </h4>
        </div>
        {canUpload && (
          <label className="flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer bg-white px-2.5 py-1 rounded-lg border border-indigo-200 hover:bg-indigo-50 shadow-xs transition-all">
            {uploadingAttachment ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                업로드 중...
              </>
            ) : (
              <>
                <Paperclip className="w-3.5 h-3.5 mr-1" />
                파일 추가
              </>
            )}
            <input
              type="file"
              onChange={onFileUpload}
              disabled={uploadingAttachment}
              className="hidden"
            />
          </label>
        )}
      </div>

      {attachments && attachments.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {attachments.map((att) => {
            const isImage = att.mimetype?.startsWith('image/');
            const isDownloading = downloadingAttachmentId === att.id;

            return (
              <div
                key={att.id}
                className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs hover:bg-slate-100 transition-all"
              >
                <div className="flex items-center space-x-2 truncate pr-2">
                  {isImage ? (
                    <Image className="w-4 h-4 text-indigo-500 shrink-0" />
                  ) : (
                    <FileText className="w-4 h-4 text-slate-500 shrink-0" />
                  )}
                  <span className="font-medium text-slate-700 truncate" title={att.name}>
                    {att.name}
                  </span>
                  {att.file_size ? (
                    <span className="text-[10px] text-slate-400 shrink-0">
                      ({(att.file_size / 1024).toFixed(1)} KB)
                    </span>
                  ) : null}
                </div>

                <button
                  type="button"
                  onClick={() => onFileDownload(att)}
                  disabled={isDownloading}
                  className="flex items-center text-indigo-600 hover:text-indigo-800 p-1 rounded hover:bg-white transition-colors shrink-0 cursor-pointer"
                  title="다운로드"
                >
                  {isDownloading ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Download className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-slate-400 py-1 italic">첨부된 파일이 없습니다.</p>
      )}
    </div>
  );
};
