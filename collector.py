'''
This script will take in given environment variables to post the top x images from a given subreddit to a discord webhook.
'''
import feedparser
import requests
import sys
import logging
import re
from time import sleep
from datetime import datetime
from os import environ
from os import remove

logging_level = getattr(logging, environ['logging_level'].upper())

subreddit = environ['subreddit']
subreddit_flair = environ['subreddit_flair']
post_qty = int(environ['post_qty'])

webhook_url = environ.get('webhook_url')

webdav_url = environ.get('webdav_url')
webdav_user = environ.get('webdav_user')
webdav_pass = environ.get('webdav_pass')


def ping_hc(suffix):
    # ping Health Checks if rnv variable set
    if environ.get('hc_url') is not None:
        hc_url = environ['hc_url']
        try:
            logging.info("Sending Health Checks ping")
            requests.get(f"{hc_url}/{suffix}", timeout=10)
        except requests.RequestException as e:
            # Log ping failure here...
            logging.error("Ping failed: %s" % e)

def search_subreddit(qty):
    feed_collected = False
    feed_attempts = 0
    while feed_collected != True:
        if subreddit_flair == "none":
            feed = feedparser.parse('https://reddit.com/r/'+subreddit+'.rss')
        else:
            feed = feedparser.parse('https://reddit.com/r/'+subreddit+'/search.rss?q=flair%3A'+subreddit_flair+'&restrict_sr=on&include_over_18=on&sort=hot&t=all')

        if feed['bozo'] == False:
            feed_collected = True
        else:
            feed_attempts += 1
            if feed_attempts > 5:
                logging.error("Unable to obtain RSS feed after 5 attempts.")
                sys.exit()
            logging.info("No RSS data obtained, retrying...")
            sleep(5)

    entries = []
    for x in range(qty):
        if subreddit_flair != "none" or subreddit_flair == "none" and x != 1:
            data = feed.entries[x].content[0].value
            logging.debug(f"Searching for links from:\n{data}")
            link = re.search(r"(https:\/\/i\.redd\.it\/\w*\.jpg|https:\/\/i\.redd\.it\/\w*\.png|https:\/\/i\.imgur\.com/\w*\.jpg|https:\/\/i\.imgur\.com/\w*\.png)", data)
            gallery = re.search(r"https://www\.reddit\.com/gallery/.*href=\"(https://www\.reddit\.com/r/.*/comments/.*)/\">", data)

            if gallery != None:
                try:
                    results = requests.get(gallery.group(1)+'.json', timeout=10, headers={'User-agent': 'the_collector'})
                except requests.RequestException as e:
                    logging.error("Collecting gallery JSON failed: %s" % e)

                listing = results.json()[0]
                for child in listing['data']['children']:
                    if 'media_metadata' in child['data']:
                        for post in child['data']['media_metadata']:
                            entries.append(child['data']['media_metadata'][post]['s']['u'].replace('&amp;','&'))

            if link != None:
                entries.append(link.group())
    return entries

def post_discord_message(webhook_url, message):
    data = {"content": message}

    result = requests.post(webhook_url, json=data, headers={'User-agent': 'the_collector'})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        ping_hc("fail")
        logging.warning(err)
        exit
    else:
        logging.info("Successfully shitposted!")
        logging.debug(data)

def upload_webdav(file_url):

    file_name = re.findall(r"https:\/\/.*\/([a-zA-Z0-9.]*)", file_url)
    file_type = re.findall(r"https:\/\/.*\/.*\.([a-z]*)", file_url)
    logging.debug(f"From {file_url} found name:  {file_name}")
    logging.debug(f"From {file_url} found type: {file_type}")

    if not file_type or not file_name:
        logging.error(f"No vaild file found from url: {file_url}")
        return

    result = requests.get(file_url)

    file = open(file_name[0], "wb")
    file.write(result.content)
    file.close()

    if file_type[0] == "jpg":
        content_type = "image/jpeg"
    elif file_type[0] == "png":
        content_type = "image/png"
    elif file_type[0] == "gif":
        content_type = "image/gif"
    else:
        logging.info("No clue what this filetype is, eject!")
        sys.exit()

    year = datetime.now().year
    month = f"{datetime.now().month:{0}{2}}"

    url = f"{webdav_url}/{year}/{month}/{file_name[0]}"
    logging.debug(url)

    header = {"content-type": content_type}
    result = requests.put(url, data=open(file_name[0], "rb"), headers=header, auth=(webdav_user, webdav_pass))

    if result.status_code == 404:
        logging.info("Initial upload failed due to missing folder, creating one now")
        session = requests.session()
        session.auth = (webdav_user, webdav_pass)
        result = session.request(method='MKCOL', url=f"{webdav_url}/{year}/{month}")

        if result.status_code == 201:
            logging.info("New folder created, retrying upload")
            result = requests.put(url, data=open(file_name[0], "rb"), headers=header, auth=(webdav_user, webdav_pass))
        else:
            ping_hc("fail")
            logging.warning("Could not create new folder!")
            exit

    try:
        result.raise_for_status()
        logging.info(f"Upload of {file_name[0]} complete")
    except requests.exceptions.HTTPError as err:
        ping_hc("fail")
        logging.warning(err)
        exit
    
    remove(file_name[0])
    logging.debug(f"Deleted {file_name[0]}")


logging.basicConfig(stream=sys.stdout, level=logging_level)
logging.info("Starting the_collector")

if webdav_url == None:
    logging.info("No url webdav passed, wont upload.")
    webdav = False
else:
    webdav = True

if webhook_url == None:
    logging.info("No url webhook passed, wont upload.")
    webhook = False
else:
    webhook = True

ping_hc("start")

if post_qty > 25:
    logging.info("Search qty cannot exceed 25, limiting.")
    post_qty = 25

logging.debug("\t- Subreddit: {}".format(subreddit))
logging.debug("\t- Quantity: {}".format(post_qty))
logging.debug("\t- Logging level: {}".format(environ['logging_level']))
if webhook == True:
    logging.debug("\t- Webhook url: {}".format(webhook_url))
if webdav == True:
    logging.debug("\t- WebDAV url: {}".format(webdav_url))
    logging.debug("\t- WebDAV User: {}".format(webdav_user))
    logging.debug("\t- WebDAV Pass: {}".format(webdav_pass))

results = search_subreddit(post_qty)

logging.info(f"Collected {len(results)} image links:")
for post in results:
    logging.info(f"    - {post}")
for post in results:
    if webhook == True:
        post_discord_message(webhook_url, post)
        sleep(1)
    
    if webdav == True:
        upload_webdav(post)

ping_hc("")
logging.info("We're done here")
