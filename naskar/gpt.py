import requests

def complete(prompt, key):
  """
  Uses OpenAI to complete a prompt with multiple outputs
  """
  r = requests.post("https://api.openai.com/v1/completions", headers={
    "Authorization": f"Bearer {key}"
  }, json={
    "model": "text-davinci-002",
    "prompt": prompt,
    "temperature": 0.7,
    "max_tokens": 256,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "n": 4,
    #"best_of": 4,
  })
  r.raise_for_status()
  return r.json()

