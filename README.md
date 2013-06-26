# Tethne

Tethne is a script for analyzing citation data. It generates a variety of networks, such as bibliographic coupling, citation, author-paper, and co-author networks, using networkx. 

![alt text](https://github.com/erickpeirson/tethne/blob/python/docs/logo.jpeg?raw=true "Logo")
*An orb-weaving spider in the genus [Tethneus](http://paleodb.org/?a=basicTaxonInfo&taxon_no=133881)*

## Collecting Web of Science data
To use Tethne you need a Web of Science data file with which to work. One such file is docs/savedrecs.txt. This file was generated from the Web of Science by first following the Web of Science's recommended search "oil spill\* mediterranean" on the Web of Science tab of the Web of Knowledge service.  

![alt text](https://github.com/erickpeirson/tethne/blob/python/docs/WebOfScienceSearch.png?raw=true "Web of Science Search")  

If you scroll down to the bottom of the search results page, you will see a set of options to save your search results.  

![alt text](https://github.com/erickpeirson/tethne/blob/python/docs/WebOfScienceResults.png?raw=true "Web of Science Results")  

Select a set of "Records" (we could have specified 1 to 156, the number of "Results" for this query), select "Full Record" and "Cited References" if you would like to utilize the full extent of Tethne's power, and finally "Save to Plain Text" your results, by default named "savedrecs.txt". An example savedrecs.txt for this tutorial is also provided in tethne/docs/.

## Collecting PubMed data

While modules utilizing PubMed data have not yet been implemented, this section describes how to collect the data that will be utilized by those modules.

First, visit http://www.ncbi.nlm.nih.gov/pubmed and from the drop-down menu next to the search bar select PMC. This will narrow your search results to the types of documents that can be interpretted by Tethne (rather than genome annotation data!). We sampled a search for "sea urchin" below.

![alt_text](https://github.com/erickpeirson/tethne/blob/python/docs/PMCSearch.png?raw=true "PMC Search")

On the search results page, check the boxes for records that you wish to network with Tethne. Then, at the top right hand corner of the page, click "Send to:" -> "File" -> "XML" -> "Create File." We've illustrated the selection of a few recrods below.

![alt_text](https://github.com/erickpeirson/tethne/blob/python/docs/PMCResults.png?raw=true "PMC Results")

The saved results for this example may be found in the docs/ folder.

## Requirements
* [Python](http://www.python.org/)
* [NetworkX](http://networkx.github.io/)
* [ElementTree](http://docs.python.org/2/library/xml.etree.elementtree.html)

I think that's it...

## Contributors
* [ap0h](https://github.com/ap0h)
* [erickpeirson](https://github.com/erickpeirson)
* [scohmer](https://github.com/scohmer)
