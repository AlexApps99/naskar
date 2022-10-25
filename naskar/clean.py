def clean(gpt):
  """
  takes output from OpenAI and cleans and filters for valid sonnets
  """
  # half-finished sonnets are no good, and if it isn't finished it's too long
  sonnets = [s["text"] for s in gpt["choices"] if s["finish_reason"] == "stop"]
  # strip each line
  sonnets = ["\n".join([l.strip() for l in s.splitlines()]) for s in sonnets]
  # split into stanzas
  sonnets = [[q.strip() for q in s.split("\n\n") if q.strip()] for s in sonnets]
  # split stanzas into lines
  sonnets = [[q.split("\n") for q in s] for s in sonnets]

  def validate_sonnet(sonnet):
    # Too few/many stanzas
    if len(sonnet) < 3 or len(sonnet) > 5: return False
    for stanza in sonnet:
      # Stanza is too long
      if len(stanza) > 4: return False
    # It's probably good enough
    return True

  def regroup_sonnet(sonnet, n):
    i = 0
    while i < len(sonnet) - 1:
      while (i < len(sonnet) - 1) and len(sonnet[i]) + len(sonnet[i+1]) <= n:
        sonnet[i:i+2] = [sonnet[i] + sonnet[i+1]]
      i += 1
    return sonnet

  # merge stanzas together until there would be more than 4 (or 3) lines per stanza
  for sonnet in sonnets:
    old_sonnet = sonnet.copy()
    sonnet = regroup_sonnet(sonnet, 4)
    if not validate_sonnet(sonnet):
      print(old_sonnet)
      sonnet = regroup_sonnet(old_sonnet, 3)

  return ["\n\n".join(["\n".join(q) for q in s]) for s in sonnets if validate_sonnet(s)]
