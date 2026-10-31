/* admin-ready-timeout-v1 */
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';

export function useIsAdmin() {
  const { user, loading } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!user || !supabase) {
      setIsAdmin(false);
      setReady(true);
      return;
    }
    const metaRole = String(user.user_metadata?.role || '');
    if (metaRole === 'admin') {
      setIsAdmin(true);
      setReady(true);
      return;
    }
    let cancelled = false;
    const failOpen = window.setTimeout(() => {
      if (!cancelled) {
        setIsAdmin(false);
        setReady(true);
      }
    }, 2500);
    (async () => {
      try {
        const { data } = await supabase
          .from('agents')
          .select('is_admin')
          .eq('user_id', user.id)
          .maybeSingle();
        let row = data;
        if (!row && user.email) {
          const { data: byEmail } = await supabase
            .from('agents')
            .select('is_admin')
            .eq('email', user.email)
            .maybeSingle();
          row = byEmail;
        }
        if (!cancelled) {
          setIsAdmin(!!row?.is_admin);
          setReady(true);
        }
      } catch {
        if (!cancelled) {
          setIsAdmin(false);
          setReady(true);
        }
      } finally {
        window.clearTimeout(failOpen);
      }
    })();
    return () => {
      cancelled = true;
      window.clearTimeout(failOpen);
    };
  }, [user, loading]);

  return { isAdmin, adminReady: ready && !loading };
}
