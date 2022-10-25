import tweepy
import requests
from io import BytesIO

class Social:
  FB_GRAPH = "https://graph.facebook.com/v15.0/"
  def __init__(self, keys):
    self.discord = keys["discord"]
    # v1.1 can upload media
    self.twitter1 = tweepy.OAuth1UserHandler(
      consumer_key=keys["twitter"]["consumer_key"],
      consumer_secret=keys["twitter"]["consumer_secret"],
      access_token=keys["twitter"]["access_token"],
      access_token_secret=keys["twitter"]["access_token_secret"]
    )
    self.twitter1 = tweepy.API(self.twitter1)
    self.twitter2 = tweepy.Client(
      consumer_key=keys["twitter"]["consumer_key"],
      consumer_secret=keys["twitter"]["consumer_secret"],
      access_token=keys["twitter"]["access_token"],
      access_token_secret=keys["twitter"]["access_token_secret"]
    )
    self.meta = keys["meta"]
    self.ig_id = str(keys["ig_id"])
    self.fb_id = str(keys["fb_id"])

  def upload_discord(self, title, desc, img):
    r = requests.post(self.discord + "?wait=true", data={
      "content": "**" + title + "**\n" + desc,
    }, files={
      "files[0]": ("sonnet.png", img, "image/png")
    })
    r.raise_for_status()
    # I'm lazy, so this is required for Facebook/instagram to work
    return r.json()["attachments"][0]["url"]

  def upload_twitter(self, title, desc, img, img_url):
    # Twitter only allows media uploads on v1.1 api (bruh)
    media = self.twitter1.media_upload("sonnet.png", file=BytesIO(img), media_category="tweet_image")
    self.twitter2.create_tweet(
      text=title,
      media_ids=[media.media_id],
      user_auth=True
    )

  def upload_facebook(self, title, desc, img, img_url):
    r = requests.get(self.FB_GRAPH + self.fb_id, params={"fields": "access_token", "access_token": self.meta})
    r.raise_for_status()
    page_token = r.json()["access_token"]
    r = requests.post(self.FB_GRAPH + self.fb_id + "/photos", params={
      "url": img_url,
      "caption": title,
      "alt_text_custom": desc,
      "access_token": page_token
    })
    r.raise_for_status()

  def upload_instagram(self, title, desc, img, img_url):
    r = requests.post(self.FB_GRAPH + self.ig_id + "/media", params={
      "image_url": img_url,
      "caption": title,
      "access_token": self.meta
    })
    r.raise_for_status()
    r = r.json()["id"]
    r = requests.post(self.FB_GRAPH + self.ig_id + "/media_publish", params={
      "creation_id": r,
      "access_token": self.meta
    })
    r.raise_for_status()

  def upload(self, title, desc, img):
    # jank to have an uploaded copy somehwere
    img_url = self.upload_discord(title, desc, img)
    for up in [self.upload_twitter, self.upload_facebook, self.upload_instagram]:
      try:
        up(title, desc, img, img_url)
      except Exception as e:
        print(up.__name__, e)

