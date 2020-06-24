import glob
import json
import pandas as pd
import country_converter as coco
from geopy.geocoders import Nominatim
from tqdm import tqdm
import spacy
from googletrans import Translator
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# list all files containing tweets
files = list(glob.iglob('Twitter/Tweets/*.json'))

tweets_data = []
for file in files:

    tweets_file = open(file, "r", encoding='utf-8')

    # Read in tweets and store in list: tweets_data
    for line in tweets_file:
        tweet = json.loads(line)
        tweets_data.append(tweet)

    tweets_file.close()

print('\n There are', len(tweets_data), 'tweets in the dataset. \n')


# Processing JSON

def flatten_tweets(tweets):
    """ Flattens out tweet dictionaries so relevant JSON is
        in a top-level dictionary. """

    tweets_list = []

    # Iterate through each tweet
    for tweet_obj in tweets:

        # Store the user screen name in 'user-screen_name'
        tweet_obj['user-screen_name'] = tweet_obj['user']['screen_name']

        # Store the user location
        tweet_obj['user-location'] = tweet_obj['user']['location']

        # Check if this is a 140+ character tweet
        if 'extended_tweet' in tweet_obj:
            # Store the extended tweet text in 'extended_tweet-full_text'
            tweet_obj['extended_tweet-full_text'] = \
                tweet_obj['extended_tweet']['full_text']

        if 'retweeted_status' in tweet_obj:
            # Store the retweet user screen name in
            # 'retweeted_status-user-screen_name'
            tweet_obj['retweeted_status-user-screen_name'] = \
                tweet_obj['retweeted_status']['user']['screen_name']

            # Store the retweet text in 'retweeted_status-text'
            tweet_obj['retweeted_status-text'] = \
                tweet_obj['retweeted_status']['text']

            if 'extended_tweet' in tweet_obj['retweeted_status']:
                # Store the extended retweet text in
                # 'retweeted_status-extended_tweet-full_text'
                tweet_obj['retweeted_status-extended_tweet-full_text'] = \
                    tweet_obj['retweeted_status']['extended_tweet']['full_text']

        if 'quoted_status' in tweet_obj:
            # Store the retweet user screen name in
            # 'retweeted_status-user-screen_name'
            tweet_obj['quoted_status-user-screen_name'] = \
                tweet_obj['quoted_status']['user']['screen_name']

            # Store the retweet text in 'retweeted_status-text'
            tweet_obj['quoted_status-text'] = \
                tweet_obj['quoted_status']['text']

            if 'extended_tweet' in tweet_obj['quoted_status']:
                # Store the extended retweet text in
                # 'retweeted_status-extended_tweet-full_text'
                tweet_obj['quoted_status-extended_tweet-full_text'] = \
                    tweet_obj['quoted_status']['extended_tweet']['full_text']

        if 'place' in tweet_obj:
            # Store the country code in 'place-country_code'
            try:
                tweet_obj['place-country_code'] = \
                    tweet_obj['place']['country_code']
            except:
                pass

        tweets_list.append(tweet_obj)

    return tweets_list


def select_text(tweets_frame):
    """ Assigns the main text to only one column depending
        on whether the tweet is a RT/quote or not"""

    tweets_list = []

    # Iterate through each tweet
    for tweet_obj in tweets:

        if 'retweeted_status-extended_tweet-full_text' in tweet_obj:
            tweet_obj['text'] = \
                tweet_obj['retweeted_status-extended_tweet-full_text']

        elif 'retweeted_status-text' in tweet_obj:
            tweet_obj['text'] = tweet_obj['retweeted_status-text']

        elif 'extended_tweet-full_text' in tweet_obj:
            tweet_obj['text'] = tweet_obj['extended_tweet-full_text']

        tweets_list.append(tweet_obj)

    return tweets_list


# flatten tweets
tweets = flatten_tweets(tweets_data)
columns_all_text = ['text', 'extended_tweet-full_text', 'retweeted_status-text',
                    'retweeted_status-extended_tweet-full_text', 'quoted_status-text',
                    'quoted_status-extended_tweet-full_text', 'lang', 'user-location',
                    'place-country_code']

# select text
tweets = select_text(tweets)
columns = ['text', 'lang', 'user-location', 'place-country_code']

# Create a DataFrame from `tweets`
df_tweets = pd.DataFrame(tweets, columns=columns)
# replaces NaNs by Nones
df_tweets.where(pd.notnull(df_tweets), None, inplace=True)

# ++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++
df_tweets_sample = df_tweets.copy()[:]  # ++++
# ++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++

# Languages

with open('Countries/languages.json', 'r', encoding='utf-8') as json_file:
    languages_dict = json.load(json_file)

names = []
for idx, row in df_tweets_sample.iterrows():
    lang = row['lang']
    if lang == 'und':
        names.append(None)
    elif lang == 'in':
        name = languages_dict['id']['name']
        names.append(name)
    elif lang=='iw':
        name = languages_dict['he']['name']
        names.append(name)
    else:
        name = languages_dict[lang]['name']
        names.append(name)

df_tweets_sample['language'] = names
df_tweets_sample.drop(['lang'], axis=1, inplace=True)

print('\n Process 1 of 5 finished! \n')


# Locations

# place-country_code

# change codes to iso3
to_iso3_func = lambda x: coco.convert(names=x, to='iso3', not_found=None) \
    if x is not None else x

df_tweets_sample['place-country_code'] = \
    df_tweets_sample['place-country_code'].apply(to_iso3_func)

# user-locations

tqdm.pandas()


def geo_locator(user_location):
    # initialize geolocator
    geolocator = Nominatim(user_agent='Tweet_locator')

    if user_location is not None:
        try:
            # get location
            location = geolocator.geocode(user_location, language='en')
            # get coordinates
            location_exact = geolocator.reverse(
                [location.latitude, location.longitude], language='en')
            # get country codes
            c_code = location_exact.raw['address']['country_code']

            return c_code

        except:
            return None

    else:
        return None


# apply geo locator to user-location
loc = df_tweets_sample['user-location'].progress_apply(geo_locator)
df_tweets_sample['user_location'] = loc

# change codes to iso3
df_tweets_sample['user_location'] = \
    df_tweets_sample['user_location'].apply(to_iso3_func)

# drop old column
df_tweets_sample.drop(['user-location'], axis=1, inplace=True)

print('\n Process 2 of 5 finished! \n')

codes = []
for idx, row in df_tweets_sample.iterrows():
    if row['place-country_code'] is None:
        code = row['user_location']
        codes.append(code)
    else:
        codes.append(row['place-country_code'])

df_tweets_sample['location'] = codes
df_tweets_sample.drop(columns=['place-country_code', 'user_location'],
                      inplace=True)

# Sentiment

nlp = spacy.load('en_core_web_sm')


def cleaner(string):
    # Generate list of tokens
    doc = nlp(string)
    lemmas = [token.lemma_ for token in doc]
    # Remove tokens that are not alphabetic
    a_lemmas = [lemma for lemma in lemmas
                if lemma.isalpha() or lemma == '-PRON-']
    # Print string after text cleaning
    return ' '.join(a_lemmas)


df_tweets_sample['text-cleaned'] = \
    df_tweets_sample['text'].progress_apply(cleaner)

print('\n Process 3 of 5 finished! \n')

translator = Translator()

trans = df_tweets_sample['text-cleaned'].progress_apply(
    translator.translate, dest='en')
df_tweets_sample['text_english'] = trans.apply(lambda x: x.text)

print('\n Process 4 of 5 finished! \n')

# instantiate new SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

sentiment_scores = df_tweets_sample['text_english'].progress_apply(
    sid.polarity_scores)
sentiment = sentiment_scores.apply(lambda x: x['compound'])
df_tweets_sample['sentiment'] = sentiment

df_tweets_sample.drop(columns=['text-cleaned'], axis=1, inplace=True)

print('\n Process 5 of 5 finished! \n')

#
cols_order = ['text', 'text_english', 'sentiment', 'language', 'location']
df_tweets_sample = df_tweets_sample[cols_order]

df_tweets_sample.to_csv('Twitter/Tweets_cleaned_full.csv')

print('\n Process completely finished!')
