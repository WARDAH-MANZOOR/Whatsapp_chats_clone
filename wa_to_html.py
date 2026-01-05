

# whatsapp_full_clone_fixed.py
# WhatsApp full chat clone with correct sides, replies, and media order

import os, re, html, pathlib, subprocess
from datetime import datetime

CHAT_FILE = "chat.txt"
MEDIA_DIR = "Media"
OUT_HTML = "whatsapp_full_clone.html"

# def convert_opus_to_mp3(file_path):
#     """Convert .opus file to .mp3 if not already converted."""
#     if not file_path.lower().endswith(".opus"):
#         return file_path
#     mp3_path = file_path[:-5] + ".mp3"
#     if not os.path.exists(mp3_path):
#         try:
#             subprocess.run(["ffmpeg", "-y", "-i", file_path, mp3_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             print(f"🎧 Converted {os.path.basename(file_path)} → {os.path.basename(mp3_path)}")
#         except Exception as e:
#             print(f"⚠️ Couldn't convert {file_path}: {e}")
#             return file_path
#     return mp3_path
def convert_opus_to_mp3(file_path):
    if not file_path.lower().endswith(".opus"):
        return file_path

    mp3_path = file_path[:-5] + ".mp3"

    if os.path.exists(mp3_path):
        return mp3_path

    print(f"🎧 Converting: {file_path}")

    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", file_path, mp3_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ FFmpeg error:")
            print(result.stderr)
            return file_path

        print(f"✅ Converted to MP3: {mp3_path}")
        return mp3_path

    except FileNotFoundError:
        print("❌ ffmpeg not found. Install ffmpeg & add to PATH.")
        return file_path


if not os.path.exists(CHAT_FILE):
    print("❌ Error: chat.txt not found in current folder.")
    raise SystemExit

# 🟢 Ask your name so your messages appear on right side
your_name = input("Enter your name (exactly as shown in WhatsApp export): ").strip()

lines = open(CHAT_FILE, encoding='utf-8', errors='ignore').read().splitlines()

patterns = [
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}(?:\s?[APMapm\.]{2,4})?)\s+-\s([^:]+):\s?(.*)$'),
    re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2})\]\s+([^:]+):\s?(.*)$'),
]

def match_line(line):
    for p in patterns:
        m = p.match(line)
        if m:
            return m.groups()
    return None

messages = []
for line in lines:
    m = match_line(line)
    if m:
        date, time, sender, text = m
        try:
            dt_obj = datetime.strptime(date.strip() + " " + time.strip(), "%d/%m/%Y %H:%M")
        except:
            dt_obj = None
        messages.append({
            "date": date.strip(),
            "time": time.strip(),
            "sender": sender.strip(),
            "text": text.strip(),
            "datetime": dt_obj
        })
    else:
        if messages:
            messages[-1]["text"] += "\n" + line.strip()

# 🧭 Sort by datetime if possible
messages.sort(key=lambda x: x["datetime"] or datetime.max)



# def find_media_in_text(text):
#     """Return exact media file path if message actually contains media."""
#     if not os.path.isdir(MEDIA_DIR):
#         return None

#     # Check if message actually has a media placeholder
#     indicators = ['<Media omitted>', 'attached', 'document omitted']
#     if not any(ind in text for ind in indicators):
#         return None  # no media in this message

#     # List all available media
#     available = {f.lower(): f for f in os.listdir(MEDIA_DIR)}

#     # Try to find a file that matches the text
#     # Often WhatsApp export names are like PTT-20250616-WA0014.opus
#     tokens = re.findall(r'[\w\-\._]+', text)
#     for token in tokens:
#         for ext in ['.opus','.mp3','.m4a','.ogg','.wav',
#                     '.jpg','.jpeg','.png','.gif','.mp4','.mov','.avi','docx','.pdf','.txt']:
#             fname = f"{token}{ext}".lower()
#             if fname in available:
#                 return os.path.join(MEDIA_DIR, available[fname])

#     # fallback: return first media file only if placeholder exists
#     for fname_lower, fname_real in available.items():
#         for ext in ['.opus','.mp3','.m4a','.ogg','.wav',
#                     '.jpg','.jpeg','.png','.gif','.mp4','.mov','.avi']:
#             if fname_lower.endswith(ext) and fname_lower in text.lower():
#                 return os.path.join(MEDIA_DIR, fname_real)

#     return None


# def find_media_in_text(text):
#     """Return media file path if message actually contains media (supports audio, video, images, docs)."""
#     if not os.path.isdir(MEDIA_DIR):
#         return None

#     # Only process if message indicates media
#     indicators = ['<Media omitted>', 'attached', 'document omitted']
#     if not any(ind in text for ind in indicators):
#         return None  # no media in this message

#     # text_lower = text.lower().replace('_', ' ').strip()
#     text_lower = text.lower()
#     files = os.listdir(MEDIA_DIR)
#     # files = os.listdir(MEDIA_DIR)

#     # First try exact or normalized match
#     for f in files:
#         f_lower = f.lower()
#         f_clean = f_lower.replace('_',' ').rsplit('.', 1)[0]  # remove extension
#         if f_clean in text_lower:
#             return os.path.join(MEDIA_DIR, f)

#     # Fallback: any word in text matches any part of filename
#     for f in files:
#         if f.lower() in text_lower:
#             return os.path.join(MEDIA_DIR, f)

#     return None

def find_media_in_text(text):
    """Detect media files by filename mention in chat text."""
    if not os.path.isdir(MEDIA_DIR):
        return None

    text_lower = text.lower()
    for f in os.listdir(MEDIA_DIR):
        if f.lower() in text_lower:
            return os.path.join(MEDIA_DIR, f)

    return None

# # 🔍 Find media referenced in text
# Keep track of which media files are already used


# 🧱 HTML structure
html_parts = ['''<!doctype html><html><head><meta charset="utf-8">
<title>WhatsApp Full Chat Clone</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Helvetica,Arial,sans-serif;background:#e5ddd5;padding:10px;margin:0}
.container{max-width:900px;margin:0 auto;background:#e5ddd5}
.header{font-weight:700;margin:10px;text-align:center}
.msg{display:block;clear:both;padding:8px 12px;margin:6px;border-radius:12px;max-width:78%;word-wrap:break-word}
.left{background:#fff;float:left}
.right{background:#dcf8c6;float:right}
.meta{font-size:11px;color:#555;margin-top:4px;opacity:0.8}
img{max-width:280px;border-radius:8px;margin-top:6px;display:block}
audio,video{width:260px;margin-top:6px;display:block}
.quote{background:#f0f0f0;border-left:3px solid #ccc;padding-left:6px;margin-bottom:4px;font-size:13px;color:#333}
.clear{clear:both}
</style></head><body>
<div class="container"><div class="header">💬 WhatsApp Chat Clone</div>
''']

# 🧩 Build chat bubbles
for msg in messages:
    sender = html.escape(msg["sender"])
    dt = html.escape(f'{msg["date"]} {msg["time"]}')
    text = msg["text"]
    bubble_side = "right" if sender.lower() == your_name.lower() else "left"

    html_parts.append(f'<div class="msg {bubble_side}">')
    html_parts.append(f'<strong>{sender}</strong>')

    # 🪄 Handle replies
    reply_match = re.search(r'\[In reply to (.+?)\]', text)
    if reply_match:
        replied_to = html.escape(reply_match.group(1))
        html_parts.append(f'<div class="quote">↪ Replying to: {replied_to}</div>')
        text = re.sub(r'\[In reply to .+?\]', '', text).strip()

    # 🔗 Handle media
    media_path = find_media_in_text(text)
    # if media_path:
    #     lower = media_path.lower()
    #     rel = media_path.replace('\\','/')

    #     # 🔊 NEW: Convert .opus to .mp3 automatically
    #     if lower.endswith(".opus"):
    #         media_path = convert_opus_to_mp3(media_path)
    #         rel = media_path.replace('\\','/')

    #     if lower.endswith(('.jpg','.jpeg','.png','.gif')):
    #         html_parts.append(f'<img src="{rel}" alt="image">')
    #     elif lower.endswith(('.mp4','.mov','.avi','.mkv')):
    #         html_parts.append(f'<video controls src="{rel}"></video>')
    #     elif lower.endswith(('.mp3','.m4a','.ogg','.wav','.opus')):
    #         html_parts.append(f'<audio controls><source src="{rel}" type="audio/mpeg">Your browser doesn’t support audio.</audio>')
    
    #     else:
    #         html_parts.append(f'<a href="{rel}">📎 Open file: {os.path.basename(rel)}</a>')
    if media_path:
        lower = media_path.lower()
        rel = media_path.replace('\\','/')

        # 🔊 NEW: Convert .opus to .mp3 automatically
        if lower.endswith(".opus"):
            media_path = convert_opus_to_mp3(media_path)
            rel = media_path.replace('\\','/')

        if lower.endswith(('.jpg','.jpeg','.png','.gif')):
            html_parts.append(f'<img src="{rel}" alt="image">')
        elif lower.endswith(('.mp4','.mov','.avi','.mkv')):
            html_parts.append(f'<video controls src="{rel}"></video>')
        elif lower.endswith(('.mp3','.m4a','.ogg','.wav','.opus')):
            html_parts.append(f'<audio controls><source src="{rel}" type="audio/mpeg">Your browser doesn’t support audio.</audio>')
        
        else:
            html_parts.append(f'<a href="{rel}">📎 Open file: {os.path.basename(rel)}</a>')

    safe = html.escape(text).replace('\n', '<br>')
    html_parts.append(f'<div>{safe}</div>')
    html_parts.append(f'<div class="meta">{dt}</div></div><div class="clear"></div>')

html_parts.append('</div></body></html>')

open(OUT_HTML, 'w', encoding='utf-8').write(''.join(html_parts))
print(f"\n✅ Chat clone created: {OUT_HTML}\nOpen it in your browser to view WhatsApp-style chat.")
print("If .opus files don’t play, you can convert them to .mp3 using ffmpeg if needed.")
