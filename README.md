# Download Live Tweets

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

# Stream 1000 tweets (including retweets) about Python
words = ['python']
df = listen_for_words(auth, words, max_tweets=1000)  # pandas DataFrame
```
