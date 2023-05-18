# Lab3: Knowledge Graphs
- In partial fulfillment of Semantic Data Management Course, Universitat Politècnica de Catalunya
- Authors: Alaa Almutawa, Adina Bondoc, You Xu
- Supervised by: Prof. Oscar Romero, Prof. Javier Flores

## Description
This repository contains code for generating the TBOX, ABOX, and queries for a knowledge graph of scholarly articles submitted to and published in conferences and journals.

## Set up
To run this, the root directory must have the following folders:
1. data: this folder will contain all the initial csv files of data generated from SDM Lab 1 of Bondoc and Ganepola
2. output: this is where all rdf files will be saved to

Required python libraries:
- rdflib
- owlrl
- Faker

## How to run
There are 3 ways to generate a working graph in GraphDB, as illustrated in the table below:

Definition |	Inference Ruleset	|	Code (Group-*-AlmutawaBondocXu.py)	|	Output (.rdf)
--- | --- | --- | --- 
TBOX and ABOX separately	|	During import into GraphDB (RDFS)	|	B1, B2-B3	|	output_tbox, output_abox
TBOX, ABOX Instances, and RDF type links separately	|	During import into GraphDB (RDFS)	|	B1, B2, B3	|	output_tbox, output_abox, output_links
TBOX and ABOX in same file	|	Before importing to GraphDB via Python RDFLib Library (RDFS Closure)	|	B	|	output_graph_inference

Inference ruleset pertains to when inference is activated. There are two cases: 
1. During import into GraphDB in which inference must be turned on and the ruleset chosen must be RDFS, 
2. Before importing into GraphDB and during TBOX and ABOX creation via Python's RDFLibrary. Before saving as a xmd file, RDFS Closure via the owlrl library is called to generate inferred triples.

## SPARQL queries
In folder ```/query```, there are 6 SPARQL queries to explore the database. They can:
- Find all Authors by executing ```query1```
- Find all properties whose domain is specifically only Author, not including the inherited properties from its superclass by executing ```query2_case1```
- Find all properties whose domain is Author and its superclasses, which includes the inherited properties by executing ```query2_case2```
- Find all properties whose domain is specifically either Conference or Journal. not including the inherited properties from their superclasses by executing ```query3_case1```
- Find all properties whose domain is Conference or Journal, and their superclasses, which includes the inherited properties by executing ```query3_case2```
- Find all the papers written by a Yunpeng Liu that where published in database conferences by executing ```query4```
