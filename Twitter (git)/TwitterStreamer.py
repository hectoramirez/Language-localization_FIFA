from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
from StreamListener import SListener

consumer_key = " "
consumer_secret = " "

access_token = " "
access_token_secret = " "

# Consumer key authentication
auth = OAuthHandler(consumer_key, consumer_secret)

# Access key authentication
auth.set_access_token(access_token, access_token_secret)

# Set up the API with the authentication handler
api = API(auth)

# Set up words to track
keywords_to_track = ['#FIFA20', '#FIFA21', 'FIFA20', 'FIFA21',
                     'FIFA 20', 'FIFA 21', '#EASPORTSFIFA']

# Instantiate the SListener object
listen = SListener(api, num_tweets=50000)

# Instantiate the Stream object
stream = Stream(auth, listen)

# Begin collecting data
stream.filter(track=keywords_to_track)