"""
  CLI wrapper for the Icite NIH API.  

  - Writes output to a .json file for inspecting.
  - Importable for use by other scripts

Usage:
  icite.py fetch <pmid> [--out=<out>]
  icite.py tree <pmid> [--max-depth=<max_depth> | --out=<out>]
  icite.py (-h | --help)
  icite.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --max-depth=<max_depth>   Max depth to recurse a publication citation tree [default: 5].
  --out=<out>               The file to dump the json results to [default: icite.json].

"""
from docopt import docopt
import types
import re
import itertools
import requests
import json

class Icite:
  #
  # ref: https://icite.od.nih.gov/api
  #
  # single url for reference
  SINGLE_URL = "https://icite.od.nih.gov/api/pubs/:param"
  # batch url is more effective because it can respond with 1-100 publications paginated
  BATCH_URL  = "https://icite.od.nih.gov/api/pubs?pmids=:param"
  # used to unpack batch responses
  BATCH_KEY  = "data"
  # the key where a publications citation tree lives
  CITED_BY   = "cited_by"
 
  def __init__(self):
    # Network Cache handles:
    # 1. cyclical references in the Graph
    # 2. in-memory caching for the entire session
    self.cached = {}

  def fetch(self, url, param):
    assert isinstance(url, str), "url must be a string: %r" % url
    assert isinstance(param, str), "param must be a string: %r" % param
    prepared_url = url.replace(":param", param)
    print(":fetch %r" % prepared_url)
    resp = requests.get(prepared_url)
    # todo: handle non 200 responses
    return resp.json()

  def prepare_ids(self, ids = []):
    assert len(ids) > 0, "cannot prepare empty ids"
    string_ids  = map(lambda id: str(id), ids)
    needs_fetch = filter(lambda id: id not in self.cached, string_ids)
    return ",".join(needs_fetch)

  # todo: this could be refactored to be a multithreaded divide-and-conquer algorithm
  def ids(self, ids = [], fetched = []):
    if len(ids) == 0: return fetched
    # icite api is limited to 100 ids per batch
    # so we slice this first batch
    this_batch = ids[0:99]
    # and store the next window to keep recursively fetching
    # as necessary
    next_batch    = ids[100:-1]
    newly_fetched = self.fetch(Icite.BATCH_URL, param = self.prepare_ids(this_batch))
    pubs          = newly_fetched[Icite.BATCH_KEY]
    for pub in pubs: self.cached.update({pub["pmid"]: pub})
    return self.ids(next_batch, fetched + pubs)

  def id(self, id):
    return self.ids([id])[0]

  # used to lazily reconstruct a tree task to keep memory complexity down
  def load(self, ids, table = {}):
    for id in ids:
      if id in self.cached: table.update({id: self.cached[id]})
    return table

  def tree(self, ids=[], fetched=[], depth=0, max_depth= 5):
    # maybe a dead branch on the tree
    if len(ids) == 0: return self.load(fetched)
    # fetch all ids at this depth
    pubs = self.ids(ids)
    fetched = fetched + ids
    if depth >= max_depth: return self.load(fetched)
    pubs_citations = map(lambda resp: resp[Icite.CITED_BY], pubs)
    next_level = list(itertools.chain.from_iterable(pubs_citations))
    return self.tree(ids=next_level, fetched=fetched, depth=depth + 1, max_depth=max_depth)

# currently this loads the test id pub tree to a depth of 5 in ~2.3m
if __name__ == "__main__":
  argv = docopt(__doc__, version='NIH Icite 1.0')
  pmid = [argv["<pmid>"]]
  icite = Icite()
  fetched = None
  # handle all operations cases
  if argv["fetch"]: 
    fetched = icite.ids(pmid)
  if argv["tree"]:  
    fetched = icite.tree(ids=pmid, max_depth=int(argv["--max-depth"]))

  with open(argv["--out"], 'w') as outfile:
    json.dump({"length": len(fetched), "data": fetched}, outfile, indent=2)