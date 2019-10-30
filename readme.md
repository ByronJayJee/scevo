scevo: (Sc)ience (Evo)lution
============================

scevo is an open-source Python library that builds citation graphs of scientific journal articles then analyzes the text of these articles to analyze the evolution of scientific ideas.

Citation graphs are currently built using the [NetworkX](https://github.com/networkx/networkx) Python package and the [iCite](https://icite.od.nih.gov/) web API.

Text analysis using Natural Language Processing is currently under development. 

Installation
============

Scevo works with Python 3. Scevo has been developed/tested on Windows but may work on Linux or Mac systems. 

You can clone scevo directly from GitHub and install the appropriate conda environment with:

    git clone https://github.com/ByronJayJee/scevo.git
    cd scevo
    conda env create -f environment.yml
    
