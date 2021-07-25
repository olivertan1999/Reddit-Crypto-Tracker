# Reddit Crypto Tracker

<p><img align="center" src="https://user-images.githubusercontent.com/61670049/126875175-c2683a4a-bbcf-414c-9697-be38c576b55b.png" width="100%" height="50%" /></p>

# Introduction
With 3.3 mil members (as of now), [r/CryptoCurrency](https://coinmarketcap.com/all/views/all/) has certainly garnered the interest of many retail investors and crypto enthusiasts. As such, this is the perfect platform to gauge the sentiment of retail investors in the market as well as to get a first hand information on what's the next up and coming coin.

The aim of this project is to create a **web-based dashboard** that showcases the overall sentiment in the comment section of the subreddit's Daily Discussion post and updates its data automatically **every 10 minutes**. This project is built under the dash framework and its backend consists of scraping the comments data via reddit's api ([PRAW](https://praw.readthedocs.io/en/stable/)) as well as scraping cryptocurrencies' data in [coinmarketcap.com](https://coinmarketcap.com/all/views/all/) via conventional web-scraping method.

# General Ideas and Assumptions
The primary idea behind this project is to get to know what coins are reddit retail investors interested in currently and understand why the coins are so popular through their price changes and history.

In forum as casual as Reddit, there are bound to be irrelevant comments that should be filtered out from our analysis. To extract only the relevant comments, I assumed that **atleast one cryptocurrency (either symbol or fullname) is mentioned in the comment.**


# Demo
![demo](https://user-images.githubusercontent.com/61670049/126874984-b58b3aff-c429-471b-a3e9-ffc810da7273.gif)

Click [here]() for the full demonstration of the web-app.
