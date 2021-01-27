# the_collector
Grabs imgur and i.reddit images from subreddits, then posts them to discord via a webhook uri.

```
docker run \
  --name=the_collector \
  --rm \
  -e subreddit=""\
  -e webhook_uri=""\
  -e post_qty=1\
  -e logging_level="info" \
  --restart unless-stopped \
  jk8c19/the_collector:latest
```

This is a run once container, so using --rm will clean up once it's done its thing.

# Parameters

| Parameter | Function | Req | Default |
|-|-|-|-|
| subreddit | name of a reddit subreddit | Y
| webhook_uri | full uri to discord webhook | Y
| post_qty | amount of posts to gather | N | 1 |
| logging_level | takes in logging level | N | info |