# -*- coding: utf-8 -*-
"""
Code to create ABOX independently of TBOX.
Input: 
    csv files of initial data from Lab 1 of Bondoc and Ganepola
    data path
    save path
Output: rdf file of ABOX (output_abox.rdf)
"""

#=============================================================================# 
#                              PRELIMINARIES                                  # 
#=============================================================================# 

# Install libraries
# !pip install rdflib
# !pip install owlrl
# !pip install Faker

import pandas as pd
import numpy as np
import os, gc
import random
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD, RDFS
import re
from datetime import datetime
from faker import Faker

#Create faker object
fake = Faker()

# Folder to save all output
savefolder='../output'

# Folder containing all data (csv)
datafolder='../data'

os.chdir(datafolder)
random.seed(123)

#=============================================================================# 
#                               PREPARE DATA                                  # 
#=============================================================================# 

#============================================================================== FUNCTIONS
def convert_to_dt(df):
    'Converts date columns (inferred from column names) into pandas datetime types'
    for col in [i for i in df.columns if 'date' in i.lower() or i.endswith('dt')]:
        print(f'To date: {col}')
        df[col]=pd.to_datetime(df[col])

def to_camel_case(text):
    """
    Convert string to camel case (no spaces)
    """
    x=[i for i in text]
    return ''.join(sum([],[x[0].upper()]+x[1:]))

#============================================================================== AUTHOR 
# Read authors and merge institution
author=pd.read_csv('authors.csv').merge(pd.read_csv('institutions.csv').rename(columns={'intitutionid':'institutionid',
                                                                                       'name':'institution'}), 
                                        on='institutionid').drop(columns='institutionid').drop(columns=['affiliations','homepage','fake'])
# Add aditional information
author['sex']=pd.Series([random.randint(1, 2) for i in range(len(author))]).map({1:'Female',2:'Male'})
author['birthdate']=[fake.date() for i in range(len(author))]
author['originCountry']=[fake.country() for i in range(len(author))]
author['hIndex']=author.hIndex.fillna(pd.Series([random.randint(1,10) for i in range(len(author))]))

# Clean up
author=author.dropna().reset_index(drop=True).rename(columns={'authorId':'author'})
author.drop(columns=['paperCount','citationCount'], inplace=True)
convert_to_dt(author)

#============================================================================== PAPER
# Read paper
paper=pd.read_csv('paper.csv').drop(columns=['sha','fake']).rename(columns={'id':'paper'})

# Synthesize new fields
paper['wordcount']=[random.randint(4000,7000) for i in range(len(paper))]
paper['abstract']=paper.abstract.fillna(pd.Series([fake.paragraph() for i in range(len(paper))]))
paper['type']=[random.sample(['short','demo','full','poster'], 1)[0] for i in range(len(paper))]
paper['doi']=[f'http://doi.org/{fake.iana_id()}/{fake.ipv4()}' for i in range(len(paper))]
paper.drop(columns=['url'], inplace=True)

# Merge paper information with conference and journal publication match
paper=pd.concat(
    [
        (pd.read_csv('submitted_to_conference.csv').merge(pd.read_csv('holds.csv').drop(columns=['fake']), on='edition')
         .drop(columns=['fake'])),
        (pd.read_csv('submitted_to_journal.csv').merge(pd.read_csv('volume_of.csv').drop(columns=['fake']), on='volume')
         .drop(columns=['fake']))
    ]
).drop_duplicates().merge(paper, on='paper')

# Fill in null dates
dts=pd.Series([fake.date() for i in range(len(paper))])
paper['published_date']=paper['published_date'].fillna(dts)
paper['submitted_date']=paper['submitted_date'].fillna(dts)

# Unify columns
paper['venue_type']=np.where(paper.conference.notna(), 'Conference', 'Journal')
paper['venue']=paper.conference.fillna(paper.journal)
paper['publication']=paper.edition.fillna(paper.volume)
paper.drop(columns=['edition','conference','volume','journal'], inplace=True)

# Since editions will now be conference conepts, all papers submitted to a conference will use the id of its proceeding as id for the conference
m=paper.venue_type=='Conference'
paper.loc[m, ['venue']] = (
    paper.loc[m, ['publication']].values)

convert_to_dt(paper)

#### PAPER CONSTRAINTS

# Submission date is less then published date
m=paper.submitted_date>paper.published_date
paper.loc[m, ['published_date', 'submitted_date']] = (
    paper.loc[m, ['submitted_date', 'published_date']].values)

# Poster can only be in conference. if not conference, change type
paper.loc[(paper.type=='poster')&(paper.venue_type=='Journal'),
          'type']=pd.Series([random.sample(['short','demo','full'], 1)[0] for i in range(len(paper))])

# Infer publication date from paper published dates
published=paper.groupby(['venue_type','venue','publication']).agg({'published_date':max,'submitted_date':min}).reset_index()
published['published_date']=published[['published_date','submitted_date']].max(axis=1)
published.drop(columns=['submitted_date'], inplace=True)
submitted=paper[['paper','submitted_date','venue_type','venue','publication']].copy()

# Get decision per paper
decision=pd.read_csv('reviews.csv').groupby('paper').agg({'decision':['sum','count']})
decision=((decision.iloc[:,0]/decision.iloc[:,1])>0.5).to_dict()
paper['decision']=paper.paper.map(decision)

# Delete values for non-approved papers based on review decisions
for col in ['published_date','publication','doi']:
    print(col)
    paper.loc[(paper.decision==False)&(paper[col].notna()),[col]]=np.nan

paper.drop(columns=['published_date'], inplace=True)

# Create submission id -- note: submission and paper has a one to one relationship, as stated in the assumptions
paper['submission']='sub-'+paper.paper.astype(int).astype(str)


#============================================================================== REVIEWS
# Read reviews
review=pd.read_csv('reviews.csv').rename(columns={'reviewerid':'reviewer'})

# Get dates
review=(submitted
 .merge(published, on=['venue_type','venue','publication'], how='outer')
 .merge(review, on=['paper'], how='right')
)
review['reviewDate']=[fake.date_between_dates(j['submitted_date'], j['published_date']) for i,j in review.iterrows()]
review.drop(columns=['venue_type','venue','publication','submitted_date','published_date'], inplace=True)
review['review']=review['paper'].astype(str)+'-'+review['reviewer'].astype(str)

#create submission id instead of paper id 
review['submission']='sub-'+review.paper.astype(int).astype(str)
review.drop(columns=['paper'], inplace=True)

#============================================================================== CONFERENCE
# Note: using edition as conference title
conference=(pd.read_csv('conference.csv').rename(columns={'id':'conference'})
            .merge(pd.read_csv('holds.csv').drop(columns=['fake']), on=['conference'])
           .merge(pd.read_csv('edition.csv').rename(columns={'id':'edition'}).drop(columns=['fake','conference']), on='edition')
           .rename(columns={'venue':'location'})
            .drop(columns=['url'])
            .rename(columns={'edition':'title','name':'conferenceSeries'})
           .drop_duplicates()
           )
conference['conference']=conference['proceeding'].copy()
conference['title']=conference['year'].astype(str) + ' ' + conference['conferenceSeries']
conference['type']=[random.sample(['workshop', 'symposium', 'expert group','regular'], 1)[0] for i in range(len(conference))]

# SENSE CHECK: Check for conference series with more than one conference -- there is one series with 2 conferences
conference[conference.duplicated(subset=['conferenceSeries'], keep=False)]

# generate more fake fields
conference['issn']=conference.issn.fillna(pd.Series([fake.ssn() for i in range(len(conference))]))
conference['publisher']=[fake.company() for i in range(len(conference))]

# Get published date
conference=(conference.merge(published[published.venue_type=='Conference']
                  .rename(columns={'venue':'conference','publication':'proceeding'}))
            .drop(columns=['venue_type'])
)

# If organizer is not an author, make null then order
conference.loc[~conference.chairperson.isin(author.author),'chairperson']=np.nan
conference.sort_values(['conference','title','chairperson'], inplace=True)

# Separate conference and proceeding: note that there is a one to one correspondence for them
cols=['title','chairperson','location','Start','End','year','conferenceSeries','type']
proceeding=conference.copy()
conference=conference[['conference']+cols].drop_duplicates().reset_index(drop=True).rename(columns={'chairperson':'organizer'})
proceeding.drop(columns=cols, inplace=True)

#============================================================================== JOURNAL
# Note: using volume id as volume as proceeding name
journal=(pd.read_csv('journal.csv').rename(columns={'id':'journal'})
            .merge(pd.read_csv('volume_of.csv').drop(columns=['fake']), on=['journal'])
           .merge(pd.read_csv('volume.csv').drop(columns=['volume']).rename(columns={'id':'volume'}).drop(columns=['fake']), on='volume')
           .drop_duplicates()
         .drop(columns=['url'])
         .rename(columns={'name':'title'})
        )
# Fill in null titles
titles=journal[['journal','title']].drop_duplicates().reset_index(drop=True)
titles.loc[titles.title.isna(), 'title']=pd.Series([i for i in 'Journal of '+fake.word() for i in range(len(titles))])
journal['title']=journal.journal.map(titles.set_index('journal').title.to_dict())
del titles

# Get published date
journal=(journal.merge(published[published.venue_type=='Journal']
                  .rename(columns={'venue':'journal','publication':'volume'}))
            .drop(columns=['venue_type'])
)

# generate more fake fields
journal['issn']=journal.issn.fillna(pd.Series([fake.ssn() for i in range(len(journal))]))
journal['publisher']=[fake.company() for i in range(len(journal))]
journal.drop(columns=['year'], inplace=True)

# If organizer is not an author, make null then order
journal.loc[~journal.editor.isin(author.author),'editor']=np.nan
journal.sort_values(['journal','title','editor'], inplace=True)

# Separate journal and volume
cols=['title','editor']
volume=journal.copy()
journal=journal[['journal']+cols].groupby(['journal','title']).head(1).reset_index(drop=True).rename(columns={'editor':'organizer'})
volume.drop(columns=cols, inplace=True)

#============================================================================== AUTHORSHIP
# Make sure authors and papers are in the main dataframes (to make sure they have propoerties)
hasAuthor=pd.read_csv('writes.csv').drop(columns=['fake'])
hasAuthor=hasAuthor.dropna().reset_index(drop=True)
hasAuthor=hasAuthor[hasAuthor.paper.isin(paper.paper)&(hasAuthor.author.isin(author.author))].reset_index(drop=True)

#============================================================================== ORGANIZERS
# Fill null organizers in journal and conference - make sure they are not authors in the same conference edition/journal
a_list=set(author.author.unique())
for df in ['conference','journal']:
    print(df)
    nulls=globals()[df][globals()[df].organizer.isna()]
    for i in nulls[df]:
        a=set(paper.loc[(paper.venue_type==to_camel_case(df))&(paper.venue==i),
                      ['paper']].merge(hasAuthor, on='paper').author.unique())
        globals()[df].loc[globals()[df][df]==i,'organizer']=np.random.choice(list(a_list-a))
print(conference.organizer.isna().sum(), journal.organizer.isna().sum())

del nulls, a_list

# Edit Paper/submission
# Get information about the chair/editor that assigned reviewers for that submission
org=pd.concat([conference[['conference','organizer']].assign(venue_type='Conference').rename(columns={'conference':'venue'}),
           journal[['journal','organizer']].assign(venue_type='Journal').rename(columns={'journal':'venue'})]).drop_duplicates()

paper=paper.merge(org, on=['venue_type','venue'], how='left')

#============================================================================== ID DATATYPES
# Convert selected id columns to int64
df_list = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
for df in df_list:
    cols=[i for i in globals()[df].columns if i in ['author', 'organizer', 'paper', 'reviewer']]
    if len(cols)>0:
        print('\n\n=======',df,'=======')
        for col in cols:
            print(col)
            globals()[df][col]=(globals()[df][col]).astype('int64')
            
#============================================================================== AREA
area=pd.read_csv('topic.csv', usecols=['community']).rename(columns={'community':'topicName'}).drop_duplicates().reset_index(drop=True)
area['area']='area-'+area.index.astype(str)

#============================================================================== HASTOPIC
hasTopic=[]
for df in ['paper','journal','volume','conference','proceeding']:
    hasTopic.append(globals()[df][[df]].rename(columns={df:'id'}).assign(typ=df))
hasTopic=pd.concat(hasTopic, ignore_index=True)
hasTopic['area']=[random.sample(list(area.area.unique()), 1)[0] for i in range(len(hasTopic))]
hasTopic=hasTopic.merge(area, on=['area'])

del org, published, submitted
gc.collect()

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
#                                DEFINE ABOX                                  # 
#=============================================================================# 

#==============================================================================  FUNCTIONS
def prepareValue(row, uri=sdm):
    """
    Function that prepares the values to be added to the graph as a URI or Literal
    source: https://wiki.uib.no/info216/index.php/Python_Examples#RDF_programming_with_RDFlib_.28Lab_2.29
    Input: row value 
    Output: Converted URI or literal
    """
    if row == None:  # none type
        value = Literal(row)
    elif (isinstance(row, str) and re.match(r'\d{4}-\d{2}-\d{2}', row)) or isinstance(row, datetime):  # date
        value = Literal(row, datatype=XSD.date)
    elif isinstance(row, bool):  # boolean value (true / false)
        value = Literal(row, datatype=XSD.boolean)
    elif isinstance(row, int):  # integer
        value = Literal(row, datatype=XSD.integer)
    elif isinstance(row, str):  # string
        value = Literal(row, datatype=XSD.string)
    elif isinstance(row, float):  # float
        value = Literal(row, datatype=XSD.float)
    return value

#==============================================================================  CLEAN ALL DATAFRAMES
# General cLean up of all dfs
df_list = [var for var in dir() if isinstance(eval(var), pd.core.frame.DataFrame)]
for df in df_list:
    print(df)
    # replace nulls with None
    globals()[df]=globals()[df].replace(np.nan, None)
    
    # Make all date columns into datetime
    dcols=[i for i in globals()[df].columns if 'date' in i.lower() or i.endswith('_dt')]
    for col in dcols:
        globals()[df][col]=pd.to_datetime(globals()[df][col])
        
#==============================================================================  ABOX FUNCTIONS        
# Convert the non-semantic CSV dataset into a semantic RDF
def area_to_rdf(df):
    """
    Concepts: Area
    """
    for index, row in df.iterrows():
        id = URIRef(sdm + "Area_" + str(row['area']))
        name = prepareValue(row["topicName"])
        
        # Adds the triples
#         g.add((id, RDF.type, sdm.Area))
        g.add((id, sdm.hasTopicName, name))
        
    print('Done: Area')
        
def author_to_rdf(df):
    """
    Concepts: Person, Author
    """
    for index, row in df.iterrows():
        # define values
        #id = URIRef(sdm + "Person_" + str(row['author']))
        id = URIRef(sdm + "Author_" + str(row['author']))
        name = prepareValue(row["name"])
        birthdate = prepareValue(row["birthdate"])
        sex = prepareValue(row["sex"])
        country = prepareValue(row["originCountry"])
        
        # Adds the triples
#         g.add((id, RDF.type, sdm.Author))
        g.add((id, sdm.hasPersonName, name))
        g.add((id, sdm.hasBirthDate, birthdate))
        g.add((id, sdm.hasSex, sex))
        g.add((id, sdm.originCountry, country))
        
        # Author
        #id = URIRef(sdm + "Author_" + str(row['author']))
        url = prepareValue(row["url"])
        hindex = prepareValue(row["hIndex"])
        institution = prepareValue(row["institution"])
                
        # Adds the triples
        g.add((id, sdm.url, url))
        g.add((id, sdm.hasHIndex, hindex))
        g.add((id, sdm.affiliatedWithInstitution, institution))
    print('Done: Author')

def conference_to_rdf(df):
    """
    Concepts: Conference
    Relationships: hasOrganizer
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Conference_" + str(row['conference']))
        conf_type={'expert group':sdm.ExpertGroup, 'symposium':sdm.Symposium, 
                   'workshop':sdm.Workshop, 'regular':sdm.RegularConference}[row['type']]
        title = prepareValue(row["title"])
        location = prepareValue(row["location"])
        start = prepareValue(row["Start"])
        end = prepareValue(row["End"])
        year = prepareValue(row["year"])
        conferenceSeries = prepareValue(row["conferenceSeries"])
        
        # Adds the triples 
        g.add((id, RDF.type, conf_type))
        g.add((id, sdm.hasVenueTitle, title))
        g.add((id, sdm.heldIn, location))
        g.add((id, sdm.startDate, start))
        g.add((id, sdm.endDate, end))
        g.add((id, sdm.heldInYear, year))
        g.add((id, sdm.conferenceSeries, conferenceSeries))
        
        # Relationships
        author_org=URIRef(sdm + "Author_" + str(row['organizer']))
        #author_org=URIRef(sdm + str(row['organizer']))
        
        # Adds the triples
        g.add((author_org, RDF.type, sdm.Chair))
        g.add((id, sdm.hasOrganizer, author_org))
    print('Done: Conference')
        
def journal_to_rdf(df):
    """
    Concepts: Journal
    Relationships: hasOrganizer
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Journal_" + str(row['journal']))
        title = prepareValue(row["title"])
        
        # Adds the triples 
        g.add((id, RDF.type, sdm.Journal))
        g.add((id, sdm.hasVenueTitle, title))
        
        # Relationships
        author_org=URIRef(sdm + "Author_" + str(row['organizer']))
        #author_org=URIRef(sdm + str(row['organizer']))

        
        # Adds the triples
        g.add((author_org, RDF.type, sdm.Editor))
        g.add((id, sdm.hasOrganizer, author_org))
    print('Done: Journal')

def volume_to_rdf(df):
    """
    Concepts: Volume
    Relationships: hasPublished
    NOTE: Used Venue > Publication relationship. note that Volume URIs replace spaces with _
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Volume_" + str(row['volume']).replace(' ','_'))
        jid= URIRef(sdm + "Journal_" + str(row['journal']))
        issn = prepareValue(row["issn"])
        published_date = prepareValue(row["published_date"])
        publisher = prepareValue(row["publisher"])
        
        # Adds the triples
        g.add((id, RDF.type, sdm.Volume))
        g.add((id, sdm.publicationIssn, issn))
        g.add((id, sdm.publishedDate, published_date))
        g.add((id, sdm.publisher, publisher))
        
        # Relationship
        g.add((jid, sdm.hasPublished, id))
    print('Done: Volume')

def proceeding_to_rdf(df):
    """
    Concepts: proceeding
    Relationships: hasPublished
    NOTE: Used Venue > Publication relationship
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Proceeding_" + str(row['proceeding']))
        cid= URIRef(sdm + "Conference_" + str(row['conference']))
        issn = prepareValue(row["issn"])
        published_date = prepareValue(row["published_date"])
        publisher = prepareValue(row["publisher"])
        
        # Adds the triples
        g.add((id, RDF.type, sdm.Proceeding)) 
        g.add((id, sdm.publicationIssn, issn))
        g.add((id, sdm.publishedDate, published_date))
        g.add((id, sdm.publisher, publisher))
        
        # Relationship
        g.add((cid, sdm.hasPublished, id))
    print('Done: Proceeding')

def paper_to_rdf(df):
    """
    Concepts: Paper, Submission
    Relationships: includedIn, publishedIn, assignedBy, submittedTo
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Paper_" + str(row['paper']))
        sid = URIRef(sdm + "Submission_" + str(row['submission']))
        oid=URIRef(sdm + 'Author_' + str(row['organizer']))
        vid=URIRef(sdm + row['venue_type']+'_' + str(row['venue']))
        paper_type={'demo':sdm.DemoPaper, 'full':sdm.FullPaper, 'short':sdm.ShortPaper, 'poster':sdm.Poster}[row['type']]
        
        for col in df.columns:
            locals()[col]=prepareValue(row[col])
            
        # Paper properties
        g.add((id,RDF.type, paper_type))
        g.add((id,sdm.paperAbstract, locals()['abstract']))
        g.add((id,sdm.paperTitle, locals()['title']))
        g.add((id,sdm.paperWordCount, locals()['wordcount']))

        # Submission properties
        g.add((sid,sdm.submissionDate, locals()['submitted_date']))

        # Relationships
        g.add((id,sdm.includedIn,sid))
        g.add((sid, sdm.assignedBy, oid))
        g.add((sid, sdm.submittedTo, vid))
        
        # Conditional property and relationship, only add if paper decision is true (published)
        if row['decision']:
            pid=URIRef(sdm + {'Conference':'Proceeding_','Journal':'Volume_'}[row['venue_type']] + str(row['publication']).replace(' ','_'))
            g.add((id,sdm.paperDOI, locals()['doi']))
            if row['type']!='poster':
                g.add((id,sdm.publishedIn,pid))
            else:
                g.add((id,sdm.posterPublishedIn,pid))
    print('Done: Paper')

def review_to_rdf(df):
    """
    Concepts: Review
    Relationships: hasReviewer, hasReview
    """
    for index, row in df.iterrows():
        # define values
        id = URIRef(sdm + "Review_" + str(row['review']))
        sid = URIRef(sdm + "Submission_" + str(row['submission']))
        rid=URIRef(sdm + 'Author_' + str(row['reviewer']))
        #rid=URIRef(sdm + str(row['reviewer']))
        
        for col in df.columns:
            locals()[col]=prepareValue(row[col])
            
        # Paper properties
        g.add((id,sdm.decision, locals()['decision']))
        g.add((id,sdm.content, locals()['content']))
        g.add((id,sdm.reviewDate, locals()['reviewDate']))

        # Relationships
        g.add((id,sdm.hasReviewer,rid))
        g.add((sid, sdm.hasReview, id))
    print('Done: Review')
        
def hasauthor_to_rdf(df):
    """
    Relationships: hasAuthor
    """
    for index, row in df.iterrows():
        # define values
        pid = URIRef(sdm + "Paper_" + str(row['paper']))
        aid = URIRef(sdm + "Author_" + str(row['author']))
        #aid = URIRef(sdm + str(row['author']))

        # Relationships
        g.add((pid,sdm.hasAuthor,aid))
    print('Done: hasAuthor')
        
def hastopic_to_rdf(df):
    """
    Relationships: paperRelatedTo, venueRelatedTo, publicationRelatedTo
    """
    for index, row in df.iterrows():
        # define values
        pid = URIRef(sdm + to_camel_case(row['typ'])+'_' + str(row['id']).replace(' ','_'))
        aid = URIRef(sdm + "Area_" + str(row['area']))
        rel={'paper':sdm.paperRelatedTo, 'journal':sdm.venueRelatedTo, 'volume':sdm.publicationRelatedTo, 
             'conference':sdm.venueRelatedTo, 'proceeding':sdm.publicationRelatedTo}[row['typ']]

        # Relationships
        g.add((pid,rel,aid))
        
    print('Done: hasTopic')
    
#==============================================================================  IMPLEMENTATION
# Call functions
area_to_rdf(area)
author_to_rdf(author)
conference_to_rdf(conference)
journal_to_rdf(journal)
volume_to_rdf(volume)
proceeding_to_rdf(proceeding)
paper_to_rdf(paper) 
review_to_rdf(review) 
hasauthor_to_rdf(hasAuthor)
hastopic_to_rdf(hasTopic)

# Get total counts
for df in df_list:
    cols=globals()[df].columns
    if df in cols:
        print(f'{df}: {globals()[df][df].nunique()}')
    if 'type' in cols:
        print(f'{df} types:\n', globals()[df]['type'].value_counts().to_frame(),'\n')
    if 'organizer' in cols:
        print(f'{df} organizer: {globals()[df]["organizer"].nunique()}')
print('Total unique organizers:',pd.concat([conference['organizer'], journal['organizer']]).nunique())

#=============================================================================# 
#                                EXPORT ABOX                                  # 
#=============================================================================# 

os.chdir(savefolder)
g.serialize(destination='output_abox.rdf',format="xml")