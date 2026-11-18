import { useEffect, useRef } from 'react';

export interface UseModalBehaviorOptions {
  isOpen: boolean;
  onClose: () => void;
  closeOnEscape?: boolean;
}

let activeBodyLockCount = 0;
let savedBodyOverflow = '';

/**
 * 모달 열림 상태에 따라 body 스크롤 잠금 및 Escape 키 닫기를 처리한다.
 */
export function useModalBehavior({
  isOpen,
  onClose,
  closeOnEscape = true,
}: UseModalBehaviorOptions): void {
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    if (!isOpen) return;

    if (activeBodyLockCount === 0) {
      savedBodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    }
    activeBodyLockCount += 1;

    return () => {
      activeBodyLockCount = Math.max(0, activeBodyLockCount - 1);
      if (activeBodyLockCount === 0) {
        document.body.style.overflow = savedBodyOverflow;
      }
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onCloseRef.current();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, closeOnEscape]);
}
