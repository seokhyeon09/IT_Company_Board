import React from 'react';
import { OfficerSimpleItem } from '../../../types/ticket';
import { DesignateOfficerForm } from './DesignateOfficerForm';
import { PendingRequestForm } from './PendingRequestForm';
import { ForceCloseForm } from './ForceCloseForm';

interface TicketWorkflowSubFormsProps {
  showDesignateModal: boolean;
  isSubmitted: boolean;
  officers: OfficerSimpleItem[];
  selectedAssignOfficerId: number | '';
  onSelectAssignOfficer: (id: number | '') => void;
  assignReason: string;
  onSetAssignReason: (val: string) => void;
  submittingDesignate: boolean;
  designateError: string;
  onToggleDesignate: () => void;
  onSubmitDesignate: () => void;
  showPendingModal: boolean;
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submittingPending: boolean;
  pendingError: string;
  onClosePendingModal: () => void;
  onSubmitPending: (e: React.FormEvent) => void;
  showCloseModal: boolean;
  closeNote: string;
  setCloseNote: (val: string) => void;
  submittingClose: boolean;
  closeError: string;
  onCloseCloseModal: () => void;
  onSubmitClose: (e: React.FormEvent) => void;
}

export const TicketWorkflowSubForms: React.FC<TicketWorkflowSubFormsProps> = ({
  showDesignateModal,
  isSubmitted,
  officers,
  selectedAssignOfficerId,
  onSelectAssignOfficer,
  assignReason,
  onSetAssignReason,
  submittingDesignate,
  designateError,
  onToggleDesignate,
  onSubmitDesignate,
  showPendingModal,
  pendingReason,
  setPendingReason,
  submittingPending,
  pendingError,
  onClosePendingModal,
  onSubmitPending,
  showCloseModal,
  closeNote,
  setCloseNote,
  submittingClose,
  closeError,
  onCloseCloseModal,
  onSubmitClose,
}) => {
  return (
    <>
      {showDesignateModal && (
        <DesignateOfficerForm
          isSubmitted={isSubmitted}
          officers={officers}
          selectedOfficerId={selectedAssignOfficerId}
          onSelectOfficer={onSelectAssignOfficer}
          assignReason={assignReason}
          setAssignReason={onSetAssignReason}
          submitting={submittingDesignate}
          error={designateError}
          onCancel={onToggleDesignate}
          onSubmit={onSubmitDesignate}
        />
      )}

      {showPendingModal && (
        <PendingRequestForm
          pendingReason={pendingReason}
          setPendingReason={setPendingReason}
          submitting={submittingPending}
          error={pendingError}
          onCancel={onClosePendingModal}
          onSubmit={onSubmitPending}
        />
      )}

      {showCloseModal && (
        <ForceCloseForm
          closeNote={closeNote}
          setCloseNote={setCloseNote}
          submitting={submittingClose}
          error={closeError}
          onCancel={onCloseCloseModal}
          onSubmit={onSubmitClose}
        />
      )}
    </>
  );
};
