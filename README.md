[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
<br>

<p><img align="center" src="https://user-images.githubusercontent.com/61670049/126895402-6db628c1-17d9-4f8f-9fba-3c7473d1453b.png" width="100%" height="100%" /></p>


<p><img align="left" src="https://styles.redditmedia.com/t5_2wlj3/styles/communityIcon_7jxh2j4ouky41.png?width=256&s=59ea46d93492e9d0951b43d7c580f72982a86974" width="55px" height="55px"/></p>

# Reddit Crypto Tracker

## Introduction
With 3.3 mil members (as of now), [r/CryptoCurrency](https://coinmarketcap.com/all/views/all/) has certainly garnered the interest of many retail investors and crypto enthusiasts. As such, this is the perfect platform to gauge the sentiment of retail investors in the market as well as to get a first hand information on what's the next up and coming coin.

The aim of this project is to create a **web-based dashboard** that showcases the overall sentiment in the comment section of the subreddit's Daily Discussion post and updates its data automatically **every 10 minutes**. This project is built under the dash framework and its backend consists of scraping the comments data via reddit's api ([PRAW](https://praw.readthedocs.io/en/stable/)) as well as scraping cryptocurrencies' data in [coinmarketcap.com](https://coinmarketcap.com/all/views/all/) via conventional web-scraping method.

## General Idea and Assumption
The primary idea behind this project is to get to know what coins are reddit retail investors interested in currently and understand why the coins are so popular through their price changes and history.

In forum as casual as Reddit, there are bound to be irrelevant comments that should be filtered out from our analysis. To extract only the relevant comments, I assumed that ***atleast one cryptocurrency (either symbol or fullname) is mentioned in the comment.***


## Preview
![demo](https://user-images.githubusercontent.com/61670049/126874984-b58b3aff-c429-471b-a3e9-ffc810da7273.gif)

Click [here]() for the full demonstration of the web-app.

## Setup
1. Open up your terminal or command prompt and cd to the directory containing the reddit-crypto-tracker files.
2. Run the following command to install all required python packages (****):
    ```
    pip install -r requirements.txt
    ```
3. When done, run the following command:
    ```
    python app.py
    ```
4. Wait for the script to run. (initial run may take a while depending on comments limit that you set in redditscrape.py)
5. Click on the link to access the webapp on browser.

## Issues and Limitations
