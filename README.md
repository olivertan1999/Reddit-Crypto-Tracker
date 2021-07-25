[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
<br>

<p><img align="center" src="https://user-images.githubusercontent.com/61670049/126895402-6db628c1-17d9-4f8f-9fba-3c7473d1453b.png" width="100%" height="100%" /></p>


<p><img align="left" src="https://styles.redditmedia.com/t5_2wlj3/styles/communityIcon_7jxh2j4ouky41.png?width=256&s=59ea46d93492e9d0951b43d7c580f72982a86974" width="55px" height="55px"/></p>

# Reddit Crypto Tracker

## Introduction
With 3.3 mil members as of now, [r/CryptoCurrency](https://coinmarketcap.com/all/views/all/) has certainly garnered the interest of many retail investors and crypto enthusiasts. As such, this is the perfect platform to gauge the sentiment of retail investors in the market as well as to get the first hand information on what's the next up and coming crypto coin.

The aim of this project is to create a **web-based dashboard** that showcases the overall sentiment in the comment section of the subreddit's Daily Discussion post and updates its data automatically **every 10 minutes**. This project is built under the dash framework and its backend consists of scraping the comments data via reddit's api ([PRAW](https://praw.readthedocs.io/en/stable/)) as well as scraping cryptocurrencies' data in [coinmarketcap.com](https://coinmarketcap.com/all/views/all/) via conventional web-scraping method.

## General Idea and Assumption
The primary idea behind this project is to get to know what coins are reddit retail investors interested in currently and understand why the coins are so popular through their price changes and history.

In forum as casual as Reddit, there are bound to be irrelevant comments that should be filtered out from our analysis. To extract only the relevant comments, I assumed that ***atleast one cryptocurrency (either coin code or full name) must be mentioned in the comment.***


## Preview
![demo](https://user-images.githubusercontent.com/61670049/126874984-b58b3aff-c429-471b-a3e9-ffc810da7273.gif)

Click [here](https://user-images.githubusercontent.com/61670049/126901716-fe7347ee-f435-448d-8a47-00c44e780dec.mp4) for the full demonstration of the web-app.

## Setup
1. Open up your terminal or command prompt and cd to the directory containing the reddit-crypto-tracker .py files.
2. Run the following command to install all required python packages (**May take a while to install**):
    ```
    pip install -r requirements.txt
    ```
3. When done, run the following command:
    ```
    python app.py
    ```
4. Wait for the script to run. (initial run may take a while (**up to 5 minutes**) depending on comments limit that you set in [redditscrape.py](https://github.com/olivertan1999/Reddit-Crypto-Tracker/blob/main/redditscrape.py))
5. Copy the link to access the webapp on browser.

## Issues and Limitations
1. Webapp might fail to run at **GMT+0 (around 10am AEST)** because that's the time when the Daily Discussion post resets, thus there wont be enough comments to analyse. The webapp will run optimally at night when there are thousands of comments and therefore larger sample size to accurately reflect the subreddit's sentiments.
2. Since there are crypto coins with common words as code name, (eg. HARMONY with ONE as its code name) this may sway the result of the analysis. As of now, 'ONE' has been removed from the search list to avoid this issue. However, there may be similar coins in the future.
3. Extracting comments via reddit's API may take a long time depending on the comments limit that you set in [redditscrape.py](https://github.com/olivertan1999/Reddit-Crypto-Tracker/blob/main/redditscrape.py)) (**up to 5 minutes especially at night time with limit set to 20**)
4. The weakness of VADER Sentiment Analysis lies on its inability to detect sarcasms in text, thus the sentiment analysis may not accurately reflect the comments' sentiments.
