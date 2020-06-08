"""Listen for tweets with specific keywords, and scrape 'em."""

import datetime
import os
import pathlib
import sys
import traceback
from typing import Iterable, List, Optional, Union

import pandas as pd
import tweepy


def listen_for_words(auth: tweepy.OAuthHandler,
                     words: Iterable[str],
                     save_dir: Union[str, pathlib.Path],
                     max_tweets: Optional[int] = None,
                     max_records_per_file: int = 100000,
                     ) -> List[str]:
    """Stream and save tweets containing certain keywords.

    Parameters
    ----------
    auth : tweepy.OAuthHandler
        An OAuth authentication handler for the Twitter API.

    words : iterable of str
        Iterable (e.g., list) of words to use as tweet keywords.

    save_dir : str or path-like
        Path to a directory where the tweet data will be saved. Saved tweets are
        stored as gzipped pickled pandas DataFrames.

    max_tweets : int, optional
        Maximum number of tweets to stream. If not provided, tweets will be
        streamed and saved to disk indefinitely (until either the Twitter API
        rejects or the disk is full). If this number is provided and the tqdm
        package is installed, a progress bar will be displayed while the tweets
        are streamed.

    max_records_per_file : int
        Maximum number of rows per saved DataFrame file.

    Returns
    -------
    list of str
        List of filenames where gzipped pickled pandas DataFrames were saved.
        Data can then be loaded with pandas.read_pickle().

    """
    listener = _TweetListener(save_dir=save_dir, max_tweets=max_tweets,
                              max_records_per_file=max_records_per_file)
    stream = tweepy.Stream(auth=auth, listener=listener)

    try:
        stream.filter(track=words)
    except:
        e_type, e, tb = sys.exc_info()
        print('Listening prematurely terminated by exception:', file=sys.stderr)
        print(f'{e_type.__name__}: {e}', file=sys.stderr)
        traceback.print_tb(tb, file=sys.stderr)

    return listener.files


class _TweetListener(tweepy.StreamListener):
    def __init__(self,
                 save_dir: Union[str, pathlib.Path],
                 max_tweets: Optional[int] = None,
                 max_records_per_file: int = 100000):
        super().__init__()

        self.max_tweets = max_tweets
        self.save_dir = save_dir
        self.max_records_per_file = max_records_per_file

        if max_tweets is not None:
            try:
                import tqdm
            except ModuleNotFoundError:
                self.progress_bar = None
            else:
                self.progress_bar = tqdm.tqdm(total=max_tweets)
        else:
            self.progress_bar = None

        self.tweets = []
        self.tweet_count = 0

        self.files = []

    @staticmethod
    def _get_tweet_text(status):
        tweet = getattr(status, 'retweeted_status', status)
        try:
            return tweet.extended_tweet['full_text']
        except AttributeError:
            return tweet.text

    def _save_tweets(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename = 'tweets_' + timestamp + '.pkl.gz'
        filename = os.path.join(self.save_dir, filename)
        self.df.to_pickle(filename)
        self.files.append(filename)
        self.tweets = []

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
        self.tweet_count += 1

        if len(self.tweets) >= self.max_records_per_file:
            self._save_tweets()

        if self.progress_bar is not None:
            self.progress_bar.update()

        if self.max_tweets is not None and self.tweet_count >= self.max_tweets:
            if self.tweets:
                self._save_tweets()

            if self.progress_bar is not None:
                self.progress_bar.close()

            return False

    @property
    def df(self) -> pd.DataFrame:
        try:
            return pd.DataFrame.from_records(self.tweets, index='id')
        except KeyError:
            return pd.DataFrame.from_records(self.tweets)
