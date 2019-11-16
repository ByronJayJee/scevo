from scevo import build_citation_graph as bcg
from scevo import text_abstract_nlp as tan
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

#pmids_of_interest = [23456790, 23456791]
pmids_of_interest = [23456790]
max_crawl_depth=2

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

nx.write_graphml(G, 'pmid_graph.sav')

#######################################################

pmids_of_interest = G.nodes()
pmids_of_interest = [int(i) for i in pmids_of_interest]

#pmids_of_interest = [23456789, 23456790, 23456791, 23456793]

print('pmids_of_interest')
print(pmids_of_interest)

abstract_dict = {}


for root_pmid in pmids_of_interest:
    abstract_dict = tan.pub_xml_abstract_grab(root_pmid, abstract_dict)

print(abstract_dict)

dictlist = []

for key, value in abstract_dict.items():
    temp_str = ''.join(str(value))
    dictlist.append(temp_str)

print(dictlist)

tf = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df = 0, stop_words = 'english')
tfidf_matrix =  tf.fit_transform(dictlist)

feature_names = tf.get_feature_names()
print(len(feature_names))

print(feature_names[50:70])

dense = tfidf_matrix.todense()

temp_arr = dense[0].tolist()[0]
print(temp_arr)
print(len(temp_arr))

pca = PCA()
pca.fit(dense)
pca_score = pca.explained_variance_ratio_

print('pca_score')
print(pca_score)

score_cum = []

tmp_pca = 0.0
for idx in range(len(pca_score)):
    tmp_pca = tmp_pca + pca_score[idx]
    score_cum.append(tmp_pca)

print('score_cum')
print(score_cum)

#######################################################

fig, ax = plt.subplots(figsize=(35, 8))

#nx.draw(G, pos=pub_dict, with_labels=True, ax=ax)
###nx.draw_networkx(G, pos=pub_dict, with_labels=True, ax=ax)
#nx.draw_spectral(G, pos=nx.spring_layout(G), with_labels=True)
#nx.draw_planar(G, with_labels=True)
#nx.draw_spring(G, with_labels=True)
#nx.draw_circular(G, with_labels=True)
#draw(G, layout='circo')

ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

#plt.show()
