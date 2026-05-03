import requests
from collections import Counter
from datetime import datetime, timedelta


STOPWORDS = {
    "する", "ある", "いる", "こと", "ため", "もの", "これ", "それ",
    "おり", "また", "なり", "ない", "よう", "について", "における",
    "に関する", "として", "によって", "ところ", "という", "ただ",
    "委員", "大臣", "政府", "答弁", "質問", "議員", "会議",
}


def fetch_weekly_keywords(top_n: int = 10) -> list[dict]:
    """先週1週間の国会会議録から頻出キーワードTOP Nを返す"""
    end = datetime.today()
    start = end - timedelta(days=7)

    params = {
        "from": start.strftime("%Y-%m-%d"),
        "until": end.strftime("%Y-%m-%d"),
        "maximumRecords": 100,
        "recordPacking": "json",
    }

    resp = requests.get("https://kokkai.ndl.go.jp/api/speech", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    speeches = data.get("speechRecord", [])
    word_counter = Counter()

    for speech in speeches:
        text = speech.get("speech", "")
        for word in text.split():
            if len(word) >= 2 and word not in STOPWORDS:
                word_counter[word] += 1

    return [
        {"word": word, "count": count}
        for word, count in word_counter.most_common(top_n)
    ]
