import requests
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import time

from random import random

import json
import sys

import xml.etree.ElementTree as ET

from sklearn.feature_extraction.text import TfidfVectorizer


def pub_xml_abstract_grab(pmid=23456789, abstract_dict={}):


    time.sleep(0.5)

    pmid_str = str(pmid)

    # sample URL:
    #https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23456789&tool=my_tool&email=my_email@example.com&rettype=abstract

    url_str_pre="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
    url_str_post="&tool=scevo&email=my_email@example.com&rettype=abstract"

    req_url = url_str_pre + pmid_str + url_str_post

    response = requests.get(req_url)

    print('\nPMID %d All attributes:' % (pmid))
    temp_res_str = response.text.encode("utf-8")
    #print(temp_res_str)
    #print(response.text)

    #root = ET.fromstring(response.text)
    root = ET.fromstring(temp_res_str)

    # all item attributes
    for elem in root:
        abstract_str = ''
        #abstract_text=elem.findall("MedlineCitation/Article/Abstract/AbstractText")
        abstract_text_elem=elem.findall("MedlineCitation/Article/Abstract/AbstractText")
        print(abstract_text_elem)
        for res in abstract_text_elem:
            temp_res_str2 = str(ET.tostring(res))
            '''
            print('\ntemp_res_str2')
            print(temp_res_str2)
            print('\ntemp_res_str2.encode("utf-8")')
            print(temp_res_str2.encode("utf-8"))
            '''
            #print('\nres')
            #print(res)
            #print('\nres.text.encode("utf-8")')
            #print(res.text.encode("utf-8"))
            #abstract_str = abstract_str + ' ' + res.text
            abstract_str = abstract_str + ' ' + str(temp_res_str2.encode("utf-8"))
            #print(res.text)
        '''
        print('\n')
        print(elem.tag, elem.attrib)
        for subelem in elem:
            print('--: ',subelem.tag, subelem.attrib)
            for subsubelem in subelem:
                print('----: ',subsubelem.tag, subsubelem.attrib)
       '''
    #print('abstract_str')
    #print(abstract_str)

    abstract_dict[pmid_str] = abstract_str

    #print(pub_dict)

    #print(pub)
    #print(pub['references'])
    return abstract_dict

if __name__ == "__main__":
    pmids_of_interest = [23456789, 23456790, 23456791, 23456793]
    #pmids_of_interest = [23456789]

    abstract_dict = {}

    # create empty graph
    #G = nx.DiGraph()

    for root_pmid in pmids_of_interest:
        abstract_dict = pub_xml_abstract_grab(root_pmid, abstract_dict)

    print(abstract_dict)

    dictlist = []

    for key, value in abstract_dict.items():
        temp = [key,value]
        #dictlist.append(temp)
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

