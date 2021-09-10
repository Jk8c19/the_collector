# the_collector
Grabs imgur and i.reddit images from subreddits, then posts them to discord via a webhook url and/or pass it WebDAV details to upload the files to a folder.

```
docker run \
  --name=the_collector \
  --rm \
  -e subreddit="" \
  -e webhook_url="" \
  -e post_qty=1 \
  -e logging_level="info" \
  -e webdav_url="" \
  -e webdav_user="" \
  -e webdav_pass="" \
  -e hc_url="" \
  jk8c19/the_collector:latest
```

This is a run once container, so using --rm will clean up once it's done its thing.

WebDAV upload was intended for use with Nextcloud and is only tested for this application.

# Parameters

| Parameter | Function | Req | Default |
|-|-|-|-|
| subreddit | name of a reddit subreddit | Y
| webhook_url | full url to discord webhook | N
| post_qty | amount of posts to gather | N | 1 |
| logging_level | takes in logging level | N | info |
| webdav_url | path to put image to | N
| webdav_user | webdav username | N
| webdav_pass | webdav application password | N
| hc_url | Healthchecks URL to ping | N