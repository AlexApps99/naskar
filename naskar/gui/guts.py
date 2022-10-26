from ..gpt import complete
from ..clean import clean
from ..social import Social
from ..render import Render
import json
import os

class SonnetGuts:
  '''
  Contains headless logic for sonnet generation
  '''
  keys = None
  render = None
  social = None

  def __init__(self):
    if not self.keys:
      with open("keys.json", "rb") as f:
        self.keys = json.load(f)
    if not self.render:
      self.render = Render("templates.json")
    if not self.social:
      self.social = Social(self.keys)
    self.templates = list(self.render.templates.keys())

  def gen_sonnets(self, title, prompt):
    '''
    Generate sonnets using GPT, returning a dict with sonnet data
    '''
    title = title.strip()
    prompt = prompt.strip()
    if title and prompt:
      prompt += "\n\n"
      gpt = complete(prompt, self.keys["openai"])
      sonnets = clean(gpt, prune=False)
      for sonnet in sonnets:
        sonnet["title"] = title
        sonnet["template"] = None
      return {
        "prompt": prompt,
        "gpt": gpt,
        "sonnets": sonnets,
      }
    else:
      return None

  def render_sonnets(self, data):
    '''
    Render sonnets using dict from gen_sonnets()
    '''
    for sonnet in data["sonnets"]:
      img, template = self.render.generate(sonnet["title"], sonnet["text"], sonnet["template"])
      sonnet["image"] = img
      sonnet["template"] = template
    return True

  def upload_sonnet(self, data, idx):
    '''
    Upload sonnet using dict from render_sonnets() and index within dict
    '''
    if not (data and idx >= 0 and idx < len(data["sonnets"])):
      return False
    sonnet = data["sonnets"][idx]
    png = Render.encode(sonnet["image"], "png")
    os.makedirs("log", exist_ok=True)
    try:
      with open("log/log.json", "x") as f:
        f.write("[]")
    except FileExistsError:
      pass

    with open("log/log.json", "r+") as f:
      j = json.load(f)
      l = len(j)
      j.append({
        "title": sonnet["title"],
        "prompt": data["prompt"],
        "text": sonnet["text"],
        "template": sonnet["template"],
        "img": f"log/{l}.png"
      })
      f.seek(0)
      json.dump(j, f, indent=2)
      f.truncate()

    with open(f"log/{l}.png", "xb") as f:
      f.write(png)

    self.social.upload(sonnet["title"], sonnet["text"], png)
    return True

