import praw
import pandas as pd
import numpy as np
import re
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import json
from bs4 import BeautifulSoup


class RedditScrape:
    """ Reddit Scraping class for scraping and summarizing comments from the Daily Discussion
        post in r/CryptoCurrency."""

    def __init__(self):

        """ Attributes:
                post (dict) - list of reddit posts in r/CryptoCurrency
                daily_comments (dict) - list of comments scraped from the Daily Discussion post
                comments_sentiment (dict) - comment count in each sentiment group
                crypto_data (dict) - list of cryptos data scraped from coinmarketcap.com
                crypto_df (dataframe) - crypto_data in dataframe form
                comments_df (dataframe) - daily_comments in dataframe form
        """

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
            'Top Comments': [],
            'Karma': [],
            'coins_mentioned': [],
            'sentiment': []
        }

        self.comments_sentiment = {
            'Positive': 0,
            'Neutral': 0,
            'Negative': 0
        }

        self.crypto_data = {
            'Coin': [],
            'Coin Code': [],
            'Price in USD ($)': [],
            '1h Change (%)': [],
            '24h Change (%)': [],
            '7d Change (%)': []
        }

        self.crypto_df = None
        self.comments_df = None

    def remove_gif_url(self, comment):

        """ Function to remove gif from comment.

            Args:
                comment (string): original comment in text form
            Returns:
                string: comment without the gif codes
        """

        clean_comment = re.sub(r'!\[gif\]\(giphy\|.*\)', '', comment)

        return clean_comment

    def find_coins(self, text, coins_code, coins_name):

        """ Function to find and extract cryptos name or symbol from the comment text.

            Args:
                text (string): comment text
                coins_code (dict): maps coins symbol to its name. eg BTC -> BITCOIN
                coins_name (dict): maps coins name to its name. eg BITCOIN -> BITCOIN
            Returns:
                string: list of crypto names separated by commas
        """

        # list of strings to be searched and matched as coin (eg. BITCOIN, BTC, ...)
        accept = self.crypto_data['Coin Code'] + self.crypto_data['Coin']
        # Remove 'ONE' from the accept list as it is an extremely common word
        accept.remove('ONE')

        text = re.split(r'\W+', text.upper())

        # Find all coins mentioned in the comment text
        coins = [coin for coin in accept if coin.upper() in text]
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

    def sentiment_analysis(self, sentiment, threshold):

        """ Function to assign comment's sentiment based on their VADER compound score.

            Args:
                sentiment (dict): list the score for each sentiment in the comment
                threshold (float): threshold to determine the comment's sentiment
            Returns:
                string: overall comment's sentiment
        """

        if sentiment['compound'] > threshold:
            self.comments_sentiment['Positive'] += 1
            return 'Positive'

        elif sentiment['compound'] < -1 * threshold:
            self.comments_sentiment['Negative'] += 1
            return 'Negative'

        else:
            self.comments_sentiment['Neutral'] += 1
            return 'Neutral'

    def get_market_data(self):

        """ Function to scrape cryptos data from coinmarketcap.com.

            Args:
                None
            Returns:
                None
        """

        print("Reading Market Data...")

        start_urls = 'https://coinmarketcap.com/all/views/all/'
        web_content = requests.get(start_urls)
        soup = BeautifulSoup(web_content.content, "html5lib")

        # Load the json data from the web html
        json_data = json.loads(soup.select("[type='application/json']")[0].getText())

        len_crypto = len(json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'])

        # Extract cryptos infos from the json data
        for i in range(len_crypto):
            coin_name = json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['name']
            self.crypto_data['Coin'].append(coin_name.upper())
            self.crypto_data['Coin Code'].append(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['symbol'].upper())
            self.crypto_data['Price in USD ($)'].append(
                round(json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                          'price'],
                      2))
            self.crypto_data['1h Change (%)'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange1h'], 2))
            self.crypto_data['24h Change (%)'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange24h'], 2))
            self.crypto_data['7d Change (%)'].append(round(
                json_data['props']['initialState']['cryptocurrency']['listingLatest']['data'][i]['quotes'][0][
                    'percentChange7d'], 2))

        self.crypto_df = pd.DataFrame(self.crypto_data)

    def reset_data(self):

        """ Function to reset the crypto_data and daily_comments attributes in the RedditScrape class.

            Args:
                None
            Returns:
                None
        """

        self.crypto_data = {
            'Coin': [],
            'Coin Code': [],
            'Price in USD ($)': [],
            '1h Change (%)': [],
            '24h Change (%)': [],
            '7d Change (%)': []
        }

        self.daily_comments = {
            'Top Comments': [],
            'Karma': [],
            'coins_mentioned': [],
            'sentiment': []
        }

    def get_data(self):

        """ Function to scrape reddit's comment via praw api.

            Args:
                None
            Returns:
                None
        """

        print("Getting Reddit's comments...")

        reddit = praw.Reddit(client_id='LgU5h51QX43Iqg', client_secret='vAJDrWv61bRlXDeSHqIvpAi_ZykAbA',
                             user_agent='Crypto Webscrape')

        # Search for the Daily Discussion post id
        hot_posts = reddit.subreddit('CryptoCurrency').hot(limit=5)

        for post in hot_posts:
            self.post['title'].append(post.title)
            self.post['id'].append(post.id)

        for index, title in enumerate(self.post['title']):
            if re.findall(r'Daily Discussion', title):
                found = self.post['id'][index]

        # Get the daily discussion post's data
        submission = reddit.submission(id=found)

        sia = SentimentIntensityAnalyzer()

        self.reset_data()
        self.get_market_data()

        coins_code = {row['Coin Code']: row['Coin'] for index, row in self.crypto_df.iterrows()}
        coins_name = {row['Coin']: row['Coin'] for index, row in self.crypto_df.iterrows()}

        # Extract and process each comments in the post
        # Change the limit (1-20) to adjust the number of comments to be collected
        # This will drastically affect the runtime as well
        submission.comments.replace_more(limit=20)

        # Skip the first mod comment
        for top_level_comment in submission.comments[1:]:
            comment = top_level_comment.body
            comment = self.remove_gif_url(comment)
            sentiment = sia.polarity_scores(comment)

            # Discard comments where no coin is mentioned
            if pd.isna(self.find_coins(comment, coins_code, coins_name)):
                continue

            self.daily_comments['Top Comments'].append(comment)
            self.daily_comments['sentiment'].append(
                self.sentiment_analysis(sentiment, 0.03))
            self.daily_comments['Karma'].append(top_level_comment.score)
            self.daily_comments['coins_mentioned'].append(
                self.find_coins(comment, coins_code, coins_name))

        self.comments_df = pd.DataFrame(self.daily_comments)

        print(f"Collected {len(self.comments_df)} comments.")

    def count_coins_mentioned(self):

        """ Function to count the number of times a crypto is mentioned from the collected comments.

            Args:
                None
            Returns:
                Dataframe: table detailing the cryptos info of the most to least mentioned coins
        """

        coins_count = {coin: 0 for coin in self.crypto_df['Coin']}

        for index, row in self.comments_df.iterrows():
            if not pd.isna(row['coins_mentioned']):
                coins = row['coins_mentioned'].split(", ")
                for coin in coins:
                    coins_count[coin] += 1

        final_coins_count = {coin: value for coin, value in
                             sorted(coins_count.items(), key=lambda item: item[1], reverse=True) if value != 0}

        # Rearrange crypto_df based on mention counts
        coin_data = pd.DataFrame()
        for coin in list(final_coins_count.keys()):
            coin_data = pd.concat([coin_data, self.crypto_df[self.crypto_df['Coin'] == coin]])

        coin_data['Mention Counts'] = coin_data['Coin'].map(final_coins_count)

        return coin_data
