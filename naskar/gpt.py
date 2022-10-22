import openai

def complete(prompt, key=None):
  """
  Uses OpenAI to complete a prompt with multiple outputs
  """
  if key: openai.api_key = key
  return openai.Completion.create(
    model="text-davinci-002",
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
    frequency_penalty=0,
    presence_penalty=0,
    n=4,
    #best_of=4,
  )

