#!/usr/bin/env python3
"""Submit Ticket layout like Overview: full-width grid, transparent glass cards."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "submit-overview-layout-v1" in c:
    print("already")
    raise SystemExit(0)

start = c.find("            {view === 'submit' && (")
end = c.find("            {view === 'success' && created && (")
if start < 0 or end < 0 or end <= start:
    print("block miss", start, end)
    raise SystemExit(1)

new_block = r'''            {view === 'submit' && (
              <div className="w-full max-w-5xl mx-auto space-y-4 pb-2">
                <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-5">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-300/90">
                    Support
                  </p>
                  <h1 className="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
                    Submit a Ticket
                  </h1>
                  <p className="mt-1.5 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed max-w-2xl">
                    We typically respond within one business day. Use the form on the left and the guides on the right if you are unsure which subject or priority to pick.
                  </p>
                </section>

                <div className="grid lg:grid-cols-12 gap-4 items-start">
                  <form
                    onSubmit={submit}
                    className="lg:col-span-5 portal-overview-glass rounded-2xl p-4 sm:p-5 space-y-3.5 relative z-20"
                  >
                    {error && (
                      <div className="text-sm text-rose-600 bg-rose-50/80 dark:bg-rose-950/40 dark:text-rose-300 px-3 py-2 rounded-lg">
                        {error}
                      </div>
                    )}
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Your name</label>
                      <input
                        value={name}
                        readOnly
                        required
                        className={`${field} opacity-90 cursor-not-allowed bg-white/40 dark:bg-white/5`}
                        title="Filled from your account — cannot be changed"
                      />
                      <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Locked to your registered account name.</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Branch *</label>
                      <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                        <option value="" disabled>
                          Select branch…
                        </option>
                        {branchOptions.map((b) => (
                          <option key={b} value={b}>{b}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Subject *</label>
                      <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
                        <option value="" disabled>
                          Select a request type…
                        </option>
                        {SUBJECT_OPTIONS.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                      <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Choose the closest match — clarify in Details.</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Details</label>
                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={4}
                        placeholder="Describe what happened, steps to reproduce, and any error messages…"
                        className={field}
                      />
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <label className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-violet-700 dark:text-violet-300 bg-violet-500/10 hover:bg-violet-500/15 border border-violet-500/20 cursor-pointer transition-colors">
                          <ImagePlus size={14} />
                          {attachPreview ? 'Change photo' : 'Add photo'}
                          <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              e.target.value = '';
                              setAttachError('');
                              if (!file) return;
                              if (!file.type.startsWith('image/')) {
                                setAttachError('Please choose an image file.');
                                return;
                              }
                              if (file.size > MAX_ATTACHMENT_BYTES) {
                                setAttachError('Image is too large (max 8 MB).');
                                return;
                              }
                              const reader = new FileReader();
                              reader.onload = () => {
                                setAttachPreview({
                                  name: file.name,
                                  size: file.size,
                                  mime: file.type,
                                  url: String(reader.result || ''),
                                });
                              };
                              reader.onerror = () => setAttachError('Could not read that image.');
                              reader.readAsDataURL(file);
                            }}
                          />
                        </label>
                        <span className="text-[11px] text-zinc-500 dark:text-zinc-400">Optional · max 8 MB</span>
                        {attachPreview && (
                          <button
                            type="button"
                            onClick={() => { setAttachPreview(null); setAttachError(''); }}
                            className="inline-flex items-center gap-1 text-[11px] text-zinc-600 dark:text-zinc-300 hover:text-rose-600"
                          >
                            <X size={12} /> Remove
                          </button>
                        )}
                      </div>
                      {attachError && <p className="text-[11px] text-rose-600 mt-1">{attachError}</p>}
                      {attachPreview && (
                        <div className="mt-2 rounded-lg overflow-hidden border border-white/30 dark:border-white/10 max-w-xs bg-white/20 dark:bg-black/20">
                          <img src={attachPreview.url} alt={attachPreview.name} className="max-h-36 w-full object-contain" />
                          <div className="px-2 py-1 text-[10px] text-zinc-500 truncate">{attachPreview.name}</div>
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1.5">Priority</label>
                      <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className={field}>
                        {([
                          { value: 'low', label: 'Low' },
                          { value: 'medium', label: 'Medium' },
                          { value: 'high', label: 'High' },
                          { value: 'critical', label: 'Critical' },
                        ] as { value: Priority; label: string }[]).map((p) => (
                          <option key={p.value} value={p.value}>{p.label}</option>
                        ))}
                      </select>
                    </div>
                    <button type="submit" disabled={saving} className={btnPrimary}>
                      {saving ? 'Submitting…' : 'Submit a Ticket'}
                    </button>
                  </form>

                  <div className="lg:col-span-7 space-y-4">
                    <div className="grid sm:grid-cols-2 gap-4">
                      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                        <div className="flex items-center gap-2 mb-2.5">
                          <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-700 dark:text-violet-300 flex items-center justify-center">
                            <Ticket size={16} />
                          </div>
                          <div>
                            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">What is a ticket?</h2>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Why this form exists</p>
                          </div>
                        </div>
                        <div className="space-y-2 text-xs sm:text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
                          <p>
                            A <span className="font-medium text-zinc-900 dark:text-zinc-100">ticket</span> is a tracked support request.
                            Submitting one creates a clear record for our team with your branch and priority.
                          </p>
                          <p>
                            After you send it, you get a ticket ID to follow under <span className="font-medium">Track Ticket</span> or <span className="font-medium">My Tickets</span>.
                          </p>
                          <ul className="list-disc pl-4 space-y-1 text-[11px] sm:text-xs text-zinc-600 dark:text-zinc-400">
                            <li>Match the closest <span className="font-medium text-zinc-800 dark:text-zinc-200">Subject</span>.</li>
                            <li>Add clear <span className="font-medium text-zinc-800 dark:text-zinc-200">Details</span> (photo optional).</li>
                            <li>Set <span className="font-medium text-zinc-800 dark:text-zinc-200">Priority</span> honestly for triage.</li>
                          </ul>
                        </div>
                      </section>

                      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 mb-1">Priority guide</h2>
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mb-2.5">Match impact at your branch.</p>
                        <div className="space-y-2">
                          {PRIORITY_GUIDE.map((p) => (
                            <div
                              key={p.level}
                              className="flex gap-2.5 items-start rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3 py-2"
                            >
                              <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${p.color}`} />
                              <div className="min-w-0">
                                <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">{p.level}</div>
                                <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug mt-0.5">{p.tip}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </section>
                    </div>

                    <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
                      <div className="flex items-end justify-between gap-3 mb-3">
                        <div>
                          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Subject guide</h2>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5">
                            Pick the subject that best describes the main problem, then clarify in Details.
                          </p>
                        </div>
                      </div>
                      <div className="grid sm:grid-cols-2 gap-2">
                        {SUBJECT_GUIDE.map((item) => (
                          <div
                            key={item.subject}
                            className={`rounded-xl border px-3 py-2 transition-colors ${
                              title === item.subject
                                ? 'border-violet-400/50 bg-violet-500/15'
                                : 'border-white/25 dark:border-white/10 bg-white/20 dark:bg-black/15'
                            }`}
                          >
                            <div className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 leading-snug">{item.subject}</div>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-snug mt-0.5">{item.tip}</p>
                          </div>
                        ))}
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            )}
'''

c = c[:start] + new_block + c[end:]

if "submit-overview-layout-v1" not in c:
    c = c.replace("/* submit-guide-v1 */", "/* submit-guide-v1 */ /* submit-overview-layout-v1 */", 1)

cp.write_text(c)
print("done", "submit-overview-layout-v1" in c)
