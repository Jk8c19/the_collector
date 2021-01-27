'''
This script will take in given environment variables to post the top x images from a given subreddit to a discord webhook.
'''
import feedparser
import requests
import sys
import logging
import re
from time import sleep
from os import environ

subreddit = environ['subreddit']
webhook_uri = environ['webhook_uri']
post_qty = int(environ['post_qty'])
logging_level = getattr(logging, environ['logging_level'].upper())

def search_subreddit(subreddit, qty):
    feed = feedparser.parse('https://reddit.com/r/'+subreddit+'.rss')
    entries = []
    for x in range(post_qty+2):
        if x != (1,2):
            data = feed.entries[x].content[0].value
            link = re.search(r"(https:\/\/i.redd.it\/\w*.jpg|https:\/\/i.redd.it\/\w*.png|https:\/\/i.imgur.com/\w*.jpg|https:\/\/i.imgur.com/\w*.png)", data)
            if link != None:
                entries.append(link.group())
    return entries

def post_discord_message(webhook_uri, message):
    data = {
        "content": message
    }

    result = requests.post(webhook_uri, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.warning(err)
    else:
        logging.info("Successfully shitposted m'lord")
        logging.debug(data)
        

logging.basicConfig(stream=sys.stdout, level=logging_level)
logging.info("Starting the_collector")
logging.debug("\t- Subreddit: {}".format(subreddit))
logging.debug("\t- Webhook URI: {}".format(webhook_uri))
logging.debug("\t- Quantity: {}".format(post_qty))
logging.debug("\t- Logging level: {}".format(environ['logging_level']))

results = search_subreddit(subreddit,post_qty)
logging.info(f"Collected {len(results)} image links")
for post in results:
    post_discord_message(webhook_uri, post)
    sleep(1)
logging.info("We're done here")
