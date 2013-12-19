"""
To do: move testing of different types of attributes to writers testing
rather than graph testing; NetworkX can support any data structure as an
attribute but the graph file formats may not.
Copyright 2013 Aaron Baker
Few changes : testing fork 
    
"""
import tethne.readers as rd
import tethne.networks as nt
import tethne.writers as wr
import tethne.utilities as util
import unittest
import networkx as nx
import os
import os.path

class TestCitationGraph(unittest.TestCase):
    """
    Test the citations, internal_citations networks (assuming the reader 
        is functioning) by checking both 'citation' and 'internal' networks
        each with either 'doi' or 'ayjid' node_ids and either no
        node attributes or 4 node attributes of 4 different variable
        types
    The sparse data file networks are built on is //testin/wos_citations.txt
   """
    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_citations.txt')
        meta_list = rd.wos2meta(wos_data)

        # ayjid with no attributes
        (self.ayjid_citations, 
         self.ayjid_internal) = nt.nx_citations(meta_list, 'ayjid')

        # doi with no attributes                                          
        (self.doi_citations, 
         self.doi_internal) = nt.nx_citations(meta_list, 'doi')

        # int, string, list, dict
        self.node_attribs = ('date', 'atitle', 'aulast', 'citations')

        # ayjid with attribs 
        (self.ayjid_cit_attrib,
         self.ayjid_int_attrib) = nt.nx_citations(meta_list,
                                                  'ayjid',
                                                  *self.node_attribs)
        # doi with attribs
        (self.doi_cit_attrib,
         self.doi_int_attrib) = nt.nx_citations(meta_list,
                                                'doi',
                                                *self.node_attribs)

    def test_ayjid(self):
        """
        Test of nx_citations with ayjid as node_id and no node attributes

        If fails, something is wrong with the construction of ayjid's
        """
        # three papers in file each with author, year, journal information
        self.assertEqual(nx.number_of_nodes(self.ayjid_internal), 3)

        # ayjid of first paper's first reference does not match exactly
        # with the ayjid of the second paper
        self.assertEqual(nx.number_of_edges(self.ayjid_internal), 0)

        # since inexact match, 3 papers with 8 citations
        self.assertEqual(nx.number_of_nodes(self.ayjid_citations), 11)

        # one edge from paper to its citations
        self.assertEqual(nx.number_of_edges(self.ayjid_citations), 8)

    def test_doi(self):
        """
        Test of nx_citations with doi as node_id and no node attributes

        If fails, something is wrong with the parsing of WOS files at
        either the DI field tag for papers or the DOI number in the CR
        field tag
        """
        # three papers in file, each with DI(=DOI) field tags
        self.assertEqual(nx.number_of_nodes(self.doi_internal), 3)

        # DOI does match exactly: first paper references second paper
        self.assertEqual(nx.number_of_edges(self.doi_internal), 1)

        # only 7 of the papers/references have DOI numbers
        self.assertEqual(nx.number_of_nodes(self.doi_citations), 7)

        # first paper has edges to its 3 citations, second has one to its
        # and third has one
        self.assertEqual(nx.number_of_edges(self.doi_citations), 5)

    def test_node_attribs(self):
        """
        Test adding of node attributes to 4 graphs: ayjid no attribs, ayjid
            with attribs, doi no attribs, and doi with attribs

        If fails, something is wrong with the assigning of node attributes
        from a meta_dict in the citations networks
        """
        # check that the attributes got added to each node
        graphs = [self.ayjid_cit_attrib, self.ayjid_int_attrib,
                  self.doi_cit_attrib, self.doi_int_attrib]
        for graph in graphs:
            for node in graph.nodes():
                node_attribs = sorted(graph.node[node])
                check_attribs = sorted(self.node_attribs)
                self.assertEqual(node_attribs, check_attribs)
        
    def test_edge_attribs(self):
        """
        Test adding of edge attributes indicating what date a paper is cited

        If fails, something is wrong with assigning the edge attribute from a
        paper to its citation indicating the date of citation
        """
        # attributes of first paper citing its first reference
        edge_attribs = self.doi_citations.edge['10.1007/s10646-013-1042-4']['10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2']
        keys = edge_attribs.keys()
        self.assertIn('date', keys)
        self.assertEqual(edge_attribs['date'], 2013)

    def test_no_edge_attrib(self):
        """
        Test adding of edge attributes when citating paper's date is missing

        If the publication date is unknown (that is, PY field tag is missing
        from the WOS data file), the edge_attribute has value None; if
        fails that assumption is wrong
        """
        # attributes of third paper citing its only reference, PY=date key
        # missing
        edge_attribs = self.doi_citations.edge['10.1016/j.ecolind.2011.07.024']['10.1016/j.ecss.2008.08.010']
        keys = edge_attribs.keys()
        self.assertIn('date', keys)
        self.assertEqual(edge_attribs['date'], None)

    def tearDown(self):
        pass

class TestAuthorPapersGraph(unittest.TestCase):
    """
    Test the author_papers network
    Assumes reader is functioning

    The test file ./testin/wos_authors.txt contains two papers in WoS field tag
    format that are from the same author. One is fully capitalized and the
    other is not.

    We also test multiple authors and their link to the same paper
    """
    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_authors.txt')
        meta_list = rd.wos2meta(wos_data)
        self.no_attribs = nt.nx_author_papers(meta_list, 'doi')

        # int, string, list, dict
        node_attribs = ('date', 'atitle', 'aulast', 'citations')
        self.node_attribs = nt.nx_author_papers(meta_list, 'doi',
                                                *node_attribs)

    def test_case_sensitivity(self):
        """
        Fails if case sensitivity of author names matters
        This is particularly relevant for author_papers network because
        a string identifier is all we have to identify authors

        more of a reader test case
        """
        person_count = 0
        for node in self.no_attribs:
            if self.no_attribs.node[node]['type'] == 'person':
                person_count += 1

        self.assertEqual(person_count, 2)

    def test_no_attribs(self):
        # 2 authors; 2 papers
        self.assertEqual(nx.number_of_nodes(self.no_attribs), 4)

        # ADAMS has 2 papers, MCLEAN has 1 paper
        self.assertEqual(nx.number_of_edges(self.no_attribs), 3)

        # each node minimally has the type attribute distinguishing
        # paper nodes from person nodes
        expected_keys = ['type']
        for node in self.no_attribs.nodes(data=True):
            node_attribs = node[1]
            obtained_keys = node_attribs.keys()
            self.assertEqual(expected_keys, obtained_keys)

    def test_node_attribs(self):
        # 2 authors; 2 papers
        self.assertEqual(nx.number_of_nodes(self.no_attribs), 4)

        # ADAMS has 2 papers, MCLEAN has 1 paper
        self.assertEqual(nx.number_of_edges(self.no_attribs), 3)

        # 2 edges from author Adams S to his 2 papers
        # the following information is pulled from the test WoS file
        paper1_node_id = '10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2'

        # paper 1 node attributes
        atitle1 = None
        aulast1 = ['ADAMS']
        date1 = 1993
        cr1_list = ['Adams S. M., 1990, AM FISHERIES SOC S',
                    ('ADAMS SM, 1985, J FISH BIOL, V26, P111,' + 
                        'DOI 10.1111/j.1095-8649.1985.tb04248.x'),
                    'ADAMS SM, 1992, ECOTOX ENVIRON SAFE, V24, P347',
                    'Adams SM, 1990, AM FISHERIES SOC S, V8, P1']
        citations1 = []
        for cite in cr1_list:
            cite_dict = rd.parse_cr(cite)
            citations1.append(cite_dict)

        # and those attributes in the expected form: a 'primitive' dictionary
        paper1_expected_attribs = {'atitle':atitle1,
                                   'aulast':aulast1,
                                   'date':date1,
                                   'citations':citations1,
                                   'type':'paper'}
        paper1_expected_keys = paper1_expected_attribs.keys()
        paper1_expected_attribs = util.subdict(paper1_expected_attribs, 
                                                      paper1_expected_keys)

        # and for paper 2 nodes (note ADAMS S is an author for both papers)
        paper2_node_id = '10.1111/j.1095-8649.1985.tb04248.x'

        # and paper 2 node attributes
        atitle2 = None
        aulast2 = ['Adams', 'MCLEAN']
        date2 = 1985
        cr2_list = [('CR ADAMS SM, 1982, CAN J FISH AQUAT SCI, V39,' + 
                        'P1175, DOI 10.1139/f82-155'),
                    ('ADAMS SM, 1982, T AM FISH SOC, V111, P549,' + 
                        'DOI 10.1577/1548-8659(1982)111<549:EPILBU>2.0.CO;2'),
                    ('ALLEN JRM, 1982, J FISH BIOL, V21, P537,' + 
                        'DOI 10.1111/j.1095-8649.1982.tb02858.x')]
        citations2 = []
        for cite in cr2_list:
            cite_dict = rd.parse_cr(cite)
            citations2.append(cite_dict)

        # and those attributes in the expected form: a 'primitive' dictionary
        paper2_expected_attribs = {'atitle':atitle2,
                                   'aulast':aulast2,
                                   'date':date2,
                                   'citations':citations2,
                                   'type':'paper'}
        paper2_expected_keys = paper2_expected_attribs.keys()
        paper2_expected_attribs = util.subdict(paper2_expected_attribs, 
                                                      paper2_expected_keys)



        # verify the contents of paper 1
        paper1_obtained_attribs = self.node_attribs.node[paper1_node_id]
        self.assertItemsEqual(paper1_expected_attribs, 
                              paper1_obtained_attribs)

        # and paper 2
        paper2_obtained_attribs = self.node_attribs.node[paper2_node_id]
        self.assertItemsEqual(paper2_expected_attribs, 
                              paper2_obtained_attribs)

    def tearDown(self):
        pass


class TestCoauthorsGraph(unittest.TestCase):
    """
    Test the coauthors network, assumes reader is functioning
    """

    def setUp(self):
        #read data from docs folder
        wos_data = rd.parse_wos('./testin/wos_coauthors.txt')
        meta_list = rd.wos2meta(wos_data)

        # test network built from meta_list with no edge attributes
        self.no_attribs = nt.nx_coauthors(meta_list)

        # test network built from meta_list with optional edge attributes
        # attributes of type str, int, list, dict
        self.attribs = ('atitle', 'date', 'aulast', 'citations')
        self.edge_attribs = nt.nx_coauthors(meta_list, *self.attribs)

    def test_graph_structure(self):
        # test for number of nodes and edges
        # viewing the input file we see 2 papers, one with 6 authors and
        # another with 4 but Cajaraville is a common author
        self.assertEqual(nx.number_of_nodes(self.no_attribs), 9)

        # 6 choose 2 + 4 choose 2 = 21 edges
        self.assertEqual(nx.number_of_edges(self.no_attribs), 21)

    def test_no_attribs(self):
        # test to ensure no edge attributes in the no_attribs graph
        expected_attribs = {}
        for edge in self.no_attribs.edges(data=True):
            obtained_attribs = edge[2]
            self.assertItemsEqual(expected_attribs, obtained_attribs)

    def test_edge_attribs(self):
        # test to ensure proper edge attributes in the edge_attribs graph
        # the following data is obtained from the input file for the
        # attribs specified in the setUp step: atitle, date, aulast, citations
        # note the wos2meta function runs upper() on names
        paper1_name_list = ['Marigomez I', 'Garmendia L', 'Soto M', 'Orbea A',
                            'Izagirre U', 'Cajaraville M']
        for i in xrange(len(paper1_name_list)):
            paper1_name_list[i] = paper1_name_list[i].upper().strip()

        paper1_atitle = ('TI Marine ecosystem health status assessment' +
                         'through integrative biomarker indices: a' + 
                         'comparative study after the Prestige oil' + 
                         'spill "Mussel Watch"')
        paper1_date = 2013
        paper1_aulast = ['Marigomez', 'Garmendia', 'Soto', 'Orbea'] 
        for i in xrange(len(paper1_aulast)):
            paper1_aulast[i] = paper1_aulast[i].upper().strip()
        paper1_cr_list = [('ADAMS SM, 1993, T AM FISH SOC, V122, P63,' +
                           'DOI 10.1577/1548-8659(1993)122<0063:AQHAIF>' + 
                           '2.3.CO;2'),
                          ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21,' +
                           'P1316, DOI 10.1897/1551-5028(2002)021' +
                           '<1316:IBRAUT>2.0.CO;2')]
        paper1_citations =  []
        for cite in paper1_cr_list:
            paper1_citations.append(rd.parse_cr(cite))

        # put the above data in the form that it is processed in Tethne
        paper1_expected_attribs = {'atitle':paper1_atitle,
                                   'date':paper1_date,
                                   'aulast':paper1_aulast,
                                   'citations':paper1_citations}
        paper1_expected_attribs = util.subdict(paper1_expected_attribs,
                                                      self.attribs)

        # do the same for the second paper in the document
        paper2_name_list = ['Han D', 'Tong X', 'Jin M', 'Cajaraville M']
        for i in xrange(len(paper2_name_list)):
            paper2_name_list[i] = paper2_name_list[i].upper().strip()
        paper2_atitle = ('Evaluation of organic contamination in urban' + 
                         'groundwater surrounding a municipal landfill,' + 
                         'Zhoukou, China')
        paper2_date = 2013
        paper2_aulast = ['Han', 'Tong', 'Jin', 'Cajaraville']
        for i in xrange(len(paper2_aulast)):
            paper2_aulast[i] = paper2_aulast[i].upper().strip()
        paper2_cr_list = [('Akyuz M, 2010, SCI TOTAL ENVIRON, V408, P5550,' + 
                           'DOI 10.1016/j.scitotenv.2010.07.063'),
                          ('APHA, 1992, STAND METH EX WAT WA'),
                          ('Basberg L, 1998, AQUAT GEOCHEM, V4, P253,' + 
                           'DOI 10.1023/A:1009623205558')]
        paper2_citations = []
        for cite in paper2_cr_list:
            paper2_citations.append(rd.parse_cr(cite))

        # and again put it in the expected form in Tethne
        paper2_expected_attribs = {'atitle':paper2_atitle,
                                   'date':paper2_date,
                                   'aulast':paper2_aulast,
                                   'citations':paper2_citations}
        paper2_expected_attribs = util.subdict(paper2_expected_attribs,
                                                      self.attribs)

        # test the actual edge attributes in the graph
        for name_index_1 in xrange(len(paper1_name_list)):
            name1 = paper1_name_list[name_index_1]
            for name_index_2 in xrange(name_index_1+1, len(paper1_name_list)):
                name2 = paper1_name_list[name_index_2]
                paper1_obtained_attribs = self.edge_attribs.edge[name1]\
                                                                [name2]
                self.assertItemsEqual(paper1_expected_attribs,
                                      paper1_obtained_attribs)

        for name_index_1 in xrange(len(paper2_name_list)):
            name1 = paper2_name_list[name_index_1]
            for name_index_2 in xrange(name_index_1+1, len(paper2_name_list)):
                name2 = paper2_name_list[name_index_2]
                paper2_obtained_attribs = self.edge_attribs.edge[name1]\
                                                                [name2]
                self.assertItemsEqual(paper2_expected_attribs,
                                      paper2_obtained_attribs)

    def tearDown(self):
        pass


class TestBiblioGraph(unittest.TestCase):
    """
    Test the bibliographic_coupling network; assumes reader is functioning

    The viewer will note that the input file has 4 papers trimmed down
    and modified from the sample //docs/savedrecs.txt. 
    
    The references
    were constructed so that the first paper shares two citations with the
    second paper, one (of the two shared between first and second) citation 
    with the third paper, and zero citations with the fourth paper.
    """
    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_biblio.txt')
        wos_meta = rd.wos2meta(wos_data)
        self.ayjid_zero = nt.nx_biblio_coupling(wos_meta, 
                                                 'ayjid',
                                                 0,
                                                 'ayjid')
        self.ayjid_one = nt.nx_biblio_coupling(wos_meta, 
                                               'ayjid',
                                               1,
                                               'ayjid')
        self.ayjid_two = nt.nx_biblio_coupling(wos_meta, 
                                               'ayjid',
                                               2,
                                               'ayjid')
        self.ayjid_attribs = nt.nx_biblio_coupling(wos_meta,
                                                   'ayjid',
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'aulast',
                                                   'date',
                                                   'citations')

        # define a separate file for the missing citations test case
        # with the same data as the other test file with the exception
        # that the fourth paper is missing its citation record
        wos_cite = rd.parse_wos('./testin/wos_biblio_cite.txt')
        doc_list_cite = rd.wos2meta(wos_cite)
        self.missing_citations_zero =  nt.nx_biblio_coupling(doc_list_cite,
                                                             'ayjid',
                                                             0,
                                                             'ayjid')

        self.missing_citations_one =  nt.nx_biblio_coupling(doc_list_cite,
                                                            'ayjid',
                                                            1,
                                                            'ayjid')

    def test_ayjid_zero(self):
        """
        Every paper shares at least 0 references with every other
        paper. This makes a complete graph.
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.ayjid_zero), 4)
        # 4 choose 2 = 6 edges 
        self.assertEqual(nx.number_of_edges(self.ayjid_zero), 6)

    def test_ayjid_one(self):
        """
        With threshold greater than 0, two papers must share at least 1
        reference in common. Test this when threshold is 1.
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.ayjid_one), 4)
        # first paper shares 2 >= 1 references with second, 1 >= 1 references
        # with third, and the second and third share 1 >= 1 references
        self.assertEqual(nx.number_of_edges(self.ayjid_one), 3)

    def test_ayjid_two(self):
        """
        With threshold greater than 0, two papers must share at least 1
        reference in common. Test this when threshold is 2.
        """
        self.assertEqual(nx.number_of_nodes(self.ayjid_two), 4)
        # first paper shares 2 >= 2 references with second
        self.assertEqual(nx.number_of_edges(self.ayjid_two), 1)

    def test_attribs(self):
        """
        Test the addition of four node attributes of different types:
            atitle - a string
            date - an int
            aulast - a list
            citations - a dictionary
        Presumably a double may be added to a network just as easily as an
        int, but we have no doubles to test in our standard meta_dict
        """
        # paper 1 meta data
        node1_atitle = ('Marine ecosystem health status assessment' + 
                        ' through integrative biomarker indices:' + 
                        ' a comparative study after the Prestige oil' + 
                        ' spill "Mussel Watch"')
        node1_date = 2013
        node1_aulast = ['Marigomez', 'Garmendia', 'Soto', 'Orbea', 
                        'Izagirre', 'Cajaraville']
        for i in xrange(len(node1_aulast)):
            node1_aulast[i] = node1_aulast[i].upper().strip()
        node1_cr_list = [('ADAMS SM, 1993, T AM FISH SOC, V122, P63, DOI' + 
                          ' 10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' + 
                          'P1316, DOI 10.1897/1551-5028(2002)021<1316:' +
                          'IBRAUT>2.0.CO;2')]
        node1_citations = []
        for cite in node1_cr_list:
            node1_citations.append(rd.parse_cr(cite))
        node1_expected_attribs = {'atitle':node1_atitle,
                                  'date':node1_date,
                                  'aulast':node1_aulast,
                                  'citations':node1_citations}
        node1_ayjid = 'MARIGOMEZ I 2013 ECOTOXICOLOGY' 

        # paper 2 meta data
        node2_atitle = ('Evaluation of organic contamination in urban ' + 
                        'groundwater surrounding a municipal landfill, ' + 
                        'Zhoukou, China')
        node2_date = 2013
        node2_aulast = ['Han', 'Tong', 'Jin', 'Hepburn', 'Tong', 'Song']
        for i in xrange(len(node2_aulast)):
            node2_aulast[i] = node2_aulast[i].upper().strip()
        node2_cr_list = [('ADAMS SM, 1993, T AM FISH SOC, V122, P63, ' + 
                          'DOI 10.1577/1548-8659(1993)122<0063:AQHAIF>' +
                          '2.3.CO;2'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' + 
                          'P1316, DOI 10.1897/1551-5028(2002)021<1316:' + 
                          'IBRAUT>2.0.CO;2')]
        node2_citations = []
        for cite in node2_cr_list:
            node2_citations.append(rd.parse_cr(cite))
        node2_expected_attribs = {'atitle':node2_atitle,
                                  'date':node2_date,
                                  'aulast':node2_aulast,
                                  'citations':node2_citations}
        node2_ayjid = 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'

        # paper 3 meta data
        node3_atitle = ('Multilevel governance and management of shared ' + 
                        'stocks with integrated markets: The European ' + 
                        'anchovy case')
        node3_date = 2013
        node3_aulast = ['Mulazzani', 'Curtin', 'Andres', 'Malorgio']
        for i in xrange(len(node3_aulast)):
            node3_aulast[i] = node3_aulast[i].upper().strip()
        node3_cr_list = [('AdriaMed, GEN OUTL MAR CAPT FI'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' +
                          'P1316, DOI 10.1897/1551-5028(2002)021' + 
                          '<1316:IBRAUT>2.0.CO;2')]
        node3_citations = []
        for cite in node3_cr_list:
            node3_citations.append(rd.parse_cr(cite))
        node3_expected_attribs = {'atitle':node3_atitle,
                                  'date':node3_date,
                                  'aulast':node3_aulast,
                                  'citations':node3_citations}
        node3_ayjid = 'MULAZZANI L 2013 MARINE POLICY'

        # paper 4 meta data
        node4_atitle = ('Application of multiple geochemical markers to ' + 
                        'investigate organic pollution in a dynamic coastal ' + 
                        'zone')
        node4_date = 2013
        node4_aulast = ['Liu', 'Wang', 'Wong', 'Qiu', 'Zeng']
        for i in xrange(len(node4_aulast)):
            node4_aulast[i] = node4_aulast[i].upper().strip()
        node4_cr_list = [('AIZENSHT.Z, 1973, GEOCHIM COSMOCHIM AC, V37, ' + 
                          'P559, DOI 10.1016/0016-7037(73)90218-4'),
                         ('BLUMER M, 1971, MAR BIOL, V8, P183, DOI ' + 
                          '10.1007/BF00355214'),
                         ('Cachot J, 2007, ENVIRON SCI TECHNOL, V41, ' + 
                          'P7830, DOI 10.1021/es071082v')]
        node4_citations = []
        for cite in node4_cr_list:
            node4_citations.append(rd.parse_cr(cite))
        node4_expected_attribs = {'atitle':node4_atitle,
                                  'date':node4_date,
                                  'aulast':node4_aulast,
                                  'citations':node4_citations}
        node4_ayjid = 'LIU L 2013 ENVIRONMENTAL TOXICOLOGY AND CHEMISTRY'

        # obtain node attributes from network and test them
        node_list = [node1_ayjid, node2_ayjid, node3_ayjid, node4_ayjid]
        attrib_list = [node1_expected_attribs, node2_expected_attribs,
                       node3_expected_attribs, node4_expected_attribs]
        for i in xrange(len(node_list)):
            node = node_list[i]
            expected_attribs = attrib_list[i]
            obtained_attribs = self.ayjid_attribs.node[node]
            self.assertEqual(expected_attribs, obtained_attribs)

    def test_missing_citations_zero(self):
        """
        if fails network is not robust to papers missing citation data
        test for threshold = 0
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.missing_citations_zero), 4)
        # 4 choose 2 = 6 edges 
        self.assertEqual(nx.number_of_edges(self.missing_citations_zero), 6)


    def test_missing_citations_one(self):
        """
        if fails network is not robust to papers missing citation data
        test for threshold = 1
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.missing_citations_one), 4)
        # first paper shares 2 >= 1 references with second, 1 >= 1 references
        # with third, and the second and third share 1 >= 1 references and
        # fourth constructed to have no citations
        self.assertEqual(nx.number_of_edges(self.missing_citations_one), 3)

    def tearDown(self):
        pass


class TestAuthorCouplingGraph(unittest.TestCase):
    """
    Test the author_coupling network
    Assumes reader is functioning

    the //testin/wos_author_coupling.txt file has been constructed with
    the following properties:
        the first paper shares 2 authors with the second and 1 with the third
        the second paper shares 1 author with the third
        the fourth paper shares 0 authors with any other paper
    """
    def setUp(self):
        # read data from docs folder
        wos_data = rd.parse_wos('./testin/wos_author_coupling.txt')
        meta_list = rd.wos2meta(wos_data)

        self.ayjid_zero = nt.nx_author_coupling(meta_list,
                                                0,
                                                'ayjid')

        self.ayjid_one = nt.nx_author_coupling(meta_list,
                                               1,
                                               'ayjid')

        self.ayjid_two = nt.nx_author_coupling(meta_list,
                                               2,
                                               'ayjid')

        self.ayjid_attribs = nt.nx_author_coupling(meta_list,
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'date')
    def test_ayjid_zero(self):
        # with four papers there are 4 nodes
        self.assertEqual(nx.number_of_nodes(self.ayjid_zero), 4)

        # every paper shares at least 0 >= 0 authors with other papers
        # so we expect 4 choose 2 = 6 edges
        self.assertEqual(nx.number_of_edges(self.ayjid_zero), 6)

    def test_ayjid_one(self):
        # four nodes: one for each paper
        self.assertEqual(nx.number_of_nodes(self.ayjid_one), 4)

        # as noted in doc string, only papers 1 2 and 3 share one author
        # among them; we expect 3 edges
        self.assertEqual(nx.number_of_edges(self.ayjid_one), 3) 

    def test_ayjid_two(self):
        # four nodes: one for each paper
        self.assertEqual(nx.number_of_nodes(self.ayjid_two), 4)

        # as noted in the doc string, one papers 1 and 2 share two authors
        # we expect 1 edge
        self.assertEqual(nx.number_of_edges(self.ayjid_two), 1)

    def test_ayjid_attribs(self):
        # paper 1 meta data
        node1_atitle = ('Marine ecosystem health status assessment' + 
                        'through integrative biomarker indices: a' + 
                        'comparative study after the Prestige oil' + 
                        'spill "Mussel Watch"')
        node1_date = 2013
        node1_expected_attribs = {'atitle':node1_atitle,
                                  'date':node1_date}
        node1_ayjid = 'MARIGOMEZ I 2013 ECOTOXICOLOGY'

        # paper 2 meta data
        node2_atitle = ('Evaluation of organic contamination in urban' + 
                        'groundwater surrounding a municipal landfill,' + 
                        'Zhoukou, China')
        node2_date = 2013
        node2_expected_attribs = {'atitle':node2_atitle,
                                  'date':node2_date}
        node2_ayjid = 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'

        # paper 3 meta data
        node3_atitle = ('Multilevel governance and management of shared' + 
                        'stocks with integrated markets: The European' + 
                        'anchovy case')
        node3_date = 2013
        node3_expected_attribs = {'atitle':node3_atitle,
                                  'date':node3_date}
        node3_ayjid = 'MULAZZANI L 2013 MARINE POLICY'

        # paper 4 meta data
        node4_atitle = ('Application of multiple geochemical markers to' + 
                        'investigate organic pollution in a dynamic coastal' + 
                        'zone')
        node4_date = 2013
        node4_expected_attribs = {'atitle':node4_atitle,
                                  'date':node4_date}
        node4_ayjid = 'LIU L 2013 ENVIRONMENTAL TOXICOLOGY AND CHEMISTRY'

        # test attribute expectations
        node_id_list = [node1_ayjid, node2_ayjid, node3_ayjid, node4_ayjid]
        node_attrib_list = [node1_expected_attribs, node2_expected_attribs,
                            node3_expected_attribs, node4_expected_attribs]
        for i in xrange(len(node_id_list)):
            node = node_id_list[i]
            obtained_attribs = self.ayjid_attribs.node[node]
            expected_attribs = node_attrib_list[i]
            self.assertItemsEqual(expected_attribs, obtained_attribs)

    def tearDown(self):
        pass


class TestAuthorCocitation(unittest.TestCase):
    """
    Test the author cocitation (analysis) network
    """
    pass

if __name__ == '__main__':
    unittest.main()
