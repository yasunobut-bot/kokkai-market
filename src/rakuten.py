import os
import requests


MOCK_DATA = {
    "総合TOP10": [
        {"rank": 1, "name": "【データ取得中】楽天市場人気商品", "url": "https://www.rakuten.co.jp/", "price": 0},
        {"rank": 2, "name": "【データ取得中】楽天市場人気商品", "url": "https://www.rakuten.co.jp/", "price": 0},
        {"rank": 3, "name": "【データ取得中】楽天市場人気商品", "url": "https://www.rakuten.co.jp/", "price": 0},
    ]
}


def fetch_rankings(app_id: str | None = None) -> dict[str, list[dict]]:
    """楽天ランキングAPIから総合TOP10を取得する。失敗時はモックデータを返す"""
    app_id = app_id or os.environ.get("RAKUTEN_APP_ID", "")

    try:
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

        if not items:
            print("楽天API: レスポンスが空。モックデータを使用")
            return MOCK_DATA

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

    except Exception as e:
        print(f"楽天API取得エラー（モックデータで続行）: {e}")
        return MOCK_DATA
