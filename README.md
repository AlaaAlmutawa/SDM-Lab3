# Lab3: Knowledge Graphs
- In partial fulfillment of Semantic Data Management Course, Universitat Politècnica de Catalunya
- Authors: Adina Bondoc, Alaa Almutawa, You Xu
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
There are 3 ways to generate
1. Separate TBOX and ABOX files: 
    - Run *abox_gen* and *tbox_gen*. This should generate the following output in the output folder: *output_abox.rdf* and *output_abox.rdf*
    - In GraphDB, import these two files and load into a graph, with ruleset **OWLRL (Optimized)**
2. Combined TBOX and ABOX file
    - Run *tbox_abox_gen* and this should generate the following output in the output folder: *output_graph_inference.rdf*
    - In GraphDB, import this file and load into a graph, with ruleset **RDFS Plus (Optimized)**
    - Note: python code makes use of the owlrl library to activate inference via RDFS Closure before saving into xml

Definition |	Inference Ruleset	|	Code (Group-*-AlmutawaBondocXu.py)	|	Output (.rdf)
--- | --- | --- | --- 
TBOX and ABOX separately	|	During import into GraphDB (RDFS)	|	B1, B2-B3	|	output_tbox, output_abox
TBOX, ABOX Instances, and RDF type links separately	|	During import into GraphDB (RDFS)	|	B1, B2, B3	|	output_tbox, output_abox, output_links
TBOX and ABOX in same file	|	Before importing to GraphDB via Python RDFLib Library (RDFS Closure)	|	B	|	output_graph_inference
