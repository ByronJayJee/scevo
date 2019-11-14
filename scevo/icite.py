"""
  CLI wrapper for the Icite NIH API.  

  - Writes output to a .json file for inspecting.
  - Importable for use by other scripts

Usage:
  icite.py fetch <pmid> [--out=<out> | --verbose]
  icite.py tree <pmid> [--max-depth=<max_depth> | --out=<out> | --verbose]
  icite.py (-h | --help)
  icite.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --max-depth=<max_depth>   Max depth to recurse a publication citation tree [default: 5].
  --out=<out>               The file to dump the json results to [default: icite.json].
  --verbose

"""

import asyncio
import types
import re
import sys
import itertools
import requests
import json
import pprint

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
  # Network Cache handles:
  # 1. cyclical references in the Graph
  # 2. in-memory caching for the entire session
  CACHE      = {}

  @staticmethod
  def log(stuff):
    if ("--verbose" in str(sys.argv)):
      print(stuff)
  
  @staticmethod
  def req(url, param):
    assert isinstance(url, str), "url must be a string: %r" % url
    assert isinstance(param, str), "param must be a string: %r" % param
    prepared_url = url.replace(":param", param)
    Icite.log(":req %r" % prepared_url)
    resp = requests.get(prepared_url)
    # todo: handle non 200 responses
    return resp.json()

  @staticmethod
  def prepare_ids(ids = []):
    assert len(ids) > 0, "cannot prepare empty ids"
    string_ids  = map(lambda id: str(id), ids)
    needs_fetch = filter(lambda id: id not in Icite.CACHE, string_ids)
    return ",".join(needs_fetch)

  # todo: this could be refactored to be a multithreaded divide-and-conquer algorithm
  @staticmethod
  def fetch_by_ids(ids = [], fetched = []):
    if len(ids) == 0: return fetched
    # icite api is limited to 100 ids per batch
    # so we slice this first batch
    this_batch = ids[0:99]
    # and store the next window to keep recursively fetching
    # as necessary
    next_batch    = ids[100:-1]
    newly_fetched = Icite.req(Icite.BATCH_URL, param = Icite.prepare_ids(this_batch))
    pubs          = newly_fetched[Icite.BATCH_KEY]
    for pub in pubs: Icite.CACHE.update({pub["pmid"]: pub})
    return Icite.fetch_by_ids(next_batch, fetched + pubs)

  @staticmethod
  def fetch_by_id(id):
    return Icite.fetch_by_ids([id])[0]

  # used to lazily reconstruct a tree task to keep memory complexity down
  @staticmethod
  def backfill(ids, table = {}):
    for id in ids:
      if id in Icite.CACHE: table.update({id: Icite.CACHE[id]})
    return table

  @staticmethod
  def fetch_citation_tree(ids=[], fetched=[], depth=0, max_depth= 5):
    # maybe a dead branch on the tree
    if len(ids) == 0: return Icite.backfill(fetched)
    # fetch all ids at this depth
    pubs = Icite.fetch_by_ids(ids)
    fetched = fetched + ids
    if depth >= max_depth: return Icite.backfill(fetched)
    pubs_citations = map(lambda resp: resp[Icite.CITED_BY], pubs)
    next_level = list(itertools.chain.from_iterable(pubs_citations))
    return Icite.fetch_citation_tree(ids=next_level, fetched=fetched, depth=depth + 1, max_depth=max_depth)

# currently this loads the test id pub tree to a depth of 5 in ~2.3m
if __name__ == "__main__":
  from docopt import docopt
  argv = docopt(__doc__, version='NIH Icite 1.0')
  pmid = [argv["<pmid>"]]
  fetched = None
  # handle all operations cases
  if argv["fetch"]: 
    fetched = Icite.fetch_by_ids(pmid)
  if argv["tree"]:  
    fetched = Icite.fetch_citation_tree(ids=pmid, max_depth=int(argv["--max-depth"]))

  results = {"length": len(fetched), "data": fetched}

  if argv["--verbose"]:
    with open(argv["--out"], 'w') as outfile:
      json.dump(results, outfile, indent=2)
    print(":saved %r" % argv["--out"])

  else:
    print(json.dump(results, sys.stdout, indent=2))