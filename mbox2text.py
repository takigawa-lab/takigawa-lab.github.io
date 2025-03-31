mport os
import mailbox
import email
from pathlib import Path
import re

# 保存先ディレクトリ（適宜変更）
output_dir = Path("mbox_output")
output_dir.mkdir(exist_ok=True)

# 添付ファイルの保存先
attachments_dir = output_dir / "attachments"
attachments_dir.mkdir(exist_ok=True)

# mboxファイルを開く（適宜ファイル名を変更）
mbox = mailbox.mbox("example.mbox")

def sanitize_filename(name):
    """ファイル名に使えない文字を置換"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

for i, message in enumerate(mbox, 1):
    subject = message['subject'] or 'No_Subject'
    from_ = message['from'] or 'No_From'
    date = message['date'] or 'No_Date'
    filename = sanitize_filename(f"{i:08d}_{subject[:50]}.txt")

    # 本文抽出
    body = ""
    attachments = []
    
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # 添付ファイルの処理
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = sanitize_filename(filename)
                    file_path = attachments_dir / f"{i:08d}_{filename}"
                    with open(file_path, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    attachments.append(file_path.name)
            
            # プレーンテキストの本文
            elif content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or "utf-8"
                try:
                    body += part.get_payload(decode=True).decode(charset, errors="replace")
                except Exception:
                    body += "[デコード失敗]\n"
    else:
        charset = message.get_content_charset() or "utf-8"
        body = message.get_payload(decode=True).decode(charset, errors="replace")

    # メールテキストの保存
    output_path = output_dir / sanitize_filename(f"{i:08d}_{subject[:50]}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"From: {from_}\nSubject: {subject}\nDate: {date}\n")
        if attachments:
            f.write(f"Attachments: {', '.join(attachments)}\n")
        f.write("\n" + body)

print("✅ 変換完了：")
print(f"- メール本文：{output_dir.resolve()}")
print(f"- 添付ファイル：{attachments_dir.resolve()}")

