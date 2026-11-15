#!/usr/bin/env python3
"""Ticket detail: popup glass modal instead of inline under table."""
from pathlib import Path

p = Path('src/components/TicketDetail.tsx')
if not p.exists() or p.stat().st_size < 5000:
    print('TicketDetail skip')
    raise SystemExit(0)

s = p.read_text()
if 'TICKET_DETAIL_MODAL_V1' in s:
    print('already')
    raise SystemExit(0)

old_open = '''  return (
    <>
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
'''

new_open = '''  return (
    <>
    {/* TICKET_DETAIL_MODAL_V1 — glass popup; theme-aware transparent card, solid text */}
    <div
      className="fixed inset-0 z-[70] flex items-start sm:items-center justify-center p-3 sm:p-5 overflow-y-auto bg-slate-900/40 dark:bg-black/55 backdrop-blur-[3px]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Ticket details"
    >
      <div
        className="ticket-detail-page relative w-full max-w-3xl my-4 sm:my-6 max-h-[min(92vh,920px)] overflow-y-auto space-y-4 rounded-2xl border border-slate-200/70 dark:border-white/15 bg-white/75 dark:bg-zinc-950/60 backdrop-blur-xl shadow-2xl shadow-black/25 p-4 sm:p-5 text-slate-900 dark:text-zinc-50"
        onClick={(e) => e.stopPropagation()}
      >
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-sm font-medium px-3 py-2 rounded-lg border border-slate-300/80 dark:border-white/20 bg-white/90 dark:bg-white/10 text-slate-800 dark:text-zinc-100 hover:bg-white dark:hover:bg-white/15 transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Tickets
        </button>
        <div className="text-xs font-mono text-slate-600 dark:text-zinc-300">{ticket.id}</div>
        {((ticket.tags || []).includes('unread') || ticket.status === 'new') && (
          <span className="ticket-new-badge text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded">New</span>
        )}
        <button
          type="button"
          onClick={onClose}
          className="ml-auto p-2 rounded-lg text-slate-500 dark:text-zinc-400 hover:bg-slate-200/70 dark:hover:bg-white/10"
          aria-label="Close"
        >
          <X size={18} />
        </button>
      </div>

      <div className="ticket-detail-panel rounded-2xl border border-slate-200/60 dark:border-white/10 bg-white/50 dark:bg-black/20 overflow-hidden">
'''

if old_open not in s:
    if 'ticket-detail-page w-full max-w-5xl' not in s:
        print('open pattern miss')
        raise SystemExit(1)
    s = s.replace(
        '<div className="ticket-detail-page w-full max-w-5xl mx-auto space-y-4 pb-8">',
        '''{/* TICKET_DETAIL_MODAL_V1 */}
    <div
      className="fixed inset-0 z-[70] flex items-start sm:items-center justify-center p-3 sm:p-5 overflow-y-auto bg-slate-900/40 dark:bg-black/55 backdrop-blur-[3px]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="ticket-detail-page relative w-full max-w-3xl my-4 sm:my-6 max-h-[min(92vh,920px)] overflow-y-auto space-y-4 rounded-2xl border border-slate-200/70 dark:border-white/15 bg-white/75 dark:bg-zinc-950/60 backdrop-blur-xl shadow-2xl p-4 sm:p-5 text-slate-900 dark:text-zinc-50"
        onClick={(e) => e.stopPropagation()}
      >''',
        1,
    )
    s = s.replace(
        'ticket-detail-panel rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm overflow-hidden',
        'ticket-detail-panel rounded-2xl border border-slate-200/60 dark:border-white/10 bg-white/50 dark:bg-black/20 overflow-hidden',
        1,
    )
    print('soft open')
else:
    s = s.replace(old_open, new_open, 1)
    print('open replaced')

old_close = '''        </div>
      </div>
    </div>

      {showSaved && ('''

new_close = '''        </div>
      </div>
    </div>
    </div>

      {showSaved && ('''

if old_close in s:
    s = s.replace(old_close, new_close, 1)
    print('close replaced')
else:
    marker = '\n      {showSaved && ('
    if marker in s and 'TICKET_DETAIL_MODAL_V1' in s:
        before = s.split(marker, 1)[0]
        if before.count('<div') > before.count('</div>'):
            s = s.replace(marker, '\n    </div>\n\n      {showSaved && (', 1)
            print('inserted overlay close')
        else:
            print('close heuristic skip')
    else:
        print('close pattern miss')

bal = s.count('{') - s.count('}')
p.write_text(s)
print('braces', bal)
print('has modal', 'TICKET_DETAIL_MODAL_V1' in s)
if bal != 0:
    raise SystemExit(f'brace imbalance {bal}')
print('patch_ticket_detail_modal_v1 done')
