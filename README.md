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
There are 2 ways to generate
1. Separate TBOX and ABOX files: 
    - Run *abox_gen* and *tbox_gen*. This should generate the following output in the output folder: *output_abox.rdf* and *output_abox.rdf*
    - In GraphDB, import these two files and load into a graph, with ruleset **OWLRL (Optimized)**
2. Combined TBOX and ABOX file
    - Run *tbox_abox_gen* and this should generate the following output in the output folder: *output_graph_inference.rdf*
    - In GraphDB, import this file and load into a graph, with ruleset **RDFS Plus (Optimized)**
    - Note: python code makes use of the owlrl library to activate inference via RDFS Closure before saving into xml

Note: In the code folder, codes are made available in both .py and jupyter notebook format but in general have the same content so running in either format should give the same output.
