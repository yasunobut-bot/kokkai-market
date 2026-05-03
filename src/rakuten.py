import os
import requests


CATEGORIES = {
    "食品・飲料": "100227",
    "日用品・生活雑貨": "558885",
    "防災・安全用品": "215783",
    "家電": "100371",
    "本・雑誌・コミック": "200162",
}


def fetch_rankings(app_id: str | None = None) -> dict[str, list[dict]]:
    """楽天ランキングAPIからカテゴリ別TOP5を取得する"""
    app_id = app_id or os.environ["RAKUTEN_APP_ID"]
    result = {}

    for category_name, genre_id in CATEGORIES.items():
        params = {
            "applicationId": app_id,
            "genreId": genre_id,
            "hits": 5,
            "format": "json",
        }
        resp = requests.get(
            "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628",
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        items = resp.json().get("Items", [])
        result[category_name] = [
            {
                "rank": i + 1,
                "name": item["Item"]["itemName"],
                "url": item["Item"]["itemUrl"],
                "price": item["Item"]["itemPrice"],
            }
            for i, item in enumerate(items)
        ]

    return result
