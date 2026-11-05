import type { Agent, Ticket } from '../types';

/** Whether the current agent can claim this ticket (open + unassigned). */
export function canClaimTicket(
  ticket: Pick<Ticket, 'assignee_id' | 'status' | 'deleted_at'> | null | undefined,
  agent: Pick<Agent, 'id'> | null | undefined,
): boolean {
  if (!ticket || !agent?.id) return false;
  if (ticket.deleted_at) return false;
  if (ticket.assignee_id) return false;
  const s = (ticket.status || '').toLowerCase();
  if (s === 'resolved' || s === 'closed') return false;
  return true;
}
