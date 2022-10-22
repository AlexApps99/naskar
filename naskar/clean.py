def clean(gpt):
  """
  takes output from OpenAI and cleans and filters for valid sonnets
  """
  # half-finished sonnets are no good, and if it isn't finished it's too long
  sonnets = [s["text"].strip() for s in gpt["choices"] if s["finish_reason"] == "stop"]

  # TODO clean up line breaks for sonnets
  # TODO discard sonnets with bad structure

  return sonnets
