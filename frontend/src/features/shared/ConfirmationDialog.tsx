import React from 'react';

export const ConfirmationDialog = ({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-sm rounded-lg bg-white p-5 shadow-lg">
        <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
        <p className="mt-2 text-sm text-gray-600">{description}</p>
        <div className="mt-4 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="rounded bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};
