import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';
import { MAINTENANCE_FORM_NAME } from '../lib/maintenance';
import { SITE404_FORM_NAME } from '../lib/site404';

export default function FormsPage() {
  const { forms, saveForm, deleteForm } = usePlatform();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    await saveForm({
      name: name.trim(),
      description: description.trim(),
      fields: [
        { id: 'subject', label: 'Subject', type: 'text', required: true },
        { id: 'details', label: 'Details', type: 'textarea', required: true },
      ],
      active: true,
    });
    setName('');
    setDescription('');
  };

  const hidden = new Set([MAINTENANCE_FORM_NAME, SITE404_FORM_NAME]);

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">Intake forms available for the portal and agent ticket creation.</p>
      <form onSubmit={add} className="bg-white rounded-xl border p-5 shadow-sm flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[160px]">
          <label className="text-xs text-slate-500">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="w-full px-3 py-2 text-sm border rounded-lg" required />
        </div>
        <div className="flex-1 min-w-[160px]">
          <label className="text-xs text-slate-500">Description</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} className="w-full px-3 py-2 text-sm border rounded-lg" />
        </div>
        <button type="submit" className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-brand-600 rounded-lg"><Plus size={16} /> Add form</button>
      </form>
      <div className="grid md:grid-cols-2 gap-4">
        {forms.filter((f) => !hidden.has(f.name)).map((f) => (
          <div key={f.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex justify-between">
              <div className="font-semibold text-slate-900">{f.name}</div>
              <button type="button" onClick={() => deleteForm(f.id)} className="text-slate-400 hover:text-rose-600"><Trash2 size={16} /></button>
            </div>
            <p className="text-sm text-slate-500 mt-1">{f.description}</p>
            <ul className="mt-3 text-xs text-slate-600 space-y-1">
              {(f.fields || []).map((field) => (
                <li key={field.id}>• {field.label} ({field.type}){field.required ? ' *' : ''}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
