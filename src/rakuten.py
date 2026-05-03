import os
import requests


def fetch_rankings(app_id: str | None = None) -> dict[str, list[dict]]:
    """楽天ランキングAPIから総合TOP10を取得する"""
    app_id = app_id or os.environ["RAKUTEN_APP_ID"]

    params = {
        "applicationId": app_id,
        "hits": 10,
        "format": "json",
    }
    resp = requests.get(
        "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628",
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    items = resp.json().get("Items", [])

    return {
        "総合TOP10": [
            {
                "rank": i + 1,
                "name": item["Item"]["itemName"],
                "url": item["Item"]["itemUrl"],
                "price": item["Item"]["itemPrice"],
            }
            for i, item in enumerate(items)
        ]
    }
