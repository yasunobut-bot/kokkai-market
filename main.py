import json
import os
import smtplib
import subprocess
import sys
from datetime import datetime

print("=== VERSION CHECK ===")
try:
    result = subprocess.run(["git", "log", "--oneline", "-3"], capture_output=True, text=True)
    print(result.stdout)
    with open("src/rakuten.py") as f:
        print("rakuten.py line 31:", f.readlines()[30].rstrip())
except Exception as e:
    print(f"version check error: {e}")
print("=====================")
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
DRAFT_FILE = DATA_DIR / "draft.json"


def generate():
    """下書きを生成してメール通知する"""
    from src.kokkai import fetch_weekly_keywords
    from src.rakuten import fetch_rankings
    from src.composer import compose

    print("国会会議録を取得中...")
    keywords = fetch_weekly_keywords()

    print("楽天ランキングを取得中...")
    rakuten = fetch_rankings()

    print("投稿文を生成中...")
    posts = compose(keywords, rakuten)

    draft = {
        "generated_at": datetime.now().isoformat(),
        "keywords": keywords,
        "rakuten": rakuten,
        "ja": posts["ja"],
        "en": posts["en"],
    }

    DATA_DIR.mkdir(exist_ok=True)
    DRAFT_FILE.write_text(json.dumps(draft, ensure_ascii=False, indent=2))
    print(f"下書きを保存しました: {DRAFT_FILE}")

    _notify(draft)


def post():
    """draft.json の内容を投稿する"""
    from src.poster import post as do_post

    if not DRAFT_FILE.exists():
        print("draft.json が見つかりません。先に generate を実行してください。")
        sys.exit(1)

    draft = json.loads(DRAFT_FILE.read_text())

    print("--- 投稿内容（日本語）---")
    print(draft["ja"])
    print("\n--- 投稿内容（英語）---")
    print(draft["en"])

    result = do_post(draft)

    history_file = DATA_DIR / "history" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    history_file.parent.mkdir(exist_ok=True)
    history_file.write_text(json.dumps({**draft, **result}, ensure_ascii=False, indent=2))

    DRAFT_FILE.unlink()
    print(f"\n投稿完了: JA={result['ja_tweet_id']} EN={result['en_tweet_id']}")


def _notify(draft: dict):
    """生成した下書きをメールで通知する"""
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    notify_email = os.environ.get("NOTIFY_EMAIL")

    if not all([smtp_user, smtp_pass, notify_email]):
        print("メール設定がないため通知をスキップします")
        return

    body = f"""立法市場 週次レポート下書き

【日本語投稿】
{draft["ja"]}

【英語投稿】
{draft["en"]}

---
GitHubで「post」ワークフローを実行すると投稿されます。
修正する場合は data/draft.json を編集してから実行してください。
"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"【立法市場】週次レポート下書き {datetime.now().strftime('%Y/%m/%d')}"
    msg["From"] = smtp_user
    msg["To"] = notify_email

    with smtplib.SMTP(os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)

    print(f"メール通知送信完了: {notify_email}")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if command == "generate":
        generate()
    elif command == "post":
        post()
    else:
        print("使い方: python main.py [generate|post]")
        sys.exit(1)
