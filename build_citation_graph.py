import requests
import networkx as nx
import matplotlib.pyplot as plt


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

def create_di_edges_refs(G, pub, current_depth=1, max_crawl_depth=1):
    #create an edge betweem the reference pmid and all its references
    pmid_start=str(pub["pmid"])
    for ref_pmid in pub['references']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)): #directed edge from start to ref
            G.add_edge("".join(pmid_start), "".join(str_ref_pmid))
        if (current_depth < max_crawl_depth):
            tmp_pub=pub_grab(ref_pmid)
            G = create_di_edges_refs(G, tmp_pub, current_depth+1, max_crawl_depth)
    return G

def create_di_edges_citeby(G, pub, current_depth=1, max_crawl_depth=1):
    #create an edge betweem the reference pmid and all its references
    pmid_start=str(pub["pmid"])
    #create an edge betweem the reference pmid and all articles that cite the ref
    for ref_pmid in pub['cited_by']:
        #print(ref_pmid)
        str_ref_pmid = str(ref_pmid)
        if not G.has_edge("".join(str_ref_pmid), "".join(pmid_start)):
            G.add_edge("".join(str_ref_pmid), "".join(pmid_start))
        if (current_depth < max_crawl_depth):
            tmp_pub=pub_grab(ref_pmid)
            G = create_di_edges_refs(G, tmp_pub, current_depth+1, max_crawl_depth)
    return G

def pub_grab(pmid=23456789):

    pmid_str = str(pmid)

    response = requests.get(
        "/".join([
            "https://icite.od.nih.gov/api",
            "pubs",
            pmid_str,
        ]),
    )
    pub = response.json()
    #print(pub)
    print(pub['references'])
    return pub

pub = pub_grab()


# create empty graph
G = nx.DiGraph()

#G = create_di_edges_all(G, pub)
G = create_di_edges_refs(G, pub, max_crawl_depth=2)
G = create_di_edges_citeby(G, pub, max_crawl_depth=2)

print(nx.number_of_nodes(G))
print(nx.number_of_edges(G))
#print(nx.number_connected_components(G))

nx.draw_circular(G, with_labels=True)
#draw(G, layout='circo')
plt.show()
