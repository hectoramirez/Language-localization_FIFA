from tweepy.streaming import StreamListener
import json
import time
import sys


class SListener(StreamListener):
    def __init__(self, api=None, fprefix='tweets', num_tweets=1000):
        self.api = api
        self.counter = 0
        self.fprefix = fprefix
        self.num_tweets = num_tweets
        self.output = open('%s_%s.json' % (self.fprefix, time.strftime('%Y%m%d-%H%M%S')), 'w')

    '''
    ### Already in StreamListener ###
    
    def on_data(self, data):
        if 'in_reply_to_status' in data:
            self.on_status(data)
        elif 'delete' in data:
            delete = json.loads(data)['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False
        elif 'limit' in data:
            if self.on_limit(json.loads(data)['limit']['track']) is False:
                return False
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print("WARNING: %s" % warning['message'])
            return
    '''

    '''def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        if self.counter >= 100:
            self.output.close()
            self.output = open('%s_%s.json' % (self.fprefix, time.strftime('%Y%m%d-%H%M%S')), 'w')
            self.counter = 0
        return'''

    def on_status(self, status):
        tweet = status._json
        self.output.write(json.dumps(tweet) + '\n')
        self.counter += 1
        if self.counter < self.num_tweets:
            return True
        else:
            self.output.close()
            return False
        self.output.close()

    def on_delete(self, status_id, user_id):
        print("Delete notice")
        return

    def on_limit(self, track):
        print("WARNING: Limitation notice received, tweets missed: %d" % track)
        return

    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return

    def on_timeout(self):
        print("Timeout, sleeping for 60 seconds...")
        time.sleep(60)
        return
