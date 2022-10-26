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

  def __init__(self, keys_path="keys.json", templates_path="templates.json", log_path="log"):
    with open(keys_path, "rb") as f:
      self.keys = json.load(f)
    with open(templates_path, "rb") as f:
      self.templates = json.load(f)
    self.render = Render(self.templates, debug=True)
    self.social = Social(self.keys)
    self.log_path = log_path

  def template_list(self):
    '''
    List of all template names
    '''
    return list(self.templates.keys())

  def gen_sonnets(self, title, prompt):
    '''
    Generate sonnets using GPT, returning a dict with sonnet data
    '''
    title = title.strip()
    prompt = prompt.lstrip()
    if title and prompt:
      if prompt.rstrip().endswith(":"):
        prompt = prompt.rstrip() + "\n\n"
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
    sonnet = data["sonnets"][idx]
    png = Render.encode(sonnet["image"], "png")
    os.makedirs(self.log_path, exist_ok=True)
    try:
      with open(self.log_path + "/log.json", "x") as f:
        f.write("[]")
    except FileExistsError:
      pass

    with open(self.log_path + "/log.json", "r+") as f:
      j = json.load(f)
      l = len(j)
      j.append({
        "title": sonnet["title"],
        "prompt": data["prompt"],
        "text": sonnet["text"],
        "template": sonnet["template"],
        "img": f"{l}.png"
      })
      f.seek(0)
      json.dump(j, f, indent=2)
      f.truncate()

    with open(f"{self.log_path}/{l}.png", "xb") as f:
      f.write(png)

    return self.social.upload(sonnet["title"], sonnet["text"], png)

