# -*- coding: utf-8 -*-
"""
Code to create rdf:type links from ABOX to TBOX
Input: 
    interim parquet files from run of B2 code
    save path
Output: rdf file of ABOX links (output_link.rdf)
"""
#=============================================================================# 
#                              PRELIMINARIES                                  # 
#=============================================================================# 

import pandas as pd
import os
from rdflib import Graph, Namespace, URIRef, RDF, XSD, RDFS

# Folder to save all output
savefolder='../output'

os.chdir(savefolder)

#=============================================================================# 
#                                READ DATA                                    # 
#=============================================================================# 

for df in ['conference','journal','volume','proceeding','paper']:
    globals()[df]=pd.read_pickle(f"interim_{df}.pkl")

#=============================================================================# 
#                               DEFINE GRAPH                                  # 
#=============================================================================# 

# Set up graph
g = Graph()
sdm = Namespace('http://example.org/sdm#')

g.bind("sdm", sdm)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("rdf", RDF)

NS = {
    'sdm': sdm,
    'rdf': RDF,
    'rdfs': RDFS,
    'xsd':XSD,
}

#=============================================================================# 
#                                DEFINE LINKS                                 # 
#=============================================================================# 

def link_conference_to_rdf(df):
    """
    Concepts: Conference type, Chair
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Conference_" + str(row['conference']))
        author_org=URIRef(sdm + "Author_" + str(row['organizer']))
        conf_type={'expert group':sdm.ExpertGroup, 'symposium':sdm.Symposium, 
                   'workshop':sdm.Workshop, 'regular':sdm.RegularConference}[row['type']]
        g.add((id, RDF.type, conf_type))
        g.add((author_org, RDF.type, sdm.Chair))
        
    print('Link done: Conference')

def link_journal_to_rdf(df):
    """
    Concepts: Journal, Editor
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Journal_" + str(row['journal']))
        author_org=URIRef(sdm + "Author_" + str(row['organizer']))
        g.add((id, RDF.type, sdm.Journal))
        g.add((author_org, RDF.type, sdm.Editor))
        
    print('Link done: Journal')

def link_volume_to_rdf(df):
    """
    Concepts: Volume
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Volume_" + str(row['volume']).replace(' ','_'))
        g.add((id, RDF.type, sdm.Volume))

    print('Link done: Volume')
    
def link_proceeding_to_rdf(df):
    """
    Concepts: Proceeding
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Proceeding_" + str(row['proceeding']))
        g.add((id, RDF.type, sdm.Proceeding)) 

    print('Link done: Proceeding')
        
def link_paper_to_rdf(df):
    """
    Concepts: Paper type
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Paper_" + str(row['paper']))
        paper_type={'demo':sdm.DemoPaper, 'full':sdm.FullPaper, 'short':sdm.ShortPaper, 'poster':sdm.Poster}[row['type']]
        g.add((id,RDF.type, paper_type))

    print('Link done: Paper')
        
#==============================================================================  IMPLEMENTATION

print("/=============================/")
print('/       GENERATE LINKS        /')
print("/=============================/")

# Call functions
link_conference_to_rdf(conference)
link_journal_to_rdf(journal)
link_volume_to_rdf(volume)
link_proceeding_to_rdf(proceeding)
link_paper_to_rdf(paper)

#=============================================================================# 
#                                EXPORT LINK                                  # 
#=============================================================================# 
g.serialize(destination='output_link.rdf',format="xml")