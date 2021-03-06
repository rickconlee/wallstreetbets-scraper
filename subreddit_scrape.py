import util # random local util functions
import configparser
import praw # reddit sdk
from psaw import PushshiftAPI # reddit sdk wrapper
import re
import datetime
from textblob import TextBlob

# ==================================================================
# Rowan University, Data Quality and Web Text Mining Final Project
# Patrick Richeal, last modified 2019-12-03
# 
# subreddit_scrape.py - Scrapes the desired subreddit for mention
#     of stock ticker symbols and gathers data about frequency/time
#     of mention
# ==================================================================

# get config data
util.log('Reading config data...')
config = configparser.ConfigParser()
config.read('config.ini')

# Load symbols from symbols.txt file
util.log('Loading symbols from symbols.txt...')
symbols_file = open('symbols.txt', 'r')
symbols = symbols_file.read().splitlines()
symbols_file.close()

# function to find any stock symbol in given string
def get_symbol_matches(text):
    matches = []
    for symbol in symbols:
        result = re.search('[ ]+' + symbol + '[ ]+', text)
        if result != None:
            matches.append(result.group(0).strip())
    return matches

# open symbol mentions file to write to
util.log('Opening symbol_mentions.csv file for writing to...')
symbol_mentions_file = open('symbol_mentions.csv', 'w+')

# regex for alpha and spaces only
alpha_regex = re.compile('[^a-zA-Z ]')

# initialize reddit sdk object
util.log('Initializing reddit sdks...')
reddit = praw.Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent=config['reddit']['user_agent']
)
api = PushshiftAPI(reddit)

# setup submission generator to loop over reddit posts on given subreddit over given date range
util.log('Setting up submission generator...')
start_epoch=int(datetime.datetime(2018, 1, 1).timestamp())
end_epoch=int(datetime.datetime(2019, 1, 1).timestamp())
submission_generator = api.search_submissions(subreddit = 'stocks', after = start_epoch, before = end_epoch)

# loop over submissions
util.log('Reading submissions for stock symbols...')
for submission in submission_generator:
    # setup search string to get symbol matches on
    search_string = ' ' + submission.title + ' ' + submission.selftext + ' '
    search_string = alpha_regex.sub(' ', search_string).lower()

    # get symbol matches using above search_string
    symbol_matches = get_symbol_matches(search_string)

    # if we got any symbol matches, get sentiment of submission title and text
    sentiment = 0
    if symbol_matches:
        textblob_obj = TextBlob(search_string)
        sentiment_val = textblob_obj.sentiment
        if sentiment_val.polarity >= 0:
            sentiment = 1
        else:
            sentiment = -1

    # for each symbol found in the content
    for symbol in symbol_matches:
        # setup line that we will write to the file
        data_string = str(int(submission.created_utc)) + ',' + symbol + ',' + str(sentiment)
        print(data_string)
        symbol_mentions_file.write(data_string + '\n')

# close file
symbol_mentions_file.close()