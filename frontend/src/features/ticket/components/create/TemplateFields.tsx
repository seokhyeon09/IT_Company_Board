import React from 'react';
import { Info } from 'lucide-react';
import { PriorityHint, TicketTemplate } from '../../types/ticketTemplate';

interface TemplateFieldsProps {
  template: TicketTemplate;
  values: Record<string, string>;
  onChangeField: (key: string, value: string) => void;
  priorityHint: PriorityHint | null;
}

export const TemplateFields: React.FC<TemplateFieldsProps> = ({
  template,
  values,
  onChangeField,
  priorityHint,
}) => {
  return (
    <div
      data-testid="template-fields-container"
      className="p-3.5 bg-slate-50/80 border border-slate-200 rounded-xl space-y-3"
    >
      <p className="text-[11px] text-slate-500">{template.description}</p>

      {priorityHint && (
        <div
          data-testid="template-priority-hint"
          className="p-2.5 bg-amber-50 border border-amber-200 rounded-lg flex items-start space-x-2 text-[11px] text-amber-800"
        >
          <Info className="w-3.5 h-3.5 mt-0.5 shrink-0 text-amber-600" />
          <span>{priorityHint.message}</span>
        </div>
      )}

      <div className="space-y-2.5">
        {template.fields.map((field) => {
          const val = values[field.key] ?? '';
          return (
            <div key={field.key}>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {field.label}
                {field.required ? (
                  <span className="text-rose-500 ml-0.5">*</span>
                ) : (
                  <span className="text-[10px] font-normal text-slate-400 ml-1">(선택)</span>
                )}
              </label>

              {field.type === 'select' && field.options ? (
                <select
                  data-template-field={field.key}
                  value={val}
                  onChange={(e) => onChangeField(field.key, e.target.value)}
                  className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                >
                  {field.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'textarea' ? (
                <textarea
                  data-template-field={field.key}
                  value={val}
                  onChange={(e) => onChangeField(field.key, e.target.value)}
                  placeholder={field.placeholder || ''}
                  rows={3}
                  className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all resize-none"
                />
              ) : (
                <input
                  data-template-field={field.key}
                  value={val}
                  onChange={(e) => onChangeField(field.key, e.target.value)}
                  placeholder={field.placeholder || ''}
                  className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
