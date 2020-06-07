# Download Live Tweets

## Requirements

* Python 3 (tested with Python 3.8+)
* [pandas](https://pandas.pydata.org/)
* [Tweepy](https://www.tweepy.org/)
* [tqdm](https://tqdm.github.io/) (Optional, for displaying a progress bar)
* [S3Fs](https://s3fs.readthedocs.io/en/latest/) (Optional, needed if saving to S3)

## Usage

```python
import tweepy

from get_tweets import listen_for_words

# Set your Twitter developer account secrets
CONSUMER_KEY = '################'
CONSUMER_SECRET = '################'
ACCESS_TOKEN = '################'
ACCESS_TOKEN_SECRET = '################'

# Set up authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Stream 1,000,000 tweets about Python and save them to the data directory
words = ['python']
save_dir = 'data'
files = listen_for_words(auth, words, save_dir, max_tweets=1000000)
# `files` is a list of file names where the tweet data are saved, as gzipped
# pickled pandas DataFrames
```
