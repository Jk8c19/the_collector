# the_collector
Grabs imgur and i.reddit images from subreddits, then posts them to discord via a webhook uri and/or pass it WebDAV details to upload the files to a folder.

```
docker run \
  --name=the_collector \
  --rm \
  -e subreddit="" \
  -e webhook_uri="" \
  -e post_qty=1 \
  -e logging_level="info" \
  -e webdav_uri="" \
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
| webhook_uri | full uri to discord webhook | N
| post_qty | amount of posts to gather | N | 1 |
| logging_level | takes in logging level | N | info |
| webdav_uri | path to put image to | N
| webdav_user | webdav username | N
| webdav_pass | webdav application password | N
| hc_url | Healthchecks URL to ping | N