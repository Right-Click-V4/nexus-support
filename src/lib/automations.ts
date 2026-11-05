import type { Automation, Priority, Ticket } from '../types';

/** Normalize rules from UI / localStorage / optional legacy `actions` JSON. */
export function normalizeAutomation(raw: Record<string, unknown> | Automation): Automation {
  const r = raw as Record<string, unknown>;
  let condition_field = String(r.condition_field || '');
  let condition_op = String(r.condition_op || 'contains');
  let condition_value = String(r.condition_value || '');
  let action = String(r.action || '');
  let action_value = String(r.action_value || '');

  // Legacy / DB shape: actions: [{ type, value, field, op, ... }]
  const actions = r.actions;
  if (Array.isArray(actions) && actions.length) {
    for (const a of actions as Array<Record<string, unknown>>) {
      const t = String(a.type || a.action || '').toLowerCase();
      if (t === 'set_priority' || t === 'priority') {
        action = 'set_priority';
        action_value = String(a.value || a.priority || action_value);
      }
      if (t === 'add_tag' || t === 'tag') {
        action = action || 'add_tag';
        if (!action_value) action_value = String(a.value || a.tag || '');
      }
      if (a.field || a.condition_field) condition_field = String(a.field || a.condition_field);
      if (a.op || a.condition_op) condition_op = String(a.op || a.condition_op);
      if (a.contains || a.value_match || a.condition_value) {
        condition_value = String(a.contains || a.value_match || a.condition_value || condition_value);
      }
    }
  }

  if (!condition_field) condition_field = 'title';
  if (!action) action = 'set_priority';

  return {
    id: String(r.id || ''),
    name: String(r.name || 'Rule'),
    trigger: String(r.trigger || 'ticket_created'),
    enabled: r.enabled !== false && r.active !== false,
    active: r.active !== false && r.enabled !== false,
    condition_field,
    condition_op,
    condition_value,
    action,
    action_value,
    description: r.description ? String(r.description) : undefined,
  };
}

/** Apply enabled automations to a new ticket draft. Returns mutated fields. */
export function applyTicketCreatedAutomations(
  ticket: Pick<Ticket, 'title' | 'description' | 'priority' | 'branch' | 'customer_name'>,
  rules: Array<Automation | Record<string, unknown>>
): { priority?: Priority; tagAdds?: string[] } {
  const out: { priority?: Priority; tagAdds?: string[] } = {};
  const enabled = (rules || [])
    .map((r) => normalizeAutomation(r as Automation))
    .filter((r) => r.enabled !== false && r.active !== false);

  for (const rule of enabled) {
    if (rule.trigger && rule.trigger !== 'ticket_created') continue;
    const field = (rule.condition_field || 'title').toLowerCase();
    const op = (rule.condition_op || 'contains').toLowerCase();
    const expected = (rule.condition_value || '').toLowerCase().trim();
    if (!expected) continue;

    let actual = '';
    if (field === 'title') actual = (ticket.title || '').toLowerCase();
    else if (field === 'description') actual = (ticket.description || '').toLowerCase();
    else if (field === 'priority') actual = (ticket.priority || '').toLowerCase();
    else if (field === 'branch') actual = (ticket.branch || '').toLowerCase();
    else if (field === 'customer') actual = (ticket.customer_name || '').toLowerCase();
    else actual = `${ticket.title || ''} ${ticket.description || ''}`.toLowerCase();

    let match = false;
    if (op === 'equals') match = actual === expected;
    else match = actual.includes(expected);

    if (!match) continue;

    const action = (rule.action || 'set_priority').toLowerCase();
    const value = (rule.action_value || '').trim();

    if (action === 'set_priority' && ['critical', 'high', 'medium', 'low'].includes(value)) {
      out.priority = value as Priority;
    }
    if ((action === 'add_tag' || action === 'tag') && value) {
      out.tagAdds = [...(out.tagAdds || []), value];
    }
  }

  return out;
}
