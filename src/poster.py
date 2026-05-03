import os
import tweepy


def _client(api_key: str, api_secret: str, access_token: str, access_secret: str) -> tweepy.Client:
    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )


def post(draft: dict) -> dict[str, str]:
    """draft["ja"] と draft["en"] をそれぞれのアカウントに投稿する"""
    ja_client = _client(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"],
    )
    en_client = _client(
        os.environ["X_EN_API_KEY"], os.environ["X_EN_API_SECRET"],
        os.environ["X_EN_ACCESS_TOKEN"], os.environ["X_EN_ACCESS_SECRET"],
    )

    ja_resp = ja_client.create_tweet(text=draft["ja"])
    en_resp = en_client.create_tweet(text=draft["en"])

    return {
        "ja_tweet_id": ja_resp.data["id"],
        "en_tweet_id": en_resp.data["id"],
    }
