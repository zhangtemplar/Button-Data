# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
This module parses the medline reference and citation data.
"""
import pickle
import json
import os
from datetime import datetime
from typing import *
from collections import defaultdict

import xmltodict
from pymongo import MongoClient

from base.template import create_product, create_user, create_relationship, add_record
from base.union_find import UnionFind
from base.util import create_logger, normalize_email, normalize_phone, parse_us_address


class Pubmed(object):
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.authors = UnionFind()
        self.logger = create_logger('pubmed.log')

    def process(self, data_directory: str):
        """
        Main entrance, parse the pubmed xml files, upload the data to database, build the relationship in it.

        :param data_directory: directory to the xml files
        :return: None
        """
        data_file = []
        for file in os.listdir(data_directory):
            if not file.endswith('xml'):
                continue
            file = os.path.join(data_directory, file)
            data_file.append(file[:-3] + 'cp')
            if os.path.exists(file[:-3] + 'cp'):
                continue
            result = self.preprocess(file)
            with open(file[:-3] + 'cp', 'wb') as fo:
                pickle.dump(result, fo)
        self.process_author(data_file)
        citation = self.compute_citation(data_file)
        self.compute_author_impact(data_file, citation)

        article_ids = self.upload_article(data_file)
        self.upload_reference(data_file, article_ids)

        author_ids = self.upload_author()
        self.upload_authorship(data_file, author_ids, article_ids)

    def compute_author_impact(self, data_file: List[str], citations: Dict) -> Dict:
        author_impact = defaultdict(lambda: {'citation': 0, 'keyword': set()})
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                users = d['author']
                article = d['article']
                for u in users:
                    affiliation = u['affiliation']
                    if len(affiliation) < 1:
                        key = (u['name'], article['name'])
                    else:
                        key = (u['name'], affiliation[0])
                    root = self.authors.find(key)
                    author_impact[root]['citation'] += citations.get(article['ref'], 0)
                    author_impact[root]['keyword'].update(article['tag'])
        pickle.dump(dict(author_impact), open('pubmed_author_citation.cp', 'wb'))
        return author_impact

    def compute_citation(self, data_file: List[str]) -> Dict:
        """
        Compute the citation information for the article.

        :param data_file:
        :param article_ids: a dict mapping of pubmed id of the article to the id in the database
        :return: list of names of files generated from preprocess
        """
        citations = defaultdict(lambda: 0)
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                reference = d['reference']
                for u in reference:
                    citations[u] += 1
        pickle.dump(dict(citations), open('pubmed_article_citation.cp', 'wb'))
        return citations

    def upload_reference(self, data_file: List[str], article_ids: dict):
        """
        Uploads the reference information for the article.

        :param data_file:
        :param article_ids: a dict mapping of pubmed id of the article to the id in the database
        :return: list of names of files generated from preprocess
        """
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                reference = [r for r in d['reference'] if isinstance(r, str)]
                article = d['article']
                if article['ref'] not in article_ids:
                    self.logger.warning('article {} is not found in server'.format(article['ref']))
                    continue
                relationship = []
                for u in reference:
                    if article['ref'] not in article_ids:
                        self.logger.warning('reference {} is not found in server'.format(article_ids[u]))
                        continue
                    r = create_relationship()
                    r['srcId'] = article_ids[article['ref']]
                    r['dstId'] = article_ids[u]
                    r['name'] = 'Reference'
                    r['type'] = 14
                    relationship.append(r)
                response = add_record('relationship', relationship)
                if response['_status'] != 'OK':
                    self.logger.error('fail to create author article relationship for {}'.format(article['name']))

    def upload_article(self, data_file: List[str]) -> dict:
        """
        Uploads the article to server and returns the mapping of pubmed id of the article to the id in the database

        :param data_file: list of names of files generated from preprocess
        :param author_ids: dictionary of (author name, author first affiliation) to author's id in database
        :return: a dict mapping of pubmed id of the article to the id in the database
        """
        article_ids = {}
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                article = d['article']
                if len(article['abs']) < 1:
                    article['abs'] = article['name']
                article['addr']['city'] = 'unknown'
                article['addr']['country'] = 'unknown'
                response = add_record('entity', article)
                if response['_status'] != 'OK':
                    self.logger.error('fail to create article for {} due to {}'.format(article['name'], response))
                    continue
                article_ids[article['ref']] = response['_items']['_id']
        pickle.dump(article_ids, open('pubmed_article_ids.cp', 'wb'))
        return article_ids

    def upload_authorship(self, data_file: List[str], author_ids: dict, article_ids: dict):
        """
        Uploads the authorship to the server.

        :param data_file: names of json files
        :param author_ids: mapping of author to its _id on server
        :param article_ids: mapping of article to its _id on server
        :return: None
        """
        # create author-article relationship
        relationship = []
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                users = d['author']
                article = d['article']
                if article['ref'] not in article_ids:
                    self.logger.warning('article {} is not found in server'.format(article['ref']))
                    continue
                for u in users:
                    # find _id of author
                    affiliation = u['affiliation']
                    if len(affiliation) < 1:
                        key = (u['name'], article['name'])
                    else:
                        key = (u['name'], affiliation[0])
                    key = self.authors.find(key)
                    if key not in author_ids:
                        self.logger.warning('user {} is not found in server'.format(u['name']))
                        continue
                    user_id = author_ids[key]
                    r = create_relationship()
                    r['srcId'] = user_id
                    r['dstId'] = article_ids[article['ref']]
                    r['name'] = 'Author'
                    r['type'] = 5
                    relationship.append(r)
                if len(relationship) > 1000:
                    response = add_record('relationship', relationship)
                    if response['_status'] != 'OK':
                        self.logger.error('fail to create authorship due to {}'.format(response))
                    relationship = []
        if len(relationship) > 0:
            response = add_record('relationship', relationship)
            if response['_status'] != 'OK':
                self.logger.error('fail to create authorship due to {}'.format(response))

    def process_author(self, data_file: List[str]) -> None:
        """
        Finds the unique authors.

        :param data_file: list of files containing the data from preprocess step
        """
        for file in data_file:
            self.logger.info('Process {}'.format(file))
            data = pickle.load(open(file, 'rb'))
            for d in data:
                article = d['article']
                users = d['author']
                for u in users:
                    if u is None:
                        continue
                    # merge the users
                    name = u['name']
                    affiliation = u['affiliation']
                    if len(affiliation) == 0:
                        self.authors.find((name, article['name']))
                    for a in affiliation:
                        if a is not affiliation[0]:
                            self.authors.union((name, a), (name, affiliation[0]))

    def upload_author(self) -> dict:
        """
        Upload the unique authors to the database.

        :param data_file: list of files containing the data from preprocess step
        :return: a dictionary using the ref of author as key and its _id in database as value
        """

        # find unique author
        author_dict = self.authors.all_elements()

        # upload the user to the server
        users = []
        user_ids = {}
        for a in author_dict:
            user = create_user()
            user['name'] = a[0]
            user['abs'] = a[1]
            user['ref'] = a[1]
            user['contact']['email'] = normalize_email(a[1])
            user['contact']['phone'] = normalize_phone(a[1])
            user['onepage']['bg'] = json.dumps([u[1] for u in author_dict[a]])
            users.append(user)
            if len(users) >= 1000:
                response = add_record('entity', users)
                if response['_status'] != 'OK':
                    self.logger.error('fail to create user'.format(a))
                else:
                    for u, r in zip(users, response['_items']):
                        user_ids[(u['name'], u['abs'])] = r['_id']
                    users = []
        if len(users) > 0:
            response = add_record('entity', users)
            if response['_status'] != 'OK':
                self.logger.error('fail to create user'.format(a))
            else:
                for u, r in zip(users, response['_items']):
                    user_ids[(u['name'], u['abs'])] = r['_id']
        del users
        pickle.dump(user_ids, open('pubmed_author_ids.cp', 'wb'))

        return user_ids

    def preprocess(self, data_file: str) -> List[dict]:
        """
        Extracts the article data from xml and save to json.

        :param data_file: xml file name
        :return: the list article extracts
        """
        result = []

        def process_one_article(_, article):
            if 'MedlineCitation' not in article:
                return False
            p = create_product()
            p['ref'] = article['MedlineCitation']['PMID']["#text"]
            if 'DateCompleted' in article['MedlineCitation']:
                date = article['MedlineCitation']['DateCompleted']
                p['created'] = datetime(
                    int(date['Year']), int(date['Month']), int(date['Day'])).strftime("%a, %d %b %Y %H:%M:%S GMT")
            if 'DateRevised' in article['MedlineCitation']:
                date = article['MedlineCitation']['DateRevised']
                p['created'] = datetime(
                    int(date['Year']), int(date['Month']), int(date['Day'])).strftime("%a, %d %b %Y %H:%M:%S GMT")
            p['name'] = article['MedlineCitation']['Article']['ArticleTitle']
            if isinstance(p['name'], dict):
                if "#text" in p['name']:
                    p['name'] = p['name']['#text']
                elif "b" in p['name']:
                    p['name'] = p['name']["b"]
                else:
                    return True
            p['asset']['type'] = 4

            if 'Abstract' in article['MedlineCitation']['Article']:
                self._abstract(article['MedlineCitation']['Article']['Abstract'], p)
            if 'CoiStatement' in article['MedlineCitation']:
                if isinstance(article['MedlineCitation']['CoiStatement'], dict):
                    if 'b' in article['MedlineCitation']['CoiStatement']:
                        if isinstance(article['MedlineCitation']['CoiStatement']['b'], list):
                            p['intro'] += '\n'.join(article['MedlineCitation']['CoiStatement']['b'])
                        else:
                            p['intro'] += article['MedlineCitation']['CoiStatement']['b']
                    elif '#text' in article['MedlineCitation']['CoiStatement']:
                        p['intro'] += article['MedlineCitation']['CoiStatement']['#text']
                elif isinstance(article['MedlineCitation']['CoiStatement'], str):
                    p['intro'] += article['MedlineCitation']['CoiStatement']

            authors = []
            if 'AuthorList' in article['MedlineCitation']['Article']:
                authors.extend(self._authors(article['MedlineCitation']['Article']['AuthorList']['Author']))
            if 'InvestigatorList' in article['MedlineCitation']:
                authors.extend(self._authors(article['MedlineCitation']['InvestigatorList']['Investigator']))

            if 'MeshHeadingList' in article['MedlineCitation']:
                p['tag'].extend(self._text_from_list_or_dict(
                    article['MedlineCitation']['MeshHeadingList']['MeshHeading'],
                    "DescriptorName"))
            if 'SupplMeshList' in article['MedlineCitation']:
                p['tag'].extend(self._text_from_list_or_dict(
                    article['MedlineCitation']['SupplMeshList']['SupplMeshName']))

            p['asset']['ind'].extend(self._text_from_list_or_dict(
                article['MedlineCitation']['Article']['PublicationTypeList']['PublicationType']))
            if 'GeneSymbolList' in article['MedlineCitation']:
                p['asset']['ind'].extend(self._text_from_list_or_dict(
                    article['MedlineCitation']['GeneSymbolList']['GeneSymbol']))
            if 'ChemicalList' in article['MedlineCitation']:
                p['asset']['ind'].extend(self._text_from_list_or_dict(
                    article['MedlineCitation']['ChemicalList']['Chemical'],
                    'NameOfSubstance'))
            if 'KeywordList' in article['MedlineCitation']:
                p['asset']['ind'].extend(self._text_from_list_or_dict(
                    article['MedlineCitation']['KeywordList']['Keyword']))

            # TODO: journal information from article['MedlineCitation']['MedlineJournalInfo']
            p['asset']['lic'] = self._text_from_list_or_dict(article['PubmedData']['ArticleIdList']['ArticleId'])
            if 'OtherID' in article['PubmedData']:
                p['asset']['lic'].extend(self._text_from_list_or_dict(article['PubmedData']['OtherID']))

            if 'ReferenceList' in article['PubmedData']:
                references = self._references(article['PubmedData']['ReferenceList'])
            else:
                references = []
            result.append({"article": p, "reference": references, "author": authors})
            return True

        self.logger.info('process {}'.format(data_file))
        try:
            xmltodict.parse(open(data_file, "rb"), item_depth=2, item_callback=process_one_article)
        except xmltodict.ParsingInterrupted:
            pass
        except Exception as e:
            self.logger.error('Fail to process {}'.format(result[-1]['article']['name']))
            raise e
        return result

    @staticmethod
    def _text_from_list_or_dict(data: dict or list, field: str = None) -> List[str]:
        """
        Extracts text list from the input which could be either a dict or a dict nested in a list.

        :param data: input
        :param field: optionally the field where data should be extracted from input
        :return: the list of text extracted
        """
        if data is None:
            return []
        elif isinstance(data, str):
            return [data]
        elif isinstance(data, dict):
            if field is not None and field in data:
                return Pubmed._text_from_list_or_dict(data[field], field)
            elif '#text' in data:
                return [data['#text']]
            elif 'b' in data:
                return [data['b']]
            else:
                return []
        elif isinstance(data, list or tuple):
            result = []
            for r in data:
                result.extend(Pubmed._text_from_list_or_dict(r, field))
            return result
        else:
            return []

    @staticmethod
    def _references(data: dict) -> List:
        """
        ReferenceList can be a list of dict
        Reference can be a list of dict
        :param data:
        :return:
        """
        if isinstance(data, list):
            result = []
            for d in data:
                result.extend(Pubmed._references(d))
            return result
        elif 'Reference' in data:
            return Pubmed._references(data['Reference'])
        elif 'ArticleIdList' not in data:
            return []
        elif isinstance(data["ArticleIdList"]["ArticleId"], dict):
            if data["ArticleIdList"]["ArticleId"]["@IdType"] == "pubmed":
                return [data["ArticleIdList"]["ArticleId"]["#text"]]
            else:
                return []
        else:
            # prefer pubmed id
            return [r["#text"] for r in data["ArticleIdList"]["ArticleId"] if r["@IdType"] == "pubmed"]

    @staticmethod
    def _abstract(data: dict, product: dict) -> None:
        if not isinstance(data['AbstractText'], list):
            if data['AbstractText'] is None:
                return
            elif '#text' in data['AbstractText']:
                product['abs'] = data['AbstractText']['#text']
            else:
                product['abs'] = data['AbstractText']
            return
        for p in data['AbstractText']:
            if p is None:
                continue
            elif isinstance(p, str):
                if len(product['abs']) < 1:
                    product['abs'] = p
                else:
                    product['intro'] += p
            elif '#text' not in p:
                continue
            elif '@Label' in p:
                if p['@Label'] == 'OBJECTIVE':
                    product['abs'] = p['#text']
                elif p['@Label'] == 'BACKGROUND':
                    product['onepage']['bg'] = p['#text']
                elif p['@Label'] == 'UNASSIGNED':
                    product['intro'] += p['#text']
                elif p['@Label'] == 'METHODS':
                    product['onepage']['prod'] = p['#text']
                elif p['@Label'] == 'RESULTS':
                    product['onepage']['high'] = p['#text']
                elif p['@Label'] == 'CONCLUSIONS':
                    product['onepage']['team'] = p['#text']
                elif len(product['abs']) < 1:
                    product['abs'] = p['#text']
                else:
                    product['intro'] += p['#text']
            elif len(product['abs']) < 1:
                product['abs'] = p['#text']
            else:
                product['intro'] += p['#text']

    @staticmethod
    def _authors(data: List[dict]) -> List[dict]:
        def parse_user(a: dict) -> dict or None:
            if 'CollectiveName' in a:
                return None
            user = {'name': '', 'affiliation': []}
            if 'ForeName' in a:
                user['name'] = '{} {}'.format(a['ForeName'], a['LastName'])
            elif 'LastName' in a:
                user['name'] = a['LastName']
            if 'AffiliationInfo' in a:
                def parse_affiliation(aff):
                    if aff is None:
                        return None
                    if isinstance(aff, str):
                        return aff
                    if '#text' in aff:
                        return aff['#text']
                    return None

                if isinstance(a['AffiliationInfo'], dict):
                    user['affiliation'].append(parse_affiliation(a['AffiliationInfo']['Affiliation']))
                elif isinstance(a['AffiliationInfo'], tuple or list):
                    for d in a['AffiliationInfo']:
                        user['affiliation'].append(parse_affiliation(d['Affiliation']))
                elif isinstance(a['AffiliationInfo'], str):
                    user['affiliation'].append(parse_affiliation(a['AffiliationInfo']))
                affiliation = []
                for a in user['affiliation']:
                    if a is None:
                        continue
                    if isinstance(a, dict) and '#text' in a:
                        affiliation.append(a['#text'])
                    elif isinstance(a, str):
                        affiliation.append(a)
                user['affiliation'] = affiliation
            return user

        result = []
        if isinstance(data, dict):
            result.append(parse_user(data))
        elif isinstance(data, list or tuple):
            result.extend([parse_user(d) for d in data])
        return [r for r in result if r is not None]


def upload_user_to_server(file_name):
    data = pickle.load(open(file_name, 'rb'))
    # upload the user to the server
    users = []
    for a in data:
        user = create_user()
        user['name'] = a[0]
        user['abs'] = a[1]
        user['ref'] = a[1]
        user['contact']['email'] = normalize_email(a[1])
        user['contact']['phone'] = normalize_phone(a[1])
        user['tag'] = data[a]['keyword']
        user['onepage']['prod'] = data[a]['citation']
        # try to parse the address
        addr = parse_us_address(a[1])
        if addr is not None:
            user['addr'] = addr
    json.dump(users, open('pubmed_author.json', 'wb'))


if __name__ == '__main__':
    Pubmed('mongodb://zhangtemplar:Button2015@eve.zhqiang.org:27017/data?authSource=admin').process(
        os.path.expanduser('~/Downloads/pubmed'))
