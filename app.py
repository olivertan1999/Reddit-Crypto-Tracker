import os.path
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_table
from dash_extensions import Lottie
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import yfinance as yf
from redditscrape import RedditScrape
import time
import requests
from bs4 import BeautifulSoup


def get_img(coin):

    """ Function to get coin's logo image url.

        Args:
            coin_code (string): eg. BTC for Bitcoin
        Returns:
            string: coin's image url
    """

    # Find image url from the previously scraped logo data
    img_src = crypto_logo[crypto_logo['coin'] == coin]['coin_img']

    try:
        return img_src.values[0]

    except IndexError:
        # If img url is missing, scrape it from coinmarketcap.com
        coin_code = rs.crypto_df[rs.crypto_df['Coin'] == coin]['Coin Code'].values[0]

        URL = f"https://coinmarketcap.com/currencies/{coin.lower().replace(' ', '-')}/"
        r = requests.get(URL)

        soup = BeautifulSoup(r.content, 'html5lib')
        elements = soup.find('img', attrs={'alt': f"{coin_code.upper()}"})

        return elements['src']
    

def top_10_coins_logo(top_coins):

    """ Function to get top 10 coins' logo image urls.

        Args:
            top_coins (DataFrame): table detailing all cryptos infos from most to least mentioned in the comments
        Returns:
            list: list of image urls for the top 10 coins mentioned
    """

    coins_rank = {f'rank-{n+1}-coin': top_coins.iloc[n]['Coin'] for n in range(10)}

    rank_1 = get_img(coins_rank["rank-1-coin"])
    rank_2 = get_img(coins_rank["rank-2-coin"])
    rank_3 = get_img(coins_rank["rank-3-coin"])
    rank_4 = get_img(coins_rank["rank-4-coin"])
    rank_5 = get_img(coins_rank["rank-5-coin"])
    rank_6 = get_img(coins_rank["rank-6-coin"])
    rank_7 = get_img(coins_rank["rank-7-coin"])
    rank_8 = get_img(coins_rank["rank-8-coin"])
    rank_9 = get_img(coins_rank["rank-9-coin"])
    rank_10 = get_img(coins_rank["rank-10-coin"])

    return rank_1, rank_2, rank_3, rank_4, rank_5, rank_6, rank_7,\
        rank_8, rank_9, rank_10


def get_candlestick(coin):

    """ Function to plot the candlestick chart of the coin.

        Args:
            coin (string): Full name of the coin. eg BITCOIN
        Returns:
            Figure: 6 days Candlestick chart with 1 hour interval
    """

    try:
        ticker = yf_crypto[yf_crypto['Name Only'] == coin.replace(" ", "")]['Symbol'].values[0]
    except IndexError:
        ticker = np.nan

    # Get tickers data
    data = yf.download(tickers=ticker,
                       period='6d',
                       interval='60m').reset_index()

    # Convert the timezone in the yf data to asia/malaysia's timezone
    data['Datetime'] = data['Datetime'].dt.tz_convert('Asia/Kuala_Lumpur')

    # declare figure
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=data['Datetime'],
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='market data',
                                 opacity=1))

    # Add titles
    fig.update_layout(
        yaxis_title=f'{coin} Price (US Dollars)',
    )

    # Update x,y-axes
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=3, label="3d", step="day", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig.update_yaxes(showline=False, linewidth=1, gridcolor='rgb(232,232,232)')

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0),
                      paper_bgcolor="rgb(255,255,255)",
                      plot_bgcolor="rgb(255,255,255)",
                      font_family='"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
                      font_size=11,
                      hoverlabel_bgcolor='rgb(244, 244, 244)',
                      hoverlabel_font_color='rgb(0,0,0)',
                      hoverlabel_bordercolor='rgb(211,211,211)')

    return fig


curr_path = os.path.dirname(os.path.realpath(__file__))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server

# Animated icon url
url_cryptoicon = "https://assets3.lottiefiles.com/datafiles/b0TVxlf8FZxor5v/data.json"

custom_css = "assets/custom.css"

curr_datetime = datetime.datetime.now()

# Declare class and get reddit and crypto data
start = time.time()
rs = RedditScrape()
rs.get_data()
end = time.time()
print("Time taken to collect data: ", end-start, 's')

crypto_data = rs.crypto_df
reddit_data = rs.comments_df

# Data mapping coin to its respective tickers in yahoo finance
yf_crypto = pd.read_csv(f"{curr_path}/crypto_data/yf_crypto.csv")

# Data containing coin's logo urls
crypto_logo = pd.read_csv(f"{curr_path}/crypto_data/crypto_logo.csv")

# crypto_data arranged from most to least mentioned in the comments
top_coin = rs.count_coins_mentioned()

# dict with elements for the dropdown menu
dropdown_items = [{'label': row['Coin'], 'value': row['Coin']} for _, row in top_coin.iterrows()]

# Top 10 cryptos' logo image urls
curr_top_coins = top_10_coins_logo(top_coin)

# MOST MENTIONED COIN BAR CHART
most_mentioned_bar = px.bar(top_coin[:10], x='Coin Code', y='Mention Counts', height=220)
most_mentioned_bar.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0),
                                 paper_bgcolor="rgb(255,255,255)",
                                 plot_bgcolor="rgb(255,255,255)",
                                 font_family='"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
                                 hoverlabel_bgcolor='rgb(244, 244, 244)',
                                 hoverlabel_font_color='rgb(0,0,0)',
                                 hoverlabel_bordercolor='rgb(211,211,211)')

most_mentioned_bar.update_traces(marker_color='rgb(162,160,165)')

# MARKET SENTIMENT GRAPH
piedata = reddit_data.groupby('sentiment').count()['Top Comments'].reset_index().rename({'Top Comments': 'Comments Count', 'sentiment': 'Sentiment'}, axis=1)
sentiment_pie_chart = px.pie(piedata,
                             values='Comments Count',
                             names='Sentiment',
                             color='Sentiment',
                             color_discrete_map={
                                 'Positive': 'rgb(232,232,232)',
                                 'Neutral': 'rgb(211,211,211)',
                                 'Negative': '(rgb(191,191,191))',
                             },
                             height=286)

sentiment_pie_chart.update_traces(textposition='inside', textinfo='percent+label')

sentiment_pie_chart.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0),
                                  font_family='"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
                                  font_size=15,
                                  hoverlabel_bgcolor='rgb(244, 244, 244)',
                                  hoverlabel_font_color='rgb(0,0,0)',
                                  hoverlabel_bordercolor='rgba(0,0,0,0)')

# Config for Lottie
option = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(Lottie(options=option, width="100px", height="72px", url=url_cryptoicon))
                ], className='mb-n2 d-none d-md-block', style={'height': '14vh', 'border': 'none'}, outline=False)
            ], width=2, md=2, lg=2, sm=2, xs=0),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1(id='title',
                                children=f"r/CryptoCurrency Daily Discussion - {curr_datetime.strftime('%B %d, %Y')}"),
                        html.H6("Reddit Retail Investors - What Are They Up To Today?")
                    ], style={'textAlign': 'left'}, className='mt-2 ml-n5 mb-n2')
                ], style={'border': 'none'})
            ], width=8, md=8, lg=9, sm=10, xs=10)
        ], no_gutters=False),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Hr(id='empty-line', children=[])
                    ], className='mt-n5 mb-n5')
                ], style={'border': 'none'})
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("What's Popular?", style={'textAlign': 'left'}, className='mt-n4 ml-3')
                    ], style={'height': '40px'})
                ], style={'width': '130px', 'border': 'none'}),
            ], width=2, sm=3, xs=5, md=2, lg=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-1-coin',
                                    src=curr_top_coins[0],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-1-tooltip',
                                children=top_coin.iloc[0]['Coin'],
                                placement='bottom',
                                target='rank-1-coin')
                ], style={'width': '30px', 'height': '30px', 'border': 'none'}),
            ], width=1, sm=2, xs=2, md=1),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-2-coin',
                                    src=curr_top_coins[1],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-2-tooltip',
                                children=top_coin.iloc[1]['Coin'],
                                placement='bottom',
                                target='rank-2-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}),
            ], width=1, sm=2, xs=2, md=1),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-3-coin',
                                    src=curr_top_coins[2],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-3-tooltip',
                                children=top_coin.iloc[2]['Coin'],
                                placement='bottom',
                                target='rank-3-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}),
            ], width=1, sm=2, xs=2, md=1),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-4-coin',
                                    src=curr_top_coins[3],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-4-tooltip',
                                children=top_coin.iloc[3]['Coin'],
                                placement='bottom',
                                target='rank-4-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-sm-block'),
            ], width=1, sm=2, md=1, className='d-none d-sm-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-5-coin',
                                    src=curr_top_coins[4],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-5-tooltip',
                                children=top_coin.iloc[4]['Coin'],
                                placement='bottom',
                                target='rank-5-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-sm-block'),
            ], width=1, md=1, className='d-none d-sm-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-6-coin',
                                    src=curr_top_coins[5],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-6-tooltip',
                                children=top_coin.iloc[5]['Coin'],
                                placement='bottom',
                                target='rank-6-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-md-block'),
            ], width=1, md=1, className='d-none d-md-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-7-coin',
                                    src=curr_top_coins[6],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-7-tooltip',
                                children=top_coin.iloc[6]['Coin'],
                                placement='bottom',
                                target='rank-7-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-md-block'),
            ], width=1, md=1, className='d-none d-md-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-8-coin',
                                    src=curr_top_coins[7],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-8-tooltip',
                                children=top_coin.iloc[7]['Coin'],
                                placement='bottom',
                                target='rank-8-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-md-block'),
            ], width=1, md=1, className='d-none d-md-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-9-coin',
                                    src=curr_top_coins[8],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-9-tooltip',
                                children=top_coin.iloc[8]['Coin'],
                                placement='bottom',
                                target='rank-9-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-md-block'),
            ], width=1, md=1, className='d-none d-md-block'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardImg(id='rank-10-coin',
                                    src=curr_top_coins[9],
                                    className='mt-n4 ml-n3',
                                    style={'height': '30px', 'width': '30px'})
                    ]),
                    dbc.Tooltip(id='rank-10-tooltip',
                                children=top_coin.iloc[9]['Coin'],
                                placement='bottom',
                                target='rank-10-coin')
                ], style={'width': '40px', 'height': '40px', 'border': 'none'}, className='d-none d-md-block'),
            ], width=1, md=1, className='d-none d-md-block')
        ], no_gutters=True, className='mb-2'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Hr(id='empty-line-2', children=[])
                    ], className='my-n4 mb-0')
                ], style={'border': 'none'})
            ], width=12)
        ], className='mt-n2'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(id='top-comments-table',
                                 children=[
                                     dash_table.DataTable(
                                         data=reddit_data[:10].to_dict('records'),
                                         sort_action='native',
                                         columns=[
                                             {'name': i, 'id': i} for i in ['Top Comments', 'Karma']
                                         ],
                                         fixed_rows={'headers': True},
                                         style_header={
                                             'fontWeight': 'bold',
                                             'fontSize': '15px',
                                             'padding': '10px 10px 10px 10px'
                                         },
                                         style_cell={
                                             # all three widths are needed
                                             'whiteSpace': 'normal',
                                             'maxWidth': '250px',
                                             'padding': '15px 12px 15px 12px',
                                             'lineHeight': '20px',
                                             'height': 'auto',
                                             'overflow': 'hidden',
                                             'textAlign': 'left',
                                             'backgroundColor': 'rgba(0,0,0,0)',
                                             'fontSize': '15px'
                                         },
                                         style_cell_conditional=[
                                             {'if': {'column_id': 'Top Comments'},
                                              'width': '70%'},
                                             {'if': {'column_id': 'Karma'},
                                              'width': '30%'},
                                         ],
                                         style_data_conditional=[
                                             {
                                                 'if': {'row_index': 'even'},
                                                 'backgroundColor': 'rgba(244,244,244,1)'
                                             }
                                         ],
                                         style_table={'overflowY': 'auto', 'height': '295px', 'minWidth': '100%'}
                                     )], style={'padding': '0px 0px 0px 0px'})
                ], style={'border': 'none'}, className='mb-2'),
            ], width=5, sm=12, md=5, xs=12),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Most Mentioned Coins in the Comment Section",
                                style={'fontSize': '15px',
                                       'fontWeight': 'bold'}),
                        style={'height': '42px',
                               'padding': '10px 10px 10px 18px'}
                    ),
                    dbc.CardBody([
                        dcc.Graph(id='top-coin-graph',
                                  figure=most_mentioned_bar)
                    ], style={'padding': '20px 30px 10px 10px'})
                ], className='mt-0')
            ], width=7, sm=12, md=7, xs=12)
        ], className='mb-2 mt-2'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Most Popular/Controversial Coins",
                                style={'fontSize': '15px',
                                       'fontWeight': 'bold'}),
                        style={'height': '42px',
                               'padding': '10px 10px 10px 18px'}
                    ),
                    dbc.CardBody(id='crypto-table',
                                 children=[
                                     dash_table.DataTable(
                                         data=top_coin.to_dict('records'),
                                         sort_action='native',
                                         columns=[
                                             {'name': i, 'id': i} for i in top_coin.columns
                                         ],
                                         fixed_rows={'headers': True},
                                         style_header={
                                             'fontWeight': 'bold',
                                             'fontSize': '15px',
                                             'padding': '10px 10px 10px 18px',
                                             'height': 'auto',
                                             'maxWidth': 'auto'
                                         },
                                         style_cell={
                                             # all three widths are needed
                                             'whiteSpace': 'normal',
                                             'maxWidth': 'auto',
                                             'padding': '10px 10px 10px 10px',
                                             'lineHeight': '20px',
                                             'height': 'auto',
                                             'overflow': 'hidden',
                                             'textAlign': 'left',
                                             'backgroundColor': 'rgba(0,0,0,0)',
                                             'fontSize': '15px'
                                         },
                                         style_data_conditional=[
                                             {
                                                 'if': {
                                                     'filter_query': '{1h Change (%)} >= 0',
                                                     'column_id': '1h Change (%)'
                                                 },
                                                 'color': 'green',
                                                 'fontWeight': 'bold'
                                             },
                                             {
                                                 'if': {
                                                     'filter_query': '{1h Change (%)} < 0',
                                                     'column_id': '1h Change (%)'
                                                 },
                                                 'color': 'tomato',
                                                 'fontWeight': 'bold'
                                             },
                                             {
                                                 'if': {
                                                     'filter_query': '{24h Change (%)} >= 0',
                                                     'column_id': '24h Change (%)'
                                                 },
                                                 'color': 'green',
                                                 'fontWeight': 'bold'
                                             },
                                             {
                                                 'if': {
                                                     'filter_query': '{24h Change (%)} < 0',
                                                     'column_id': '24h Change (%)'
                                                 },
                                                 'color': 'tomato',
                                                 'fontWeight': 'bold'
                                             },
                                             {
                                                 'if': {
                                                     'filter_query': '{7d Change (%)} >= 0',
                                                     'column_id': '7d Change (%)'
                                                 },
                                                 'color': 'green',
                                                 'fontWeight': 'bold'
                                             },
                                             {
                                                 'if': {
                                                     'filter_query': '{7d Change (%)} < 0',
                                                     'column_id': '7d Change (%)'
                                                 },
                                                 'color': 'tomato',
                                                 'fontWeight': 'bold'
                                             }
                                         ],
                                         style_table={'overflowY': 'auto', 'overflowX': 'scroll',
                                                      'height': '300px'},
                                         style_cell_conditional=[
                                             {'if': {'column_id': 'Coin'},
                                              'width': '17%'},
                                             {'if': {'column_id': 'Coin Code'},
                                              'width': '12%'},
                                             {'if': {'column_id': 'Price in USD ($)'},
                                              'width': '14%'},
                                             {'if': {'column_id': '24h Change (%)'},
                                              'width': '14%'},
                                             {'if': {'column_id': '1h Change (%)'},
                                              'width': '13%'},
                                             {'if': {'column_id': '7d Change (%)'},
                                              'width': '13%'},
                                             {'if': {'column_id': 'Mention Counts'},
                                              'width': '20%'}
                                         ],
                                     )], style={'height': "100%", 'padding': '0px 0px 0px 0px', 'border': 'none'})
                ], className='mb-3'),
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("r/CryptoCurrency's Market Sentiment",
                                style={'fontSize': '15px',
                                       'fontWeight': 'bold'}),
                        style={'height': '42px',
                               'padding': '10px 10px 10px 18px'}
                    ),
                    dbc.CardBody([
                        dcc.Graph(id='pie-chart',
                                  figure=sentiment_pie_chart,
                                  style={'height': '100%',
                                         'width': '100%'}
                                  )
                    ])
                ], style={'height': '378px'}, className='mb-1'),
            ], width=5, sm=12, xs=12, md=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Most Popular/Controversial Coins' Charts",
                                style={'fontSize': '15px',
                                       'fontWeight': 'bold'}),
                        style={'height': '42px',
                               'padding': '10px 10px 10px 18px'}
                    ),
                    dcc.Dropdown(id='dropdown',
                                 options=dropdown_items,
                                 value=top_coin.iloc[0]['Coin'],
                                 style=dict(
                                     height='10%',
                                     padding='0px 0px 0px 0px'
                                 ),
                                 className='mt-2 ml-2 mr-2'),
                    dbc.CardBody([
                        dcc.Graph(id='coin-candlestick',
                                  figure=get_candlestick(top_coin.iloc[0]['Coin']),
                                  style={'height': '270px'})
                    ], style={'padding': '10px 10px 10px 10px'}, className='mt-0')
                ])
            ], style={'border': 'none'}, width=7, xs=12, sm=12, md=7),
        ], className='mb-1'),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Hr(id='empty-line-3', children=[])
                    ], className='mt-n3 mb-n3')
                ], style={'border': 'none'})
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(id='credit',
                                children=f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                        html.H6(id='credit-2',
                                children="Created and Designed by Oliver Tan",
                                className='mt-n2'),
                    ], className='mt-n4 mb-n3')
                ], style={'border': 'none'})
            ], width=6, xs=6, sm=8, md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.A([
                            html.Img(src='https://image.flaticon.com/icons/png/512/2111/2111425.png',
                                     style={
                                         'height': '30px',
                                         'width': '30px',
                                         'float': 'right',
                                         'position': 'relative',
                                         'padding-top': 0,
                                         'padding-right': 0
                                     }, className='ml-3')
                        ], href='https://github.com/olivertan1999', className='ml-3'),
                        html.A([
                            html.Img(src='https://image.flaticon.com/icons/png/512/2111/2111532.png',
                                     style={
                                         'height': '30px',
                                         'width': '30px',
                                         'float': 'right',
                                         'position': 'relative',
                                         'padding-top': 0,
                                         'padding-right': 0
                                     })
                        ], href='https://www.linkedin.com/in/olivertan10/')
                    ], className='mt-n4 mb-n3')
                ], style={'border': 'none'})
            ], width=6, xs=6, sm=4, md=6)
        ])
    ], fluid=True),
    dcc.Store(id='crypto-store', data=""),
    dcc.Store(id='top-coin-store', data=""),
    dcc.Store(id='reddit-data', data=""),
    dcc.Interval(id='update-interval',
                 interval=600000,
                 n_intervals=0),
    dcc.Interval(id='update-logo-interval',
                 interval=650000,
                 n_intervals=0)
])


@app.callback(
    Output("top-coin-store", 'data'),
    Input("update-interval", 'n_intervals')
)

def update_data(n):
    """ Update reddit and crypto data upon callback.
        Store the updated top coin table in the top-coin-store for later access. """
    
    print("Updating Data...")
    print("Number of update: ", n)

    rs.get_data()
    new_top_coin = rs.count_coins_mentioned().round(2)

    return new_top_coin.to_json(orient='split')


@app.callback(
    Output('rank-1-coin', 'src'),
    Output('rank-1-tooltip', 'children'),
    Output('rank-2-coin', 'src'),
    Output('rank-2-tooltip', 'children'),
    Output('rank-3-coin', 'src'),
    Output('rank-3-tooltip', 'children'),
    Output('rank-4-coin', 'src'),
    Output('rank-4-tooltip', 'children'),
    Output('rank-5-coin', 'src'),
    Output('rank-5-tooltip', 'children'),
    Output('rank-6-coin', 'src'),
    Output('rank-6-tooltip', 'children'),
    Output('rank-7-coin', 'src'),
    Output('rank-7-tooltip', 'children'),
    Output('rank-8-coin', 'src'),
    Output('rank-8-tooltip', 'children'),
    Output('rank-9-coin', 'src'),
    Output('rank-9-tooltip', 'children'),
    Output('rank-10-coin', 'src'),
    Output('rank-10-tooltip', 'children'),
    [Input('update-logo-interval', 'n_intervals'),
     Input('top-coin-store', 'data')]
)

def update_top_coins_2(n_intervals, new_top_coin):
    """ Update the latest top 10 cryptos logos and tooltips. """
    
    final_coins_count = pd.read_json(new_top_coin, 'split')

    coins_rank = {f'rank-{n+1}-coin': final_coins_count.iloc[n]['Coin'] for n in range(10)}

    rank_1 = get_img(coins_rank["rank-1-coin"])
    rank_2 = get_img(coins_rank["rank-2-coin"])
    rank_3 = get_img(coins_rank["rank-3-coin"])
    rank_4 = get_img(coins_rank["rank-4-coin"])
    rank_5 = get_img(coins_rank["rank-5-coin"])
    rank_6 = get_img(coins_rank["rank-6-coin"])
    rank_7 = get_img(coins_rank["rank-7-coin"])
    rank_8 = get_img(coins_rank["rank-8-coin"])
    rank_9 = get_img(coins_rank["rank-9-coin"])
    rank_10 = get_img(coins_rank["rank-10-coin"])

    return rank_1, coins_rank["rank-1-coin"],\
        rank_2, coins_rank["rank-2-coin"],\
        rank_3, coins_rank["rank-3-coin"],\
        rank_4, coins_rank["rank-4-coin"],\
        rank_5, coins_rank["rank-5-coin"],\
        rank_6, coins_rank["rank-6-coin"],\
        rank_7, coins_rank["rank-7-coin"],\
        rank_8, coins_rank["rank-8-coin"],\
        rank_9, coins_rank["rank-9-coin"],\
        rank_10, coins_rank["rank-10-coin"]


@app.callback(
    Output('top-comments-table', 'children'),
    [Input('update-logo-interval', 'n_intervals')]
)

def update_comments_table(n_intervals):
    """ Update the top 10 reddit comments table. """
    
    new_reddit_data = rs.comments_df

    return [dash_table.DataTable(
                data=new_reddit_data[:10].to_dict('records'),
                sort_action='native',
                columns=[
                    {'name': i, 'id': i} for i in ['Top Comments', 'Karma']
                ],
                fixed_rows={'headers': True},
                style_header={
                    'fontWeight': 'bold',
                    'fontSize': '15px',
                    'padding': '10px 10px 10px 10px'
                },
                style_cell={
                    # all three widths are needed
                    'whiteSpace': 'normal',
                    'maxWidth': '250px',
                    'padding': '15px 12px 15px 12px',
                    'lineHeight': '20px',
                    'height': 'auto',
                    'overflow': 'hidden',
                    'textAlign': 'left',
                    'backgroundColor': 'rgba(0,0,0,0)',
                    'fontSize': '15px'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Top Comments'},
                     'width': '70%'},
                    {'if': {'column_id': 'Karma'},
                     'width': '30%'},
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'even'},
                        'backgroundColor': 'rgba(244,244,244,1)'
                    }
                ],
                style_table={'overflowY': 'auto', 'height': '295px'}
            )]


@app.callback(
    Output('top-coin-graph', 'figure'),
    [Input('update-logo-interval', 'n_intervals'),
     Input('top-coin-store', 'data')]
)

def update_most_mentioned_graph(n_intervals, new_top_coin):
    """ Update the most mentioned coin bar chart upon callback. """
    
    # Read the updated data from the top-coin-graph component
    new_top_coin = pd.read_json(new_top_coin, 'split')

    updated_bar_chart = px.bar(new_top_coin[:10], x='Coin Code', y='Mention Counts', height=220)

    updated_bar_chart.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0),
                                    paper_bgcolor="rgb(255,255,255)",
                                    plot_bgcolor="rgb(255,255,255)",
                                    font_family='"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
                                    hoverlabel_bgcolor='rgb(244, 244, 244)',
                                    hoverlabel_font_color='rgb(0,0,0)',
                                    hoverlabel_bordercolor='rgb(211,211,211)')

    updated_bar_chart.update_traces(marker_color='rgb(162,160,165)')

    return updated_bar_chart


@app.callback(
    Output("crypto-table", "children"),
    [Input('update-logo-interval', 'n_intervals'),
     Input('top-coin-store', 'data')]
)

def update_table(n_intervals, new_top_coin):
    """ Update the most mentioned coins table upon callback. """

    new_top_coin = pd.read_json(new_top_coin, 'split').round(2)

    return [dash_table.DataTable(
                data=new_top_coin.to_dict('records'),
                sort_action='native',
                columns=[
                    {'name': i, 'id': i} for i in new_top_coin.columns
                ],
                fixed_rows={'headers': True},
                style_header={
                    'fontWeight': 'bold',
                    'fontSize': '15px',
                    'padding': '10px 10px 10px 18px'
                },
                style_cell={
                    # all three widths are needed
                    'whiteSpace': 'normal',
                    'maxWidth': 'auto',
                    'padding': '10px 10px 10px 10px',
                    'lineHeight': '20px',
                    'height': 'auto',
                    'overflow': 'hidden',
                    'textAlign': 'left',
                    'backgroundColor': 'rgba(0,0,0,0)',
                    'fontSize': '15px'
                },
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{1h Change (%)} >= 0',
                            'column_id': '1h Change (%)'
                        },
                        'color': 'green',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{1h Change (%)} < 0',
                            'column_id': '1h Change (%)'
                        },
                        'color': 'tomato',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{24h Change (%)} >= 0',
                            'column_id': '24h Change (%)'
                        },
                        'color': 'green',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{24h Change (%)} < 0',
                            'column_id': '24h Change (%)'
                        },
                        'color': 'tomato',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{7d Change (%)} >= 0',
                            'column_id': '7d Change (%)'
                        },
                        'color': 'green',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'filter_query': '{7d Change (%)} < 0',
                            'column_id': '7d Change (%)'
                        },
                        'color': 'tomato',
                        'fontWeight': 'bold'
                    }
                ],
                style_table={'overflowY': 'auto', 'overflowX': 'auto', 'minWidth': '100%',
                             'height': '30vh'},
                style_cell_conditional=[
                    {'if': {'column_id': 'Coin'},
                     'width': '17%'},
                    {'if': {'column_id': 'Coin Code'},
                     'width': '10%'},
                    {'if': {'column_id': 'Price in USD ($)'},
                     'width': '14%'},
                    {'if': {'column_id': '24h Change (%)'},
                     'width': '14%'},
                    {'if': {'column_id': '1h Change (%)'},
                     'width': '13%'},
                    {'if': {'column_id': '7d Change (%)'},
                     'width': '13%'}
                ],
            )]


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('update-logo-interval', 'n_intervals')]
)

def update_piechart(n_intervals):
    """ Update the sentiment pie chart upon callback. """

    new_reddit_data = rs.comments_df

    pie_data = new_reddit_data.groupby('sentiment').count()['Top Comments'].reset_index().rename({'Top Comments': 'Comments Count', 'sentiment': 'Sentiment'}, axis=1)

    new_pie_chart = px.pie(pie_data,
                           values='Comments Count',
                           names='Sentiment',
                           color='Sentiment',
                           color_discrete_map={
                                'Positive': 'rgb(232,232,232)',
                                'Neutral': 'rgb(211,211,211)',
                                'Negative': '(rgb(191,191,191))',
                           },
                           height=286)

    new_pie_chart.update_traces(textposition='inside', textinfo='percent+label')

    new_pie_chart.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0),
                                font_family='"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
                                font_size=15,
                                hoverlabel_bgcolor='rgb(244, 244, 244)',
                                hoverlabel_font_color='rgb(0,0,0)',
                                hoverlabel_bordercolor='rgba(0,0,0,0)')

    return new_pie_chart


@app.callback(
    Output('title', 'children'),
    Output('credit', 'children'),
    Input('update-logo-interval', 'n_intervals')
)

def update_title(n):
    """ Update the header and footer upon callback. """

    return f"r/CryptoCurrency Daily Discussion - {datetime.datetime.now().strftime('%B %d, %Y')}",\
           f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@app.callback(
    Output('coin-candlestick', 'figure'),
    Input('dropdown', 'value')
)

def update_line_chart(value):
    """ Update the candlestick chart based on the dropdown element selected. """

    return get_candlestick(value)


if __name__ == '__main__':
    app.run_server(debug=False, port=8000)
