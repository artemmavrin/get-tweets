"""Listen for tweets with specific keywords, and scrape 'em."""

from typing import Iterable

import pandas as pd
import tqdm
import tweepy


class TweetListener(tweepy.StreamListener):
    def __init__(self, max_tweets: int):
        super().__init__()
        self.tweets = []
        self.max_tweets = max_tweets
        self.progress_bar = tqdm.tqdm(total=self.max_tweets)

    @staticmethod
    def _get_tweet_text(status):
        tweet = getattr(status, 'retweeted_status', status)
        try:
            return tweet.extended_tweet['full_text']
        except AttributeError:
            return tweet.text

    def on_status(self, status):
        record = dict(
            id=status.id,
            username=status.user.screen_name,
            description=status.user.description,
            location=status.user.location,
            following=status.user.friends_count,
            followers=status.user.followers_count,
            total_tweets=status.user.statuses_count,
            user_created_timestamp=status.user.created_at,
            tweet_created_timestamp=status.created_at,
            retweet_count=status.retweet_count,
            hashtags=status.entities['hashtags'],
            is_retweet=hasattr(status, 'retweeted_status'),
            text=self._get_tweet_text(status),
        )
        self.tweets.append(record)

        self.progress_bar.update()
        if len(self.tweets) >= self.max_tweets:
            self.progress_bar.close()
            return False

    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame.from_records(self.tweets, index='id')


def listen_for_words(auth: tweepy.OAuthHandler, words: Iterable[str],
                     max_tweets: int = 1000) -> pd.DataFrame:
    listener = TweetListener(max_tweets=max_tweets)
    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.filter(track=words)
    return listener.df
