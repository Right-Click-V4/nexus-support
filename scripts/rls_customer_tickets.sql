-- Run in Supabase SQL Editor (Dashboard → SQL → New query → Run)
-- Fixes: empty My Tickets, cannot Submit a Ticket (RLS / Bad Request), no agents online

ALTER TABLE IF EXISTS public.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.agents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "customers_read_own_tickets" ON public.tickets;
CREATE POLICY "customers_read_own_tickets" ON public.tickets
FOR SELECT TO authenticated
USING (
  lower(coalesce(customer_email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  OR EXISTS (
    SELECT 1 FROM public.agents a
    WHERE a.user_id = auth.uid()
       OR lower(coalesce(a.email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
);

DROP POLICY IF EXISTS "customers_insert_own_tickets" ON public.tickets;
CREATE POLICY "customers_insert_own_tickets" ON public.tickets
FOR INSERT TO authenticated
WITH CHECK (
  lower(coalesce(customer_email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  OR EXISTS (
    SELECT 1 FROM public.agents a
    WHERE a.user_id = auth.uid()
       OR lower(coalesce(a.email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
);

DROP POLICY IF EXISTS "customers_update_own_tickets" ON public.tickets;
CREATE POLICY "customers_update_own_tickets" ON public.tickets
FOR UPDATE TO authenticated
USING (
  lower(coalesce(customer_email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  OR EXISTS (
    SELECT 1 FROM public.agents a
    WHERE a.user_id = auth.uid()
       OR lower(coalesce(a.email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
)
WITH CHECK (
  lower(coalesce(customer_email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  OR EXISTS (
    SELECT 1 FROM public.agents a
    WHERE a.user_id = auth.uid()
       OR lower(coalesce(a.email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
);

DROP POLICY IF EXISTS "authenticated_read_agents" ON public.agents;
CREATE POLICY "authenticated_read_agents" ON public.agents
FOR SELECT TO authenticated
USING (true);

DROP POLICY IF EXISTS "agents_update_own_row" ON public.agents;
CREATE POLICY "agents_update_own_row" ON public.agents
FOR UPDATE TO authenticated
USING (
  user_id = auth.uid()
  OR lower(coalesce(email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
)
WITH CHECK (
  user_id = auth.uid()
  OR lower(coalesce(email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
);
