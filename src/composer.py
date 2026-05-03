import os
import anthropic


PROMPT_JA = """\
以下のデータをもとに、Xへの投稿文（日本語）を作成してください。

## 今週の国会頻出ワードTOP3
{keywords}

## 楽天で注目されたカテゴリ・商品
{rakuten}

## 制約
- 280文字以内
- 絵文字を適度に使う
- 最後に #立法市場 #国会 #楽天 を付ける
- 「政治と買い物の意外な連動」が伝わるトーンで
- 事実に基づき、特定の政治的立場をとらない

投稿文のみ出力してください。"""

PROMPT_EN = """\
Based on the data below, write an X post in English.

## Top keywords in Japan's parliament this week
{keywords}

## Notable Rakuten product categories
{rakuten}

## Constraints
- Under 280 characters
- Use emojis naturally
- End with #LegislativeMarket #JapanesePolitics #Rakuten
- Tone: surprising, data-driven, culturally curious
- Factual only, no political bias

Output the post text only."""


def compose(keywords: list[dict], rakuten: dict) -> dict[str, str]:
    """国会データ＋楽天データからJA/EN投稿文を生成する"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    kw_text = "\n".join(f"{i+1}位「{k['word']}」({k['count']}回)" for i, k in enumerate(keywords[:3]))
    rakuten_text = "\n".join(
        f"【{cat}】" + "、".join(items[0]["name"][:20] for items in [v] for _ in [None] if v)
        for cat, v in list(rakuten.items())[:3]
        if v
    )

    def generate(prompt: str) -> str:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    return {
        "ja": generate(PROMPT_JA.format(keywords=kw_text, rakuten=rakuten_text)),
        "en": generate(PROMPT_EN.format(keywords=kw_text, rakuten=rakuten_text)),
    }
