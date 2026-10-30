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
  if (text == null || typeof text !== 'string' || !text.startsWith(PREFIX)) return { text: text || '' };
  const rest = text.slice(PREFIX.length);
  const nl = rest.indexOf('\n');
  const jsonPart = nl === -1 ? rest : rest.slice(0, nl);
  const caption = nl === -1 ? '' : rest.slice(nl + 1);
  try {
    const att = JSON.parse(jsonPart) as ChatAtt;
    if (!att?.url) return { text };
    return { att, text: caption };
  } catch {
    return { text };
  }
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
