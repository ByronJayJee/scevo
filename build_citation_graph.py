import requests
import networkx as nx
import matplotlib.pyplot as plt


def create_di_edges_refs(G, pub):
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

pmid_start = "23456789"

response = requests.get(
    "/".join([
        "https://icite.od.nih.gov/api",
        "pubs",
        pmid_start,
    ]),
)
pub = response.json()
print(pub)
print(pub['references'])


# create empty graph
G = nx.DiGraph()
"""
#create an edge betweem the reference pmid and all its references
for ref_pmid in pub['references']:
    print(ref_pmid)
    str_ref_pmid = str(ref_pmid)
    if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)): #directed edge from start to ref
        G.add_edge("".join(pmid_start), "".join(str_ref_pmid))

#create an edge betweem the reference pmid and all articles that cite the ref
for ref_pmid in pub['cited_by']:
    print(ref_pmid)
    str_ref_pmid = str(ref_pmid)
    if not G.has_edge("".join(str_ref_pmid), "".join(pmid_start)):
        G.add_edge("".join(str_ref_pmid), "".join(pmid_start))
"""

G = create_di_edges_refs(G, pub)

print(nx.number_of_nodes(G))
print(nx.number_of_edges(G))
#print(nx.number_connected_components(G))

nx.draw_random(G, with_labels=True)
#draw(G, layout='circo')
plt.show()
