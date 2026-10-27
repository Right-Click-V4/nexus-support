import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Send, Users, ArrowLeft, Plus, Search, BellOff, Bell, Pin,
  Info, Hash, LogOut, X, Pencil, Trash2,
} from 'lucide-react';

/* Restored via deploy write_pcc — temporary stub replaced immediately */
export default function PortalCommunityChat(_props: {
  displayName: string;
  email: string;
  onBack?: () => void;
}) {
  return (
    <div className="portal-community-shell flex flex-1 min-h-0 h-full items-center justify-center rounded-xl border border-zinc-200 bg-white/90 text-sm text-zinc-500">
      Loading community…
    </div>
  );
}
