import os
import requests
import anthropic
from datetime import datetime, timedelta


EXTRACT_PROMPT = """\
以下は今週の国会議事録の発言テキストです。

この中から、以下のカテゴリに関連するキーワード・トピックTOP10を抽出してください。
対象カテゴリ：経済・財政・税・物価・金融・産業・貿易・雇用・社会保障・医療・年金・エネルギー・環境・安全保障・法案・規制・インフラ・農業・デジタル・AI

ルール：
- 「理事」「委員長」「異議なし」などの議事進行ワードは除外
- 具体的な政策名・法案名・社会問題名を優先
- 同じ概念の言い換えはまとめる（例：「物価高」「インフレ」→「物価・インフレ」）
- 出現頻度の多いものを優先

出力形式（JSON配列のみ、説明文なし）：
[
  {"word": "キーワード", "count": 出現回数の概算},
  ...
]

議事録テキスト：
{text}
"""


def fetch_weekly_keywords(top_n: int = 10) -> list[dict]:
    """先週1週間の国会会議録からClaudeで経済・政策関連キーワードTOP Nを返す"""
    end = datetime.today()
    start = end - timedelta(days=7)

    params = {
        "from": start.strftime("%Y-%m-%d"),
        "until": end.strftime("%Y-%m-%d"),
        "maximumRecords": 50,
        "recordPacking": "json",
    }

    resp = requests.get(
        "https://kokkai.ndl.go.jp/api/speech",
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    speeches = data.get("speechRecord", [])
    if not speeches:
        print("国会会議録: 発言データなし")
        return [{"word": "（今週の国会データなし）", "count": 0}]

    combined_text = "\n".join(
        s.get("speech", "")[:500]
        for s in speeches[:30]
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": EXTRACT_PROMPT.replace("{text}", combined_text),
        }],
    )

    import json
    raw = msg.content[0].text.strip()
    try:
        keywords = json.loads(raw)
        return keywords[:top_n]
    except Exception:
        start_idx = raw.find("[")
        end_idx = raw.rfind("]") + 1
        if start_idx != -1 and end_idx > start_idx:
            keywords = json.loads(raw[start_idx:end_idx])
            return keywords[:top_n]
        return [{"word": "キーワード抽出エラー", "count": 0}]
