"""Sync customer branch to customers table; calm flybys; better hero escort; login card polish."""
from pathlib import Path

auth = Path('src/context/AuthContext.tsx')
if auth.exists():
    s = auth.read_text()
    if 'SYNC_CUSTOMER_BRANCH_V1' not in s:
        old = '''    const { data: res, error } = await supabase.auth.updateUser({ data: payload });
    if (error) throw friendlyAuthError(error);
    if (res.user) setUser(res.user);
    if (res.session) setSession(res.session);
  };'''
        new = '''    const { data: res, error } = await supabase.auth.updateUser({ data: payload });
    if (error) throw friendlyAuthError(error);
    if (res.user) setUser(res.user);
    if (res.session) setSession(res.session);
    // SYNC_CUSTOMER_BRANCH_V1 — mirror branch onto customers row so Users tab sees it
    try {
      const email = (res.user?.email || '').trim().toLowerCase();
      if (email && data.branch !== undefined) {
        const branchVal = String(data.branch || '').trim().toUpperCase() || null;
        const name =
          (res.user?.user_metadata as any)?.full_name ||
          (res.user?.user_metadata as any)?.name ||
          email.split('@')[0];
        const { data: existing } = await supabase
          .from('customers')
          .select('id')
          .eq('email', email)
          .maybeSingle();
        if (existing?.id) {
          await supabase.from('customers').update({ branch: branchVal, name }).eq('id', existing.id);
        } else {
          await supabase.from('customers').insert({
            name,
            email,
            branch: branchVal,
            role: 'Customer',
            status: 'approved',
          });
        }
      }
    } catch (e) {
      console.warn('customer branch sync', e);
    }
  };'''
        if old in s:
            s = s.replace(old, new, 1)
            print('updateProfile sync')
        su = '''      if (error) throw friendlyAuthError(error);
      if (data.session) {
        await supabase.auth.signOut();
      }
    } finally {
      setAuthBusy(false);
    }
  };

  const resetPassword'''
        su_new = '''      if (error) throw friendlyAuthError(error);
      // SYNC_CUSTOMER_BRANCH_SIGNUP
      try {
        if (role === 'customer' && data.user?.email) {
          const email = data.user.email.trim().toLowerCase();
          const branchVal = branch ? branch.trim().toUpperCase() : null;
          const name = fullName || email.split('@')[0];
          const { data: existing } = await supabase
            .from('customers')
            .select('id')
            .eq('email', email)
            .maybeSingle();
          if (existing?.id) {
            await supabase.from('customers').update({ branch: branchVal, name }).eq('id', existing.id);
          } else {
            await supabase.from('customers').insert({
              name,
              email,
              branch: branchVal,
              role: 'Customer',
              status: 'pending',
            });
          }
        }
      } catch (e) {
        console.warn('signup customer row', e);
      }
      if (data.session) {
        await supabase.auth.signOut();
      }
    } finally {
      setAuthBusy(false);
    }
  };

  const resetPassword'''
        if su in s:
            s = s.replace(su, su_new, 1)
            print('signup sync')
        auth.write_text(s)
    else:
        print('auth already')
else:
    print('auth missing')

fly = Path('src/components/LoginFlybys.tsx')
if fly.exists():
    s = fly.read_text()
    broken = """      timer = setTimeout(schedule, gaps[Math.floor(Math.random() * gaps.length)] * 1000);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);"""
    fixed = """      timer = setTimeout(schedule, gaps[Math.floor(Math.random() * gaps.length)] * 1000);
    };

    timer = setTimeout(schedule, 3500 + Math.random() * 2500);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);"""
    if broken in s:
        s = s.replace(broken, fixed, 1)
        print('repaired broken schedule')
    if 'FLYBY_CALM_V2' not in s:
        s = s.replace('setFlybys((prev) => [...prev.slice(-2),', 'setFlybys((prev) => [ /* FLYBY_CALM_V2 */ ')
        s = s.replace('setFlybys((prev) => [...prev.slice(-1),', 'setFlybys((prev) => [ /* FLYBY_CALM_V2 */ ')
        for old_g, new_g in [
            ('const gaps = [12, 16, 20, 26, 32];', 'const gaps = [18, 22, 28, 34, 40]; // FLYBY_CALM_V2'),
            ('const gaps = [10,11,12,13,14,15];', 'const gaps = [18, 22, 28, 34, 40]; // FLYBY_CALM_V2'),
            ('const gaps = [16, 22, 28, 34, 42];', 'const gaps = [18, 22, 28, 34, 40]; // FLYBY_CALM_V2'),
        ]:
            if old_g in s:
                s = s.replace(old_g, new_g, 1)
                break
        s = s.replace(
            'timer = setTimeout(schedule, 1200 + Math.random() * 1000);',
            'timer = setTimeout(schedule, 3500 + Math.random() * 2500);',
        )
        s = s.replace(
            'timer = setTimeout(schedule, 2200 + Math.random() * 1800);',
            'timer = setTimeout(schedule, 3500 + Math.random() * 2500);',
        )
        print('flyby calm soft')
    fly.write_text(s)
else:
    print('fly missing')

scene = Path('src/components/LoginScene.tsx')
if scene.exists():
    s = scene.read_text()
    if 'HERO_ESCORT_V2' not in s:
        old_curious_trigger = '''      if (
        mode !== 'portal' &&
        mode !== 'curious' &&
        craft &&
        now - lastCuriousAt > 9000 &&
        Math.random() < 0.014
      ) {
        mode = 'curious';
        curiousUntil = now + randomIn(2200, 4200);
        lastCuriousAt = now;
        modeSpeed = randomIn(1.4, 2.1);
        targetX = craft.x;
        targetY = craft.y;
        scaleGoal = randomIn(0.88, 1.12);
        if (craft.id !== lastChatCraftId && Math.random() < 0.75) {
          lastChatCraftId = craft.id;
          setHeroChat(HERO_CHATS[Math.floor(Math.random() * HERO_CHATS.length)]);
          chatUntil = now + 2200;
        }
      }
      if (mode === 'curious') {
        if (craft) {
          targetX = craft.x + (craft.dir === 'ltr' ? 28 : -28);
          targetY = craft.y + Math.sin(now * 0.004) * 10;
        }
        if (now >= curiousUntil || !craft) {
          mode = 'cruise';
          modeUntil = now + randomIn(1200, 2400);
          modeSpeed = randomIn(0.9, 1.3);
          pickTarget(sr.width, sr.height);
        }
      }'''
        new_curious = '''      // HERO_ESCORT_V2 — smooth escort alongside craft, not orbit-spin
      if (
        mode !== 'portal' &&
        mode !== 'curious' &&
        craft &&
        now - lastCuriousAt > 7000 &&
        Math.random() < 0.028
      ) {
        mode = 'curious';
        curiousUntil = now + randomIn(3800, 6200);
        lastCuriousAt = now;
        modeSpeed = randomIn(1.6, 2.4);
        scaleGoal = randomIn(0.95, 1.08);
        if (craft.id !== lastChatCraftId && Math.random() < 0.85) {
          lastChatCraftId = craft.id;
          setHeroChat(HERO_CHATS[Math.floor(Math.random() * HERO_CHATS.length)]);
          chatUntil = now + 2800;
        }
      }
      if (mode === 'curious') {
        if (craft) {
          const ahead = craft.dir === 'ltr' ? 56 : -56;
          const side = craft.dir === 'ltr' ? -22 : 22;
          targetX = craft.x + ahead;
          targetY = craft.y + side + Math.sin(now * 0.0028) * 6;
          modeSpeed = 2.2;
        }
        if (now >= curiousUntil || !craft) {
          mode = 'cruise';
          modeUntil = now + randomIn(1600, 2800);
          modeSpeed = randomIn(0.85, 1.2);
          pickTarget(sr.width, sr.height);
        }
      }'''
        if old_curious_trigger in s:
            s = s.replace(old_curious_trigger, new_curious, 1)
            print('hero escort')
        else:
            print('curious block miss')
        scene.write_text(s)
    else:
        print('scene already')
else:
    print('scene missing')

css = Path('src/login-glass.css')
if css.exists():
    t = css.read_text()
    if 'LOGIN_CARD_POLISH_V2' not in t:
        t = t.rstrip() + '''

/* LOGIN_CARD_POLISH_V2 */
.login-glass-card {
  background: linear-gradient(160deg, rgba(28, 16, 52, 0.92) 0%, rgba(14, 8, 32, 0.94) 55%, rgba(20, 10, 40, 0.92) 100%) !important;
  border: 1px solid rgba(196, 181, 253, 0.28) !important;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04) inset,
    0 24px 60px rgba(0, 0, 0, 0.45),
    0 0 80px rgba(124, 58, 237, 0.18) !important;
  backdrop-filter: blur(18px) saturate(1.2) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.2) !important;
  border-radius: 1.35rem !important;
  padding: 1.5rem 1.4rem 1.35rem !important;
}
.login-glass-card h2,
.login-glass-card .login-card-title {
  letter-spacing: -0.02em;
  color: #faf5ff !important;
}
.login-glass-input {
  background: rgba(8, 4, 20, 0.72) !important;
  border: 1px solid rgba(167, 139, 250, 0.28) !important;
  color: #f5f3ff !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.login-glass-input:focus {
  border-color: rgba(192, 132, 252, 0.65) !important;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.22) !important;
  outline: none !important;
}
.login-glass-card button[type="submit"],
.login-glass-card .login-btn-primary {
  background: linear-gradient(105deg, #a855f7 0%, #7c3aed 45%, #6366f1 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  box-shadow: 0 10px 28px rgba(124, 58, 237, 0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
  font-weight: 650 !important;
  letter-spacing: 0.01em;
}
.login-glass-card button[type="submit"]:hover,
.login-glass-card .login-btn-primary:hover {
  filter: brightness(1.06);
  transform: translateY(-1px);
}
.login-audience-tabs button {
  border-radius: 999px !important;
}
'''
        css.write_text(t)
        print('card css')
    else:
        print('css already')
else:
    print('css missing')

print('DONE')
