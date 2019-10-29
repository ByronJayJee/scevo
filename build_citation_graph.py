import requests
import networkx as nx

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
G = nx.Graph()

#create an edge betweem the reference pmid and all its references
for ref_pmid in pub['references']:
    print(ref_pmid)
    str_ref_pmid = str(ref_pmid)
    if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)):
        G.add_edge("".join(pmid_start), "".join(str_ref_pmid))

#create an edge betweem the reference pmid and all articles that cite the ref
for ref_pmid in pub['cited_by']:
    print(ref_pmid)
    str_ref_pmid = str(ref_pmid)
    if not G.has_edge("".join(pmid_start), "".join(str_ref_pmid)):
        G.add_edge("".join(pmid_start), "".join(str_ref_pmid))

print(nx.number_of_nodes(G))
print(nx.number_of_edges(G))
print(nx.number_connected_components(G))
