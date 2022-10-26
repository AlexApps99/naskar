from PIL import Image, ImageFont, ImageDraw
from random import choice
from io import BytesIO

class Render:
  '''
  Facilitates turning a sonnet into an image
  '''
  def __init__(self, templates, debug=False):
    self.templates = templates
    self.debug = debug
    for k, v in self.templates.items():
      v["name"] = k

  def get_template(self, name=None, load=True):
    '''
    Picks a random template, loading the image in the process
    '''
    if name:
      t = self.templates[name]
    else:
      t = choice(list(self.templates.values()))
    if load:
      if "img" not in t:
        with Image.open("templates/" + t["file"]) as img:
          img.load()
        t["img"] = img
    return t

  def add_text(self, imgdraw, text, p):
    '''
    Adds text to image, given text params p
    '''
    font = ImageFont.truetype("templates/" + p.get("font", "Roboto-Regular.ttf"), p["size"])
    cent = p.get("center", False)
    if self.debug: imgdraw.rectangle([tuple(c) for c in p["xy"]], "#ff00ff40")
    imgdraw.text(
      xy=p["xy"][0],
      text=text,
      fill=p["fill"],
      font=font,
      spacing=p.get("spacing", 4),
      anchor="ma" if cent else "la",
      align="center" if cent else "left"
    )

  def generate(self, title, sonnet, template=None, format=None):
    '''
    Generates an image from a given sonnet
    '''
    t = self.get_template(template)
    img = t["img"].copy()
    d = ImageDraw.Draw(img)
    self.add_text(d, title, t["title"])
    self.add_text(d, sonnet, t["text"])

    if format:
      img = Render.encode(img, format)
    return (img, t["name"])

  def encode(img, format):
    '''
    Encodes a Pillow image into the given format
    '''
    imgb = BytesIO()
    img.save(imgb, format=format)
    return imgb.getvalue()

