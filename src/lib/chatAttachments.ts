/* parse-safe-v1 */
/** Encode/decode file attachments inside chat message text (works without DB columns). */

export type ChatAtt = {
  url: string;
  name?: string;
  mime?: string;
};

const PREFIX = '__ATT__';

export function encodeChatAttachment(att: ChatAtt, caption?: string): string {
  const payload = JSON.stringify({
    url: att.url,
    name: att.name || 'file',
    mime: att.mime || 'application/octet-stream',
  });
  const cap = (caption || '').trim();
  return `${PREFIX}${payload}${cap ? `\n${cap}` : ''}`;
}

export function parseChatAttachment(text?: string | null): { att?: ChatAtt; text: string } {
  // LEGACY_JSON_ATT_V1
  if (text == null || typeof text !== 'string') return { text: text || '' };
  const raw = text.trim();
  if (!raw) return { text: '' };

  // Preferred: __ATT__{json}[\ncaption]
  if (raw.startsWith(PREFIX)) {
    const rest = raw.slice(PREFIX.length);
    const nl = rest.indexOf('\n');
    const jsonPart = nl === -1 ? rest : rest.slice(0, nl);
    const caption = nl === -1 ? '' : rest.slice(nl + 1);
    try {
      const att = JSON.parse(jsonPart) as ChatAtt;
      if (att?.url) return { att, text: caption };
    } catch { /* fall through */ }
    return { text: raw };
  }

  // Legacy / mistaken: plain {"url":"data:...","name":"...","mime":"..."}
  if (raw.startsWith('{') && (raw.includes('"url"') || raw.includes("'url'"))) {
    try {
      const obj = JSON.parse(raw) as ChatAtt & { __ATT__?: unknown };
      // Nested mistake: {"url":"__ATT__{...}"}
      if (typeof obj.url === 'string' && obj.url.startsWith(PREFIX)) {
        return parseChatAttachment(obj.url);
      }
      if (typeof obj.url === 'string' && (obj.url.startsWith('data:') || obj.url.startsWith('http'))) {
        return {
          att: {
            url: obj.url,
            name: obj.name || 'attachment',
            mime: obj.mime || (obj.url.startsWith('data:image') ? 'image/jpeg' : 'application/octet-stream'),
          },
          text: '',
        };
      }
    } catch { /* ignore */ }
  }

  return { text: raw };
}

export function isImageMime(mime?: string) {
  return !!mime && mime.startsWith('image/');
}

/** Read a File as data-URL then encode as chat attachment payload. */
export async function encodeChatFile(file: File, caption?: string): Promise<string> {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result || ''));
    r.onerror = () => reject(new Error('Could not read file'));
    r.readAsDataURL(file);
  });
  return encodeChatAttachment(
    { url: dataUrl, name: file.name, mime: file.type || 'application/octet-stream' },
    caption,
  );
}
