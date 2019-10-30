import requests
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from random import random

import json
import sys

def create_di_edges_all(G, pub):
    #create an edge betweem the reference pmid and all its references
    pmid_start=str(pub["pmid"])
    for ref_pmid in pub['references']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)): #directed edge from start to ref
            G.add_edge("".join(pmid_start), "".join(str_ref_pmid))

    #create an edge betweem the reference pmid and all articles that cite the ref
    for ref_pmid in pub['cited_by']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(str_ref_pmid), "".join(pmid_start)):
            G.add_edge("".join(str_ref_pmid), "".join(pmid_start))
    return G

def create_di_edges_refs(G, pub, pub_dict, current_depth=1, max_crawl_depth=1):
    #create an edge betweem the reference pmid and all its references
    pmid_start=str(pub["pmid"])
    for ref_pmid in pub['references']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)): #directed edge from start to ref
            G.add_edge("".join(pmid_start), "".join(str_ref_pmid))
            _, pub_dict = pub_grab(ref_pmid, pub_dict)
        if (current_depth < max_crawl_depth):
            tmp_pub, pub_dict = pub_grab(ref_pmid, pub_dict)
            G, pub_dict = create_di_edges_refs(G, tmp_pub, pub_dict, current_depth+1, max_crawl_depth)
    return G, pub_dict

def create_di_edges_citeby(G, pub, pub_dict, current_depth=1, max_crawl_depth=1):
    #create an edge betweem the reference pmid and all its references
    pmid_start=str(pub["pmid"])
    #create an edge betweem the reference pmid and all articles that cite the ref
    for ref_pmid in pub['cited_by']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(str_ref_pmid), "".join(pmid_start)):
            G.add_edge("".join(str_ref_pmid), "".join(pmid_start))
            _, pub_dict = pub_grab(ref_pmid, pub_dict)
        if (current_depth < max_crawl_depth):
            tmp_pub, pub_dict = pub_grab(ref_pmid, pub_dict)
            G, pub_dict = create_di_edges_refs(G, tmp_pub, pub_dict, current_depth+1, max_crawl_depth)
    return G, pub_dict

def pub_grab(pmid=23456789, pub_dict={}):

    pmid_str = str(pmid)

    response = requests.get(
        "/".join([
            "https://icite.od.nih.gov/api",
            "pubs",
            pmid_str,
        ]),
    )

    pub = response.json()

    pub_dict[pmid_str] = np.array([pub['year'], random()*2019])
    #pub_dict[pmid] = pub

    #print(pub_dict)

    #print(pub)
    #print(pub['references'])
    return pub, pub_dict


if __name__ == "__main__":
    pmids_of_interest = [23456789, 23456790, 23456791, 23456793]
    #pmids_of_interest = [23456789]
    max_crawl_depth=1

    pub_dict = {}

    # create empty graph
    G = nx.DiGraph()

    for root_pmid in pmids_of_interest:
        pub, pub_dict = pub_grab(root_pmid, pub_dict)
        G, pub_dict = create_di_edges_refs(G, pub, pub_dict, max_crawl_depth=max_crawl_depth)
        G, pub_dict = create_di_edges_citeby(G, pub, pub_dict, max_crawl_depth=max_crawl_depth)

    print(nx.number_of_nodes(G))
    print(nx.number_of_edges(G))
    #print(nx.number_connected_components(G))

    print("G.nodes()")
    print(G.nodes())

    fig, ax = plt.subplots(figsize=(35, 8))

    #nx.draw(G, pos=pub_dict, with_labels=True, ax=ax)
    nx.draw_networkx(G, pos=pub_dict, with_labels=True, ax=ax)
    #nx.draw_spectral(G, pos=nx.spring_layout(G), with_labels=True)
    #nx.draw_planar(G, with_labels=True)
    #nx.draw_spring(G, with_labels=True)
    #nx.draw_circular(G, with_labels=True)
    #draw(G, layout='circo')

    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    plt.show()
