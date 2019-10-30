from scevo import build_citation_graph as bcg
import matplotlib.pyplot as plt
import networkx as nx

pmids_of_interest = [23456790, 23456791]
max_crawl_depth=1

pub_dict = {}

# create empty graph
G = nx.DiGraph()

for root_pmid in pmids_of_interest:
    pub, pub_dict = bcg.pub_grab(root_pmid, pub_dict)
    G, pub_dict = bcg.create_di_edges_refs(G, pub, pub_dict, max_crawl_depth=max_crawl_depth)
    G, pub_dict = bcg.create_di_edges_citeby(G, pub, pub_dict, max_crawl_depth=max_crawl_depth)

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
