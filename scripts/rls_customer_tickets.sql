-- Run in Supabase SQL Editor so customers can see their own tickets + agents online status.
-- Safe to re-run: drops policies by name first if they exist.

-- Tickets: authenticated users who are agents/admins see all;
-- customers see rows where customer_email matches their login email.
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

-- Agents: any signed-in user can read agent presence (needed for Live Chat "Active now")
DROP POLICY IF EXISTS "authenticated_read_agents" ON public.agents;
CREATE POLICY "authenticated_read_agents" ON public.agents
FOR SELECT TO authenticated
USING (true);

-- Optional: allow customers to insert tickets with their own email
DROP POLICY IF EXISTS "customers_insert_own_tickets" ON public.tickets;
CREATE POLICY "customers_insert_own_tickets" ON public.tickets
FOR INSERT TO authenticated
WITH CHECK (
  lower(coalesce(customer_email, '')) = lower(coalesce(auth.jwt() ->> 'email', ''))
  OR EXISTS (
    SELECT 1 FROM public.agents a WHERE a.user_id = auth.uid()
  )
);
