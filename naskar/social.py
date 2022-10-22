import tweepy
import requests

class Social:
  FB_GRAPH = "https://graph.facebook.com/v15.0/me/"
  def __init__(self, keys):
    self.discord = keys["discord"]
    # v1.1 can upload media
    #self.twitter = tweepy.OAuth1UserHandler(
    #  consumer_key=keys["twitter"]["consumer_key"],
    #  consumer_secret=keys["twitter"]["consumer_secret"],
    #  access_token=keys["twitter"]["access_token"],
    #  access_token_secret=keys["twitter"]["access_token_secret"]
    #)
    self.facebook = keys["facebook"]
    self.instagram = keys["instagram"]

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
    # file object?
    media = self.twitter.media_upload("sonnet.png", file=img, media_category="tweet_image")
    self.twitter.update_status(
      status=title,
      media_ids=[media.id]
    )

  def upload_facebook(self, title, desc, img, img_url):
    r = requests.post(self.FB_GRAPH + "media", params={
      "url": img_url,
      "caption": title,
      "access_token": self.facebook
    })
    r.raise_for_status()

  def upload_instagram(self, title, desc, img, img_url):
    r = requests.post(self.FB_GRAPH + "media", params={
      "image_url": img_url,
      "caption": title,
      "access_token": self.instagram
    })
    r.raise_for_status()
    r = r.json()["id"]
    r = requests.post(self.FB_GRAPH + "media_publish", params={
      "creation_id": r,
      "access_token": self.instagram
    })
    r.raise_for_status()

  def upload(self, title, desc, img):
    # jank to have an uploaded copy somehwere
    img_url = self.upload_discord(title, desc, img)
    for up in []:
      try:
        up(title, desc, img, img_url)
      except Exception as e:
        print(up.__name__, e)

