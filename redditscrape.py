import praw
import pandas as pd
import numpy as np
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import json
from bs4 import BeautifulSoup


class RedditScrape:
    def __init__(self):
        self.post = {
            'title': [],
            'score': [],
            'id': [],
            'url': [],
            'num_comments': [],
            'body': [],
            'created': []
        }

        self.daily_comments = {
            'top_comments': [],
            'karma': [],
            'coins_mentioned': [],
            'sentiment': []
        }

        self.comments_sentiment = {
            'Positive': 0,
            'Neutral': 0,
            'Negative': 0
        }

        self.crypto_data = {
            'coin': [],
            'coin_code': [],
            'price_in_usd': [],
            'percent_change_1h': [],
            'percent_change_24h': [],
            'percent_change_7d': []
        }

        self.crypto_df = None
        self.comments_df = None

    def remove_gif_url(self, comment):
        # Remove GIF
        clean_comment = re.sub(r'!\[gif\]\(giphy\|.*\)', '', comment)

        return clean_comment

    def find_coins(self, text, crypto_data, coins_code, coins_name):
        accept = self.crypto_data['coin_code'] + self.crypto_data['coin']

        coins = [coin for coin in accept if coin.upper() in text.upper()]

        coins_mentioned = []
        for coin in coins:
            try:
                coins_mentioned.append(coins_code[coin])
            except KeyError:
                coins_mentioned.append(coins_name[coin])

        if coins_mentioned:
            return ", ".join(set(coins_mentioned))
        else:
            return np.nan

    def sentiment_analysis(self, comment, sentiment, comment_sentiment, threshold):
        if sentiment['compound'] > threshold:
            comment_sentiment['Positive'] += 1
            return 'Positive'

        elif sentiment['compound'] < -1 * threshold:
            comment_sentiment['Negative'] += 1
            return 'Negative'

        else:
            comment_sentiment['Neutral'] += 1
            return 'Neutral'

        return sentiment

    def get_market_data(self):
        print("Reading Market Data...")

        start_urls = 'https://coinmarketcap.com/all/views/all/'
        web_content = requests.get(start_urls)
        soup = BeautifulSoup(web_content.content, "lxml")
        json_data = json.loads(soup.select("[type='application/json']")[0].getText())

        lenCrypto = len(json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'])

        for i in range(lenCrypto):
            coin_name = json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['name']
            self.crypto_data['coin'].append(coin_name.upper())
            self.crypto_data['coin_code'].append(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['symbol'].upper())
            self.crypto_data['price_in_usd'].append(
                round(json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                          'price'],
                      2))
            self.crypto_data['percent_change_1h'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange1h'], 2))
            self.crypto_data['percent_change_24h'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange24h'], 2))
            self.crypto_data['percent_change_7d'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange7d'], 2))

        self.crypto_df = pd.DataFrame(self.crypto_data)

    def reset_data(self):
        self.crypto_data = {
            'coin': [],
            'coin_code': [],
            'price_in_usd': [],
            'percent_change_1h': [],
            'percent_change_24h': [],
            'percent_change_7d': []
        }

        self.daily_comments = {
            'top_comments': [],
            'karma': [],
            'coins_mentioned': [],
            'sentiment': []
        }

    def get_data(self):
        print("Getting Reddit's comments...")

        reddit = praw.Reddit(client_id='LgU5h51QX43Iqg', client_secret='vAJDrWv61bRlXDeSHqIvpAi_ZykAbA',
                             user_agent='Crypto Webscrape')

        hot_posts = reddit.subreddit('CryptoCurrency').hot(limit=5)

        for post in hot_posts:
            self.post['title'].append(post.title)
            self.post['id'].append(post.id)

        for index, title in enumerate(self.post['title']):
            if re.findall(r'Daily Discussion', title):
                found = self.post['id'][index]

        submission = reddit.submission(id=found)

        sia = SentimentIntensityAnalyzer()

        self.reset_data()
        self.get_market_data()

        coins_code = {row['coin_code']: row['coin'] for index, row in self.crypto_df.iterrows()}
        coins_name = {row['coin']: row['coin'] for index, row in self.crypto_df.iterrows()}

        submission.comments.replace_more(limit=1)
        for top_level_comment in submission.comments[1:]:
            comment = top_level_comment.body
            comment = self.remove_gif_url(comment)
            sentiment = sia.polarity_scores(comment)

            self.daily_comments['top_comments'].append(comment)
            self.daily_comments['sentiment'].append(
                self.sentiment_analysis(comment, sentiment, self.comments_sentiment, 0.03))
            self.daily_comments['karma'].append(top_level_comment.score)
            self.daily_comments['coins_mentioned'].append(
                self.find_coins(comment, self.crypto_df, coins_code, coins_name))

        self.comments_df = pd.DataFrame(self.daily_comments)

        return f"Collected {len(self.comments_df)} comments."