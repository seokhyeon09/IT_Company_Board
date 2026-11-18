import React from 'react';

export interface InlineErrorNoticeProps {
  message: string;
  title?: string;
  sticky?: boolean;
}

export const InlineErrorNotice: React.FC<InlineErrorNoticeProps> = ({
  message,
  title = '오류',
  sticky = false,
}) => {
  if (!message) return null;

  const baseClass = 'p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl';
  const alignClass = title === '오류' ? 'text-center' : '';
  const stickyClass = sticky ? 'sticky top-0 z-10 shadow-sm' : '';
  const className = [baseClass, alignClass, stickyClass].filter(Boolean).join(' ');

  return (
    <div role="alert" className={className}>
      <p className="font-bold">{title}</p>
      <p className="text-xs mt-1">{message}</p>
    </div>
  );
};
