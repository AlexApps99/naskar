from PIL import Image, ImageFont, ImageDraw
from random import choice
import json
from io import BytesIO

# TODO title
class Render:
  '''
  Facilitates turning a sonnet into an image
  '''
  def __init__(self, filename="templates.json"):
    with open(filename, "rb") as f:
      self.templates = json.load(f)

  def get_template(self, load=True):
    '''
    Picks a random template, loading the image in the process
    '''
    t = choice(self.templates)
    if load:
      if "img" not in t:
        with Image.open(t["file"]) as img:
          img.load()
        t["img"] = img
    return t

  def add_text(self, imgdraw, text, p):
    '''
    Adds text to image, given text params p
    '''
    # TODO scale the font size until the text fits the bounds
    font = ImageFont.truetype("/usr/share/fonts/TTF/" + p.get("font", "Roboto-Regular.ttf"), p["size"])
    cent = p.get("center", False)
    imgdraw.text(
      xy=p["xy"][0],
      text=text,
      fill=p["fill"],
      font=font,
      spacing=p.get("spacing", 4),
      anchor="ma" if cent else "la",
      align="center" if cent else "left"
    )

  def generate(self, title, sonnet, format=None):
    '''
    Generates an image from a given sonnet
    '''
    t = self.get_template()
    img = t["img"].copy()
    d = ImageDraw.Draw(img)
    self.add_text(d, title, t["title"])
    self.add_text(d, sonnet, t["text"])
    if format:
      return Render.encode(img, format)
    else:
      return img

  def encode(img, format):
    imgb = BytesIO()
    img.save(imgb, format=format)
    return imgb.getvalue()

