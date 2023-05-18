# -*- coding: utf-8 -*-
"""
Code to create TBOX independently of ABOX.
Input: 
    save path
Output: rdf file of TBOX (output_tbox.rdf)
"""

#=============================================================================# 
#                              PRELIMINARIES                                  # 
#=============================================================================# 

# Install libraries
# !pip install rdflib
# !pip install owlrl

import os
from rdflib import Graph, Namespace, RDF, RDFS, XSD

# Folder to save all output
savefolder='../output'

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
#                                DEFINE TBOX                                  # 
#=============================================================================# 

#==============================================================================  CONCEPTS
# Author concept 
g.add((sdm.Author,RDFS.subClassOf, sdm.Person))
# Organizer concept
g.add((sdm.Organizer,RDFS.subClassOf, sdm.Author))
# Chair concept
g.add((sdm.Chair,RDFS.subClassOf, sdm.Organizer))
# Editor concept
g.add((sdm.Editor,RDFS.subClassOf, sdm.Organizer))

# Demo Paper concept 
g.add((sdm.DemoPaper,RDFS.subClassOf, sdm.Paper))

# Full Paper concept 
g.add((sdm.FullPaper,RDFS.subClassOf, sdm.Paper))

# Short Paper concept 
g.add((sdm.ShortPaper,RDFS.subClassOf, sdm.Paper))

# Poster concept 
g.add((sdm.Poster,RDFS.subClassOf, sdm.Paper))

# Proceeding concept 
g.add((sdm.Proceeding,RDFS.subClassOf, sdm.Publication))

# Volume concept 
g.add((sdm.Volume,RDFS.subClassOf, sdm.Publication))

# Journal concept 
g.add((sdm.Journal,RDFS.subClassOf, sdm.Venue))

# Conference concept 
g.add((sdm.Conference,RDFS.subClassOf, sdm.Venue))

# Workshop concept 
g.add((sdm.Workshop,RDFS.subClassOf, sdm.Conference))

# Regular Conference concept 
g.add((sdm.RegularConference,RDFS.subClassOf, sdm.Conference))

# Regular Conference concept 
g.add((sdm.RegularConference,RDFS.subClassOf, sdm.Conference))

# Synposium concept 
g.add((sdm.Symposium,RDFS.subClassOf, sdm.Conference))

# Expert Group concept 
g.add((sdm.ExpertGroup,RDFS.subClassOf, sdm.Conference))


#==============================================================================  PROPERTIES
# Range is Author 
# hasAuthor property
g.add((sdm.hasAuthor,RDFS.domain, sdm.Paper))
g.add((sdm.hasAuthor,RDFS.range, sdm.Author))

# hasReviewer
g.add((sdm.hasReviewer,RDFS.domain, sdm.Review))
g.add((sdm.hasReviewer,RDFS.range, sdm.Author))

# Range is Organizer 
# assignedBy property 
g.add((sdm.assignedBy,RDFS.domain, sdm.Submission))
g.add((sdm.assignedBy,RDFS.range, sdm.Organizer))

# hasOrganizer property 
g.add((sdm.hasOrganizer,RDFS.domain, sdm.Venue))
g.add((sdm.hasOrganizer,RDFS.range, sdm.Organizer))

# Range is Review 
# hasReview property
g.add((sdm.hasReview,RDFS.domain, sdm.Submission))
g.add((sdm.hasReview,RDFS.range, sdm.Review))

# Range is Submission
# includedIn property
g.add((sdm.includedIn,RDFS.domain, sdm.Paper))
g.add((sdm.includedIn,RDFS.range, sdm.Submission))

# Range is Area 
# paperRelatedTo property
g.add((sdm.paperRelatedTo,RDFS.subPropertyOf, sdm.relatedTo))

g.add((sdm.paperRelatedTo,RDFS.domain, sdm.Paper))
g.add((sdm.paperRelatedTo,RDFS.range, sdm.Area))

# Range is Venue
# submittedTo property
g.add((sdm.submittedTo,RDFS.domain, sdm.Submission))
g.add((sdm.submittedTo,RDFS.range, sdm.Venue))

# venueRelatedTo property
g.add((sdm.venueRelatedTo,RDFS.subPropertyOf, sdm.relatedTo))

g.add((sdm.venueRelatedTo,RDFS.domain, sdm.Venue))
g.add((sdm.venueRelatedTo,RDFS.range, sdm.Area))

# publicationRelatedTo property
g.add((sdm.publicationRelatedTo,RDFS.subPropertyOf, sdm.relatedTo))

g.add((sdm.publicationRelatedTo,RDFS.domain, sdm.Publication))
g.add((sdm.publicationRelatedTo,RDFS.range, sdm.Area))

# Range is Publication 
# publishedIn property
g.add((sdm.publishedIn,RDFS.domain, sdm.Paper))
g.add((sdm.publishedIn,RDFS.range, sdm.Publication))

# hasPublished property 
g.add((sdm.hasPublished,RDFS.domain, sdm.Venue))
g.add((sdm.hasPublished,RDFS.range, sdm.Publication))

# Range is Proceeding 
# posterPublishedIn property
g.add((sdm.posterPublishedIn,RDFS.subPropertyOf, sdm.publishedIn))


g.add((sdm.posterPublishedIn,RDFS.domain, sdm.Poster))
g.add((sdm.posterPublishedIn,RDFS.range, sdm.Proceeding))

#==============================================================================  DATA PROPERTIES

## Person concept data properties
## hasPersonName
g.add((sdm.hasPersonName,RDFS.domain, sdm.Person))
g.add((sdm.hasPersonName,RDFS.range, XSD.string))

## hasBirthDate 
g.add((sdm.hasBirthDate,RDFS.domain, sdm.Person))
g.add((sdm.hasBirthDate,RDFS.range, XSD.date))

## hasSex 
g.add((sdm.hasSex,RDFS.domain, sdm.Person))
g.add((sdm.hasSex,RDFS.range, XSD.string))

## originCountry 
g.add((sdm.originCountry,RDFS.domain, sdm.Person))
g.add((sdm.originCountry,RDFS.range, XSD.string))

## Author concept data properties 
## hasHIndex 
g.add((sdm.hasHIndex,RDFS.domain, sdm.Author))
g.add((sdm.hasHIndex,RDFS.range, XSD.float))

## url
g.add((sdm.url,RDFS.domain, sdm.Author))
g.add((sdm.url,RDFS.range, XSD.string))

## affiliatedWithInstitution
g.add((sdm.affiliatedWithInstitution,RDFS.domain, sdm.Author))
g.add((sdm.affiliatedWithInstitution,RDFS.range, XSD.string))


## Review concept data properties 
## decision
g.add((sdm.decision,RDFS.domain, sdm.Review))
g.add((sdm.decision,RDFS.range, XSD.integer))

## content 
g.add((sdm.content,RDFS.domain, sdm.Review))
g.add((sdm.content,RDFS.range, XSD.string))

## reviewDate
g.add((sdm.reviewDate,RDFS.domain, sdm.Review))
g.add((sdm.reviewDate,RDFS.range, XSD.date))

## Submission concept data properties 
## submissionDate
g.add((sdm.submissionDate,RDFS.domain, sdm.Submission))
g.add((sdm.submissionDate,RDFS.range, XSD.date))

## Venue concept data properties
## hasVenueTitle
g.add((sdm.hasVenueTitle,RDFS.domain, sdm.Venue))
g.add((sdm.hasVenueTitle,RDFS.range, XSD.string))

## Conference concept data properties 
## conferenceSeries
g.add((sdm.conferenceSeries,RDFS.domain, sdm.Conference))
g.add((sdm.conferenceSeries,RDFS.range, XSD.string))

## startDate
g.add((sdm.startDate,RDFS.domain, sdm.Conference))
g.add((sdm.startDate,RDFS.range, XSD.date))

## endDate
g.add((sdm.endDate,RDFS.domain, sdm.Conference))
g.add((sdm.endDate,RDFS.range, XSD.date))

## heldIn
g.add((sdm.heldIn,RDFS.domain, sdm.Conference))
g.add((sdm.heldIn,RDFS.range, XSD.string))

## heldInYear
g.add((sdm.heldInYear,RDFS.domain, sdm.Conference))
g.add((sdm.heldInYear,RDFS.range, XSD.integer))

## Publication concept data properties
## publicationIssn
g.add((sdm.publicationIssn,RDFS.domain, sdm.Publication))
g.add((sdm.publicationIssn,RDFS.range, XSD.string))

## publisher 
g.add((sdm.publisher,RDFS.domain, sdm.Publication))
g.add((sdm.publisher,RDFS.range, XSD.string))

## publishedDate
g.add((sdm.publishedDate,RDFS.domain, sdm.Publication))
g.add((sdm.publishedDate,RDFS.range, XSD.date))

## Paper concept data properties 
## paperTitle
g.add((sdm.paperTitle,RDFS.domain, sdm.Paper))
g.add((sdm.paperTitle,RDFS.range, XSD.string))

## paperWordCount
g.add((sdm.paperWordCount,RDFS.domain, sdm.Paper))
g.add((sdm.paperWordCount,RDFS.range, XSD.integer))

## paperAbstract 
g.add((sdm.paperAbstract,RDFS.domain, sdm.Paper))
g.add((sdm.paperAbstract,RDFS.range, XSD.string))

## paperDOI
g.add((sdm.paperDOI,RDFS.domain, sdm.Paper))
g.add((sdm.paperDOI,RDFS.range, XSD.string))

## Area concept data properties 
## hasTopicName
g.add((sdm.hasTopicName,RDFS.domain, sdm.Area))
g.add((sdm.hasTopicName,RDFS.range, XSD.string))

#=============================================================================# 
#                                EXPORT TBOX                                  # 
#=============================================================================# 

os.chdir(savefolder)
g.serialize(destination='output_tbox.rdf',format="xml")