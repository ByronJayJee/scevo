"""
  CLI wrapper for the Icite NIH API.  

  - Writes output to a .json file for inspecting.
  - Importable for use by other scripts

Usage:
  icite.py fetch <pmid> [--out=<out>]
  icite.py tree <pmid> [--max-depth=<max_depth>, --verbose]
  icite.py (-h | --help)
  icite.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --max-depth=<max_depth>   Max depth to recurse a publication citation tree [default: 5].
  --out=<out>               The file to dump the json results to [default: icite.json].
  --verbose

"""
import multiprocessing as mp
import types
import re
import sys
import itertools
import requests
import json
from list import List

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
  def prepare_ids(ids = [], cache={}):
    assert len(ids) > 0, "cannot prepare empty ids"
    string_ids  = map(lambda id: str(id), ids)
    needs_fetch = filter(lambda id: id not in cache, string_ids)
    return ",".join(needs_fetch)

  @staticmethod
  def fetch_ids_pure(ids = [], cache={}):
    if len(ids) == 0: return []
    newly_fetched = Icite.req(Icite.BATCH_URL, 
      param=Icite.prepare_ids(ids, cache))
    return newly_fetched[Icite.BATCH_KEY]

  @staticmethod
  def fetch_ids_parallel(ids = [], cache={}, results=[]):
    worker_pool = mp.Pool(mp.cpu_count())
    for batch in List.chunk(ids, 100):
      worker_pool.apply_async(Icite.fetch_ids_pure, 
        args=(batch, cache),
        callback=lambda result: results.append(result))
    worker_pool.close()
    worker_pool.join()
    return List.flatten(results)
    

  @staticmethod
  def fetch_by_id(id):
    return Icite.fetch_ids_pure([id])[0]

  @staticmethod
  def fetch_citation_tree(ids=[], fetched={}, depth=0, max_depth= 5):
    # maybe a dead branch on the tree
    if len(ids) == 0: return fetched
    # fetch all ids at this depth
    pubs = Icite.fetch_ids_parallel(ids, cache=fetched)
    for pub in pubs: fetched.update({pub["pmid"]: pub})
    if depth >= max_depth: return fetched
    pubs_citations = map(lambda resp: resp[Icite.CITED_BY], pubs)
    next_level = List.flatten(pubs_citations)
    return Icite.fetch_citation_tree(ids=next_level, 
                                     fetched=fetched, 
                                     depth=depth+1, 
                                     max_depth=max_depth)

# currently this loads the test id pub tree to a depth of 5 in ~2.3m
if __name__ == "__main__":
  from docopt import docopt
  argv = docopt(__doc__, version='NIH Icite 1.0')
  pmid = [argv["<pmid>"]]
  results = None
  # handle all operations cases
  if argv["fetch"]: 
    results = Icite.fetch_by_id(pmid)
  if argv["tree"]:  
    results = Icite.fetch_citation_tree(ids=pmid, max_depth=int(argv["--max-depth"]))
    results = {"length": len(results), "data": results}

  if argv["--verbose"]:
    with open(argv["--out"], 'w') as outfile:
      json.dump(results, outfile, indent=2)
    print(":saved %r" % argv["--out"])

  else:
    print(json.dump(results, sys.stdout, indent=2))