/* ticket-panel-v1 */
/* ticket-unread-v1 */
import { useMemo, useState, useRef, useEffect } from 'react';
import { X, Trash2, MessageSquare, Clock, Paperclip, Download, ArrowLeft } from 'lucide-react';
import { useTickets } from '../context/TicketContext';
import { usePlatform } from '../context/PlatformContext';
import { INITIAL_BRANCHES } from '../data';
import type { Ticket, Priority, Status, TicketMessage, TicketAttachment } from '../types';
import { uploadAttachment } from '../lib/storage';

interface Props {
  ticket: Ticket;
  onClose: () => void;
}

export default function TicketDetail({ ticket, onClose }: Props) {
  const { updateTicket, deleteTicket, addNote, addMessage, agents, currentAgent } = useTickets();
  const { canned } = usePlatform();
  const [status, setStatus] = useState<Status>(ticket.status);
  const [priority, setPriority] = useState<Priority>(ticket.priority);
  const [assigneeId, setAssigneeId] = useState(ticket.assignee_id || '');
  const [branch, setBranch] = useState(ticket.branch || '');
  const [noteText, setNoteText] = useState('');
  const [replyText, setReplyText] = useState('');
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [attachError, setAttachError] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const isAdmin = !!currentAgent?.is_admin;
  /* Clear New/unread indicator when agent opens the ticket */
  useEffect(() => {
    const tags = ticket.tags || [];
    const needs =
      tags.includes('unread') ||
      ticket.status === 'new';
    if (!needs) return;
    const nextTags = tags.filter((t) => t !== 'unread');
    void updateTicket(ticket.id, {
      ...(ticket.status === 'new' ? { status: 'open' as Status } : {}),
      tags: nextTags,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.id]);


  const branchOptions = useMemo(() => {
    const set = new Set(INITIAL_BRANCHES.map((b) => b.name));
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) (JSON.parse(raw) as { name: string }[]).forEach((b) => set.add(b.name));
    } catch {}
    if (ticket.branch) set.add(ticket.branch);
    return Array.from(set).sort();
  }, [ticket.branch]);

  const slaBreached =
    ticket.sla_due_at && ticket.status !== 'resolved'
      ? new Date(ticket.sla_due_at).getTime() < Date.now()
      : false;

  const save = async () => {
    setSaving(true);
    try {
      await updateTicket(ticket.id, {
        status,
        priority,
        assignee_id: assigneeId || null,
        branch: branch.trim() || undefined,
      });
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!isAdmin) {
      alert('Only admins can permanently delete tickets.');
      return;
    }
    setSaving(true);
    try {
      await deleteTicket(ticket.id);
      onClose();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Delete failed');
    } finally {
      setSaving(false);
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim()) return;
    await addNote(ticket.id, noteText);
    setNoteText('');
  };

  const handleReply = async () => {
    if (!replyText.trim()) return;
    await addMessage(ticket.id, replyText, 'public');
    setReplyText('');
  };

  const onFile = async (file: File) => {
    setAttachError('');
    setUploading(true);
    try {
      const uploaded = await uploadAttachment(file, `tickets/${ticket.id}`);
      const att: TicketAttachment = {
        id: `att-${Date.now()}`,
        name: uploaded.name,
        size: uploaded.size,
        mime: uploaded.mime,
        url: uploaded.url,
        created_at: new Date().toISOString(),
        uploaded_by: currentAgent?.name || 'Agent',
      };
      const attachments = [...(ticket.attachments || []), att];
      await updateTicket(ticket.id, { attachments } as Parameters<typeof updateTicket>[1]);
    } catch (e) {
      setAttachError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const removeAttachment = async (id: string) => {
    const attachments = (ticket.attachments || []).filter((a) => a.id !== id);
    await updateTicket(ticket.id, { attachments } as Parameters<typeof updateTicket>[1]);
  };

  const thread: TicketMessage[] = [
    ...(ticket.messages || []),
    ...(ticket.notes || []).map((n) => ({
      id: n.id,
      text: n.text,
      author: n.author,
      kind: 'internal' as const,
      created_at: n.created_at,
    })),
  ].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

  return (
    <div className="ticket-detail-page w-full max-w-5xl mx-auto space-y-4 pb-8">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-sm font-medium px-3 py-2 rounded-lg border border-slate-200 dark:border-white/15 bg-white/80 dark:bg-white/5 text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-white/10 transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Tickets
        </button>
        <div className="text-xs font-mono text-slate-500 dark:text-slate-400">{ticket.id}</div>
        {((ticket.tags || []).includes('unread') || ticket.status === 'new') && (
          <span className="ticket-new-badge text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded">New</span>
        )}
      </div>

      <div className="ticket-detail-panel rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm overflow-hidden">
        <div className="ticket-detail-header px-5 sm:px-6 py-4 border-b flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50 leading-tight tracking-tight">
              {ticket.title}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Submitted {new Date(ticket.created_at).toLocaleString()}
              {ticket.channel ? ` · ${ticket.channel}` : ''}
            </p>
          </div>
        </div>

        <div className="p-5 sm:p-6 space-y-6">
          {ticket.sla_due_at && (
            <div className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2 ${
              slaBreached ? 'bg-rose-50 text-rose-700' : 'bg-slate-50 text-slate-600'
            }`}>
              <Clock size={14} />
              SLA due {new Date(ticket.sla_due_at).toLocaleString()}
              {slaBreached && <span className="font-semibold">· Breached</span>}
            </div>
          )}

          <div>
            <div className="text-xs font-medium text-slate-400 uppercase mb-1">Customer</div>
            <div className="text-sm font-medium text-slate-800">{ticket.customer_name}</div>
            {ticket.customer_email && <div className="text-xs text-slate-500">{ticket.customer_email}</div>}
          </div>

          <div>
            <div className="text-xs font-medium text-slate-400 uppercase mb-1">Description</div>
            <p className="text-sm text-slate-700 whitespace-pre-wrap">{ticket.description || 'No description provided.'}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs font-medium text-slate-400 uppercase mb-1">Channel</div>
              <div className="text-sm capitalize text-slate-800">{ticket.channel}</div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-400 uppercase mb-1">Created</div>
              <div className="text-sm text-slate-800">{new Date(ticket.created_at).toLocaleString()}</div>
            </div>
          </div>

          <hr className="border-slate-200" />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Branch</label>
            <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="">Unassigned</option>
              {branchOptions.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <select value={status} onChange={(e) => setStatus(e.target.value as Status)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="new">New</option>
              <option value="open">Open</option>
              <option value="pending">Pending</option>
              <option value="on-hold">On Hold</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Assignee</label>
            <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="">Unassigned</option>
              {agents.map((a) => (
                <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
              ))}
            </select>
          </div>

          <button type="button" onClick={save} disabled={saving} className="w-full py-2.5 bg-sky-600 text-white text-sm font-medium rounded-lg hover:bg-sky-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Changes'}
          </button>

          <hr className="border-slate-200" />

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-1.5">
                <Paperclip size={14} /> Attachments
              </h3>
              <button type="button" onClick={() => fileRef.current?.click()} disabled={uploading} className="text-xs font-medium text-sky-600 hover:underline disabled:opacity-50">
                {uploading ? 'Uploading…' : '+ Add file'}
              </button>
              <input ref={fileRef} type="file" className="hidden" onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) onFile(f);
                e.target.value = '';
              }} />
            </div>
            {attachError && <p className="text-xs text-rose-600 mb-2">{attachError}</p>}
            <p className="text-[11px] text-slate-400 mb-2">Uses Supabase Storage when connected; otherwise local data URL (max ~400KB).</p>
            <div className="space-y-1.5">
              {(ticket.attachments || []).length === 0 && <p className="text-xs text-slate-400">No attachments</p>}
              {(ticket.attachments || []).map((a) => (
                <div key={a.id} className="flex items-center gap-2 text-sm bg-slate-50 rounded-lg px-3 py-2">
                  <div className="min-w-0 flex-1">
                    <div className="font-medium text-slate-800 truncate">{a.name}</div>
                    <div className="text-[10px] text-slate-400">{(a.size / 1024).toFixed(1)} KB · {a.uploaded_by || 'Unknown'}</div>
                  </div>
                  <a href={a.url} download={a.name} target="_blank" rel="noreferrer" className="p-1 text-slate-400 hover:text-sky-600"><Download size={14} /></a>
                  <button type="button" onClick={() => removeAttachment(a.id)} className="p-1 text-slate-400 hover:text-rose-600"><Trash2 size={14} /></button>
                </div>
              ))}
            </div>
          </div>

          <hr className="border-slate-200" />

          <div>
            <h3 className="text-sm font-semibold text-slate-800 mb-2">Reply to customer</h3>
            {canned.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                {canned.map((c) => (
                  <button key={c.id} type="button" onClick={() => setReplyText(c.body)} className="text-[10px] px-2 py-1 rounded-full bg-slate-100 text-slate-600 hover:bg-sky-50 hover:text-sky-700">{c.shortcut || c.title}</button>
                ))}
              </div>
            )}
            <div className="flex gap-2">
              <input value={replyText} onChange={(e) => setReplyText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleReply()} placeholder="Public reply…" className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/30" />
              <button type="button" onClick={handleReply} disabled={!replyText.trim()} className="px-3 py-2 text-sm font-medium bg-sky-600 text-white rounded-lg disabled:opacity-40">Send</button>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare size={16} className="text-slate-400" />
              <h3 className="text-sm font-semibold text-slate-800">Conversation</h3>
            </div>
            <div className="space-y-2 mb-3 max-h-48 overflow-y-auto">
              {thread.length === 0 && <p className="text-xs text-slate-400">No messages yet</p>}
              {thread.map((n) => (
                <div key={n.id} className={`rounded-lg px-3 py-2 text-sm ${n.kind === 'public' ? 'bg-sky-50 border border-sky-100' : 'bg-slate-50'}`}>
                  <span className="text-[10px] font-semibold uppercase text-slate-400">{n.kind === 'public' ? 'Public' : 'Internal'}</span>
                  <div className="text-slate-700">{n.text}</div>
                  <div className="text-[10px] text-slate-400 mt-1">{n.author} · {new Date(n.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input value={noteText} onChange={(e) => setNoteText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleAddNote()} placeholder="Internal note…" className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg" />
              <button type="button" onClick={handleAddNote} disabled={!noteText.trim()} className="px-3 py-2 text-sm font-medium bg-slate-100 hover:bg-slate-200 rounded-lg disabled:opacity-40">Note</button>
            </div>
          </div>

          <hr className="border-slate-200" />

          {isAdmin ? (
            !confirmDelete ? (
              <button type="button" onClick={() => setConfirmDelete(true)} className="w-full py-2 text-sm font-medium text-rose-600 hover:bg-rose-50 rounded-lg flex items-center justify-center gap-2">
                <Trash2 size={16} /> Delete ticket
              </button>
            ) : (
              <div className="flex gap-2">
                <button type="button" onClick={handleDelete} disabled={saving} className="flex-1 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg disabled:opacity-50">Confirm delete</button>
                <button type="button" onClick={() => setConfirmDelete(false)} className="flex-1 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
              </div>
            )
          ) : (
            <p className="text-xs text-slate-400 text-center">Ticket delete is admin-only. Soft-close by setting status to Resolved.</p>
          )}
        </div>
      </div>
    </div>
  );
}
