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
from os import remove

logging_level = getattr(logging, environ['logging_level'].upper())

subreddit = environ['subreddit']
post_qty = int(environ['post_qty'])

webhook_uri = environ.get('webhook_uri')

webdav_uri = environ.get('webdav_uri')
webdav_user = environ.get('webdav_user')
webdav_pass = environ.get('webdav_pass')


def search_subreddit(qty):
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
    data = {"content": message}

    result = requests.post(webhook_uri, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.warning(err)
    else:
        logging.info("Successfully shitposted!")
        logging.debug(data)

def upload_webdav(file_uri, subreddit):

    file_name = re.findall(r"https:\/\/.*\/([a-zA-Z0-9.]*)", file_uri)
    file_type = re.findall(r"https:\/\/.*\/.*\.(.*)", file_uri)
    logging.debug(f"From {file_uri} found {file_name[0]}")
    result = requests.get(file_uri)

    file = open(file_name[0], "wb")
    file.write(result.content)
    file.close()

    if file_type[0] == "jpg":
        content_type = "image/jpeg"
    elif file_type[0] == "png":
        content_type = "image/png"
    else:
        logging.info("No clue what this filetype is, eject!")
        sys.exit()

    uri = f"{webdav_uri}/{file_name[0]}"
    logging.debug(uri)

    header = {"content-type": content_type}
    result = requests.put(uri, data=open(file_name[0], "rb"), headers=header, auth=(webdav_user, webdav_pass))

    try:
        result.raise_for_status()
        logging.info(f"Upload of {file_name[0]} complete")
    except requests.exceptions.HTTPError as err:
        logging.warning(err)
    
    remove(file_name[0])
    logging.debug(f"Deleted {file_name[0]}")

if webdav_uri == None:
    webdav = False
else:
    webdav = True

if webhook_uri == None:
    webhook = False
else:
    webhook = True

logging.basicConfig(stream=sys.stdout, level=logging_level)
logging.info("Starting the_collector")
logging.debug("\t- Subreddit: {}".format(subreddit))
logging.debug("\t- Quantity: {}".format(post_qty))
logging.debug("\t- Logging level: {}".format(environ['logging_level']))
if webhook == True:
    logging.debug("\t- Webhook URI: {}".format(webhook_uri))
if webdav == True:
    logging.debug("\t- WebDAV URI: {}".format(webdav_uri))
    logging.debug("\t- WebDAV User: {}".format(webdav_user))
    logging.debug("\t- WebDAV Pass: {}".format(webdav_pass))

results = search_subreddit(post_qty)
logging.info(f"Collected {len(results)} image links")
for post in results:
    if webhook == True:
        post_discord_message(webhook_uri, post)
        sleep(1)
    
    if webdav == True:
        upload_webdav(post, subreddit)

logging.info("We're done here")
