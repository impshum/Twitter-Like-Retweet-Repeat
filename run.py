import tweepy
import schedule
from time import sleep
from datetime import datetime as dt
from random import randint
import configparser


config = configparser.ConfigParser()
config.read('conf.ini')
consumer_key = config['LOGIN']['consumer_key']
consumer_secret = config['LOGIN']['consumer_secret']
access_key = config['LOGIN']['access_key']
access_secret = config['LOGIN']['access_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

query = config['SETTINGS']['query']
query = f'{query} -filter:retweets'
wake_hour = int(config['SETTINGS']['wake_hour'])
sleep_hour = int(config['SETTINGS']['sleep_hour'])
min_sleep = int(config['SETTINGS']['min_sleep'])
max_sleep = int(config['SETTINGS']['max_sleep'])
min_sleep_timer = int(config['SETTINGS']['min_sleep_timer'])
max_sleep_timer = int(config['SETTINGS']['max_sleep_timer'])
favorite = int(config['SETTINGS']['favorite'])
retweet = int(config['SETTINGS']['retweet'])


def liker():
    if dt.now().hour in range(wake_hour, sleep_hour):
        max_per_run = int(config['SETTINGS']['max_per_run'])
        try:
            for s in api.search(q=query, lang='en', result_type='recent'):
                if not s.retweeted and 'RT @' not in s.text:
                    id = s.id
                    username = s.user.screen_name
                    tweet = s.text.replace('\n', '')
                    link = f'https://twitter.com/{username}/status/{id}'
                    if retweet:
                        api.retweet(id)
                        print(f'Liking {link}')
                    if favorite:
                        sleep(randint(1, 3))
                        api.create_favorite(id)
                        print(f'Favoriting {link}')

                    max_per_run -= 1
                    if not max_per_run:
                        break
                    sleep(randint(min_sleep, max_sleep))
        except tweepy.TweepError as e:
            print(e)


def main():
    liker()
    schedule.every(min_sleep_timer).to(max_sleep_timer).minutes.do(liker)
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    main()
