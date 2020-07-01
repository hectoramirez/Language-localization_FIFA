import glob
import json
import pandas as pd
import country_converter as coco
from geopy.geocoders import Nominatim
from tqdm import tqdm
import spacy
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# +++++++++++++++++++++++++
#         Import          +
# +++++++++++++++++++++++++

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


# +++++++++++++++++++++++++
#    Processing JSON      +
# +++++++++++++++++++++++++

def flatten_tweets(tweets):
    """ Flattens out tweet dictionaries so relevant JSON is
        in a top-level dictionary. """

    tweets_list = []

    # Iterate through each tweet
    for tweet_obj in tweets:

        ''' User info'''
        # Store the user screen name in 'user-screen_name'
        tweet_obj['user-screen_name'] = tweet_obj['user']['screen_name']

        # Store the user location
        tweet_obj['user-location'] = tweet_obj['user']['location']

        ''' Text info'''
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

        ''' Place info'''
        if 'place' in tweet_obj:
            # Store the country code in 'place-country_code'
            try:
                tweet_obj['place-country'] = \
                    tweet_obj['place']['country']

                tweet_obj['place-country_code'] = \
                    tweet_obj['place']['country_code']

                tweet_obj['location-coordinates'] = \
                    tweet_obj['place']['bounding_box']['coordinates']
            except:
                pass

        tweets_list.append(tweet_obj)

    return tweets_list


def select_text(tweets):
    ''' Assigns the main text to only one column depending
        on whether the tweet is a RT/quote or not'''

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
columns = ['text', 'lang', 'user-location', 'place-country',
           'place-country_code', 'location-coordinates', 'user-screen_name']

# Create a DataFrame from `tweets`
df_tweets = pd.DataFrame(tweets, columns=columns)
# replaces NaNs by Nones
df_tweets.where(pd.notnull(df_tweets), None, inplace=True)

print('\n Processing JSON (process 1 of 5) finished! \n')

# ++++++++++++++++++++++++++++++++++++++++++
df_tweets_sample = df_tweets.copy()[:]  # ++
# ++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++
#       Languages         +
# +++++++++++++++++++++++++

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
    elif lang == 'iw':
        name = languages_dict['he']['name']
        names.append(name)
    else:
        name = languages_dict[lang]['name']
        names.append(name)

df_tweets_sample['language'] = names
df_tweets_sample.drop(['lang'], axis=1, inplace=True)

print('\n Languages (process 2 of 5) finished! \n')

# +++++++++++++++++++++++++
#       Locations         +
# +++++++++++++++++++++++++


# change codes to iso3
to_iso3_func = lambda x: coco.convert(names=x, to='iso3', not_found=None) \
    if x is not None else x

df_tweets_sample['place-country_code'] = \
    df_tweets_sample['place-country_code'].apply(to_iso3_func)

# change name to standard name
to_std_func = lambda x: coco.convert(names=x, to='name_short', not_found=None) \
    if x is not None else x

df_tweets_sample['place-country'] = \
                        df_tweets_sample['place-country_code'].apply(to_std_func)

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
df_tweets_sample['user-country_code'] = loc

# change codes to iso3
df_tweets_sample['user-country_code'] = \
    df_tweets_sample['user-country_code'].apply(to_iso3_func)

# create user-country column
df_tweets_sample['user-country'] = \
    df_tweets_sample['user-country_code'].apply(to_std_func)

# drop old column
df_tweets_sample.drop(['user-location'], axis=1, inplace=True)

countries, codes = [], []
for idx, row in df_tweets_sample.iterrows():
    if row['place-country_code'] is None:
        country = row['user-country']
        code = row['user-country_code']
        countries.append(country)
        codes.append(code)
    else:
        countries.append(row['place-country'])
        codes.append(row['place-country_code'])

df_tweets_sample['location'] = countries
df_tweets_sample['location_code'] = codes

# drop old columns
df_tweets_sample.drop(columns=['place-country', 'place-country_code',
                               'user-country', 'user-country_code'],
                      inplace=True)

print('\n Locations (process 3 of 5) finished! \n')

# +++++++++++++++++++++++++
#       Text cleaning     +
# +++++++++++++++++++++++++

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


df_tweets_sample['text_cleaned'] = \
    df_tweets_sample['text'].progress_apply(cleaner)

# select only not-null tweets not in English
mask1 = df_tweets_sample['text'].notnull()
mask2 = df_tweets_sample['language'] != 'English'
df_masked = df_tweets_sample[mask1 & mask2]

# split dataframe in x equal-size pieces
df_tweets_sample_splitted = np.array_split(df_masked, 150)


def tweet_translation(df, idx):
    """ Translate tweets using googletrans """

    from googletrans import Translator

    translator = Translator()

    try:
        # translate raw tweet
        trans = df['text'].apply(translator.translate, dest='en')
        # create column extracting the translated text
        df['text_english'] = trans.apply(lambda x: x.text)
        # append to empty list
        translations.append(df)
        # save data in case error happens
        df.to_csv('Twitter/Translations/translation_{}.csv'.format(idx))

    except Exception as e:
        print(e, ' -- at index ', idx)


translations = []
for idx, df in enumerate(tqdm(df_tweets_sample_splitted)):
    tqdm._instances.clear()
    tweet_translation(df, idx)

df_translations = pd.concat(translations)
df_english = df_tweets_sample.join(df_translations['text_english'])

# replaces NaNs by Nones
df_english.where(pd.notnull(df_english), None, inplace=True)

# add original English tweets to text_english by replacing Nones
texts = []
for idx, row in df_english.iterrows():
    if row['text_english'] is None:
        text = row['text']
        texts.append(text)
    else:
        texts.append(row['text_english'])

df_english['text_english'] = texts

print('\n Text cleaning (process 4 of 5) finished! \n')


# +++++++++++++++++++++++++
#       Sentiment         +
# +++++++++++++++++++++++++

df_sentiment = df_english.copy()

# instantiate new SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

sentiment_scores = df_sentiment['text_english'].progress_apply(
                                                            sid.polarity_scores)
sentiment = sentiment_scores.apply(lambda x: x['compound'])
df_sentiment['sentiment'] = sentiment

cols_order = ['text', 'language', 'location', 'location_code',
              'location-coordinates', 'sentiment', 'text_english',
              'text_cleaned', 'user-screen_name']
df_final = df_sentiment[cols_order]

df_final.to_csv('Twitter/Tweets_sentiment.csv')

print('\n Sentiment (process 5 of 5) finished! \n')

print(df_final.head())
