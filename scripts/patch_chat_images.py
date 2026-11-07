"""Fix live chat image send + render on portal and agent."""
from pathlib import Path
import re

plv = Path('src/components/PortalLiveChatView.tsx')
if plv.exists() and plv.stat().st_size > 1000:
    s = plv.read_text()
    old_file = """    try {
      const dataUrl = await encodeChatFile(file);
      await sendChatMessage(
        chatId,
        JSON.stringify({ url: dataUrl, name: file.name, mime: file.type || 'application/octet-stream' }),
        'customer',
      );
    } catch {
      setFileError('Could not attach file.');
    }"""
    new_file = """    try {
      const payload = await encodeChatFile(file);
      await sendChatMessage(chatId, payload, 'customer');
    } catch {
      setFileError('Could not attach file.');
    }"""
    if old_file in s:
        s = s.replace(old_file, new_file, 1)
        print('PLV onFile fixed')
    elif "JSON.stringify({ url: dataUrl" in s:
        s = re.sub(
            r"const dataUrl = await encodeChatFile\(file\);\s*await sendChatMessage\(\s*chatId,\s*JSON\.stringify\(\{ url: dataUrl, name: file\.name, mime: file\.type \|\| 'application/octet-stream' \}\),\s*'customer',\s*\);",
            "const payload = await encodeChatFile(file);\n      await sendChatMessage(chatId, payload, 'customer');",
            s, count=1,
        )
        print('PLV onFile fixed regex')
    if 'const parsed = parseChatAttachment' not in s and "const att = parseChatAttachment(m.text || m.body || '');" in s:
        s = s.replace(
            "const att = parseChatAttachment(m.text || m.body || '');",
            "const parsed = parseChatAttachment(m.text || m.body || '');\n            const att = parsed.att;\n            const displayText = (parsed.text || '').trim();",
            1,
        )
        old_body = """                  {att ? (
                    isImageMime(att.mime) ? (
                      <img src={att.url} alt={att.name} className=\"max-w-full rounded-lg\" />
                    ) : (
                      <a href={att.url} download={att.name} className=\"underline\">{att.name}</a>
                    )
                  ) : (
                    <div className=\"whitespace-pre-wrap break-words\">{m.text || m.body || ''}</div>
                  )}"""
        new_body = """                  {att ? (
                    <div className=\"space-y-1\">
                      {isImageMime(att.mime) || (att.url || '').startsWith('data:image') ? (
                        <img src={att.url} alt={att.name || 'attachment'} className=\"max-w-full max-h-64 rounded-lg object-contain\" />
                      ) : (
                        <a href={att.url} download={att.name} className=\"underline break-all text-sm\">{att.name || 'Download file'}</a>
                      )}
                      {displayText ? <div className=\"whitespace-pre-wrap break-words\">{displayText}</div> : null}
                    </div>
                  ) : (
                    <div className=\"whitespace-pre-wrap break-words\">{displayText || m.text || m.body || ''}</div>
                  )}"""
        if old_body in s:
            s = s.replace(old_body, new_body, 1)
            print('PLV render fixed')
    plv.write_text(s)
else:
    print('PLV skip')

lcp = Path('src/components/LiveChatPage.tsx')
if lcp.exists():
    s = lcp.read_text()
    if "from '../lib/chatAttachments'" not in s:
        m = re.search(r"^import .+$", s, re.M)
        if m:
            s = s[:m.end()] + "\nimport { parseChatAttachment, isImageMime } from '../lib/chatAttachments';" + s[m.end():]
            print('LCP import')
    if 'CHAT_ATT_RENDER_V1' not in s and 'parseChatAttachment' in s:
        helper = """
  // CHAT_ATT_RENDER_V1
  const renderChatBody = (raw?: string | null) => {
    const parsed = parseChatAttachment(raw || '');
    if (parsed.att) {
      const att = parsed.att;
      const isImg = isImageMime(att.mime) || (att.url || '').startsWith('data:image');
      return (
        <div className=\"space-y-1\">
          {isImg ? (
            <img src={att.url} alt={att.name || 'attachment'} className=\"max-w-full max-h-56 rounded-lg object-contain\" />
          ) : (
            <a href={att.url} download={att.name} className=\"underline break-all text-sm\">{att.name || 'Download file'}</a>
          )}
          {parsed.text ? <div className=\"whitespace-pre-wrap break-words\">{parsed.text}</div> : null}
        </div>
      );
    }
    return <div className=\"whitespace-pre-wrap break-words\">{raw || ''}</div>;
  };
"""
        idx = s.find('  return (\n    <div')
        if idx < 0:
            idx = s.find('  return (')
        if idx > 0:
            s = s[:idx] + helper + '\n' + s[idx:]
            print('LCP helper')
        old_block = """                  const body = (m.text || m.body || '').toString();
                  const isImg = /\\.(png|jpe?g|gif|webp)(\\?|$)/i.test(body) || body.includes('giphy.com') || body.includes('media.tenor');"""
        new_block = """                  const body = (m.text || m.body || '').toString();
                  const parsedAtt = parseChatAttachment(body);
                  const isImg = !parsedAtt.att && (/\\.(png|jpe?g|gif|webp)(\\?|$)/i.test(body) || body.includes('giphy.com') || body.includes('media.tenor'));"""
        if old_block in s:
            s = s.replace(old_block, new_block, 1)
            print('LCP vars')
        old_render = """                        {isImg ? (
                          <a href={body} target=\"_blank\" rel=\"noreferrer\" className=\"block\">
                            <img src={body} alt=\"media\" className=\"max-h-48 rounded-lg\" />
                          </a>
                        ) : body.startsWith('http') ? (
                          <a href={body} target=\"_blank\" rel=\"noreferrer\" className=\"underline break-all inline-flex items-center gap-1\">
                            {body} <ExternalLink size={12} />
                          </a>
                        ) : (
                          <div className=\"whitespace-pre-wrap break-words text-[15px] leading-relaxed\">{body}</div>
                        )}"""
        new_render = """                        {parsedAtt.att ? (
                          renderChatBody(body)
                        ) : isImg ? (
                          <a href={body} target=\"_blank\" rel=\"noreferrer\" className=\"block\">
                            <img src={body} alt=\"media\" className=\"max-h-48 rounded-lg\" />
                          </a>
                        ) : body.startsWith('http') ? (
                          <a href={body} target=\"_blank\" rel=\"noreferrer\" className=\"underline break-all inline-flex items-center gap-1\">
                            {body} <ExternalLink size={12} />
                          </a>
                        ) : (
                          <div className=\"whitespace-pre-wrap break-words text-[15px] leading-relaxed\">{body}</div>
                        )}"""
        if old_render in s:
            s = s.replace(old_render, new_render, 1)
            print('LCP render')
    lcp.write_text(s)
else:
    print('LCP skip')
print('chat images done')
