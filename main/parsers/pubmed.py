# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
This module parses the medline reference and citation data.
"""
import os
from datetime import datetime
from typing import *
import json

import xmltodict
from pymongo import MongoClient

from base.template import create_product


class Pubmed(object):
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)

    def process(self, data_file: str):
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
                        p['intro'] += article['MedlineCitation']['CoiStatement']['b']
                    elif '#text' in article['MedlineCitation']['CoiStatement']:
                        p['intro'] += article['MedlineCitation']['CoiStatement']['#text']
                else:
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

        try:
            xmltodict.parse(open(data_file, "rb"), item_depth=2, item_callback=process_one_article)
        except xmltodict.ParsingInterrupted:
            pass
        except Exception as e:
            print(result[-1]['article']['name'])
            raise e
        return result

    @staticmethod
    def _text_from_list_or_dict(data: dict or list, field: str=None) -> List[str]:
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
            if field is not None:
                return Pubmed._text_from_list_or_dict(data[field])
            elif '#text' in data:
                return [data['#text']]
            elif 'b' in data:
                return [data['b']]
            else:
                return []
        elif isinstance(data, list or tuple):
            result = []
            for r in data:
                result.extend(Pubmed._text_from_list_or_dict(r))
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
        else:
            if 'ArticleIdList' not in data:
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
                if isinstance(a['AffiliationInfo'], dict):
                    user['affiliation'].append(a['AffiliationInfo']['Affiliation'])
                else:
                    user['affiliation'].extend([d['Affiliation'] for d in a['AffiliationInfo']])
            # TODO: parse address and company from AffiliationInfo
            return user

        if isinstance(data, dict):
            return [parse_user(data)]
        elif isinstance(data, list or tuple):
            return [parse_user(d) for d in data]
        else:
            return []


if __name__ == '__main__':
    result = Pubmed('mongodb://zhangtemplar:Button2015@eve.zhqiang.org:27017/data?authSource=admin').process(
        os.path.expanduser('~/Downloads/pubmed19n1053.xml'))
    with open(os.path.expanduser('~/Downloads/pubmed19n1053.json'), 'w') as fo:
        json.dump(result, fo)
