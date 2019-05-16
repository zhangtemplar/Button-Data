# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Process the patents data from http://www.patentsview.org/download/
"""
import json
import os
from typing import *

from base.template import create_product
from base.util import create_logger, format_datetime, remove_empty_string_from_array, format_html_table, unique


class PatentsView(object):

    # classification of assignee type
    ASSIGNEE_TYPE = {
        '1': 'Unassigned',
        '2': 'US Company or Corporation',
        '3': 'Foreign Company or Corporation',
        '4': 'US Individual',
        '5': 'Foreign Individual',
        '6': 'US  Federal Government',
        '7': 'Foreign Government',
        '8': 'US County Government',
        '9': 'US State Government'
    }

    # cpc classification id
    CPC_CLASSIFICATION_SECTION = {
        'A': 'Human Necessitites',
        'B': 'Performing Operations; Transporting',
        'C': 'hemistry; Metallurgy',
        'D': 'Textiles; Paper',
        'E': 'Fixed Constructions',
        'F': 'Mechanical Engineering; Lighting; Heating; Weapons; Blasting Engines or Pumps',
        'G': 'Physics',
        'H': 'Electricity',
        'Y': 'General Tagging of New Technological Developments',
    }

    IPCR_CLASSIFICATION_SECTION = {
        'A': 'Human Necessitites',
        'B': 'Performing Operations; Transporting',
        'C': 'Chemistry; Metallurgy',
        'D': 'Textiles; Paper',
        'E': 'Fixed Constructions',
        'F': 'Mechanical Engineering; Lighting; Heating; Weapons; Blasting',
        'G': 'Physics',
        'H': 'Electricity',
    }

    def init_cpc_group(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.cpc_group = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.cpc_group[data[0]] = data[1]
        json.dump(self.cpc_group, open(data_name[:-3] + 'json', 'w'))

    def init_cpc_subgroup(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.cpc_subgroup = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.cpc_subgroup[data[0]] = data[1]
        json.dump(self.cpc_subgroup, open(data_name[:-3] + 'json', 'w'))

    def init_cpc_subsection(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.cpc_subsection = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.cpc_subsection[data[0]] = data[1]
        json.dump(self.cpc_subsection, open(data_name[:-3] + 'json', 'w'))

    def init_nber_category(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.nber_category = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.nber_category[data[0]] = data[1]
        json.dump(self.nber_category, open(data_name[:-3] + 'json', 'w'))

    def init_nber_subcategory(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.nber_subcategory = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.nber_subcategory[data[0]] = data[1]
        json.dump(self.nber_subcategory, open(data_name[:-3] + 'json', 'w'))

    def init_uspc_class(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.uspc_class = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.uspc_class[data[0]] = data[1]
        json.dump(self.uspc_class, open(data_name[:-3] + 'json', 'w'))

    def init_uspc_subclass(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.uspc_subclass = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.uspc_subclass[data[0]] = data[1]
        json.dump(self.uspc_subclass, open(data_name[:-3] + 'json', 'w'))

    def init_wipo_field(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.wipo_field = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.wipo_field[data[0]] = data[1]
        json.dump(self.wipo_field, open(data_name[:-3] + 'json', 'w'))

    def init_uspto_class(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.uspto_class = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.uspto_class[data[0]] = data[1]
        json.dump(self.uspto_class, open(data_name[:-3] + 'json', 'w'))

    def __init__(self, data_path):
        self.logger = create_logger('patents_view.log')
        if not os.path.exists(data_path):
            self.logger.critical('{} doesnot exist'.format(data_path))
            return
        self.data_path = data_path
        self.cpc_group = {}
        self.init_cpc_group(os.path.join(data_path, 'cpc_group.tsv'))
        self.cpc_subgroup = {}
        self.init_cpc_subgroup(os.path.join(data_path, 'cpc_subgroup.tsv'))
        self.cpc_subsection = {}
        self.init_cpc_subsection(os.path.join(data_path, 'cpc_subsection.tsv'))
        self.nber_category = {}
        self.init_nber_category(os.path.join(data_path, 'nber_category.tsv'))
        self.nber_subcategory = {}
        self.init_nber_subcategory(os.path.join(data_path, 'nber_subcategory.tsv'))
        self.uspc_class = {}
        self.init_uspc_class(os.path.join(data_path, 'mainclass_current.tsv'))
        self.uspc_subclass = {}
        self.init_uspc_subclass(os.path.join(data_path, 'subclass_current.tsv'))
        self.wipo_field = {}
        self.init_wipo_field(os.path.join(data_path, 'wipo_field.tsv'))
        self.uspto_class = {}
        self.init_uspto_class(os.path.join(data_path, 'mainclass_current.tsv'))

    PATENT_HEADER = [
        'id', 'type', 'number', 'country', 'date', 'abstract', 'title', 'kind', 'num_claims', 'filename', 'withdrawn']
    US_TERM_OF_GRANT_HEADER = ['lapse_of_patent', 'disclaimer_date', 'term_disclaimer', 'term_grant', 'term_extension']

    @staticmethod
    def process_file(
            input_name: str,
            output_name: str,
            result: dict,
            callback: Callable,
            save_callback: Callable = None):
        if os.path.exists(output_name):
            result = json.load(open(output_name, 'r'))
        with open(input_name, 'r') as fi:
            for count, line in enumerate(fi):
                if count == 0:
                    continue
                if count <= len(result):
                    continue
                if count % 100000 == 0:
                    json.dump(result, open(output_name, 'w'))
                    if save_callback is not None:
                        save_callback(count)
                callback(line.split('\t'), result)
        return result

    def process_patent(self):
        patents = {}
        # load the patent

        def patent_callback(data: List[str], result: dict) -> None:
            if len(data) != len(self.PATENT_HEADER):
                self.logger.error('fail to parse {}'.format(data))
                return
            d = {k: v for k, v in zip(self.PATENT_HEADER, data)}
            patent = create_product()
            patent['tag'].append(d['type'])
            patent['ref'] = d['number']
            patent['addr']['country'] = d['country']
            patent['updated'] = format_datetime(d['date'])
            patent['abs'] = d['abstract']
            patent['name'] = d['title']
            patent['tag'].append(d['kind'])
            patent['tag'] = remove_empty_string_from_array(patent['tag'])
            result[patent['ref']] = patent
        self.logger.critical('patent')
        patents = self.process_file(
            os.path.join(self.data_path, 'patent.tsv'),
            os.path.join(self.data_path, 'patent.json'),
            patents,
            patent_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'patent.json'), 'w'))

        # load the application
        def application_callback(data: List[str], result: dict):
            patent_id = data[1]
            patent_created = format_datetime(data[5])
            result[patent_id]['created'] = patent_created
        self.logger.critical('application')
        patents = self.process_file(
            os.path.join(self.data_path, 'application.tsv'),
            os.path.join(self.data_path, 'application.json'),
            patents,
            application_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'application.json'), 'w'))

        # load the brief summary
        def summary_callback(data: List[str], result: dict):
            patent_id = data[1]
            patent_intro = data[2]
            result[patent_id]['intro'] += patent_intro
        self.logger.critical('brf_sum_text')
        self.process_file(
            os.path.join(self.data_path, 'brf_sum_text.tsv'),
            os.path.join(self.data_path, 'brf_sum_text.json'),
            patents,
            summary_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'brf_sum_text.json'), 'w'))

        # load the claim
        def claim_callback(data: List[str], result: dict):
            patent_id = data[1]
            patent_claim = data[2]
            result[patent_id]['asset']['market'] += patent_claim
        self.logger.critical('claim')
        patents = self.process_file(
            os.path.join(self.data_path, 'claim.tsv'),
            os.path.join(self.data_path, 'claim.json'),
            patents,
            claim_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'claim.json'), 'w'))

        # load the cpc tag
        def cpc_callback(data: List[str], result: dict):
            patent_id = data[1]
            result[patent_id]['tag'].append(self.CPC_CLASSIFICATION_SECTION[data[2]])
            result[patent_id]['tag'].append(self.cpc_subsection[data[3]])
            result[patent_id]['tag'].append(self.cpc_group[data[4]])
            result[patent_id]['tag'].append(self.cpc_subgroup[data[5]])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        self.logger.critical('cpc_current')
        patents = self.process_file(
            os.path.join(self.data_path, 'cpc_current.tsv'),
            os.path.join(self.data_path, 'cpc_current.json'),
            patents,
            cpc_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'cpc_current.json'), 'w'))

        # load the foreign priority
        def foreign_priority_callback(data: List[str], result: dict):
            patent_id = data[1]
            result[patent_id]['tag'].append(data[3])
            result[patent_id]['tag'].append(data[5])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
            result[patent_id]['asset']['lic'].append(data[4])
        self.logger.critical('foreign_priority')
        patents = self.process_file(
            os.path.join(self.data_path, 'foreign_priority.tsv'),
            os.path.join(self.data_path, 'foreign_priority.json'),
            patents,
            foreign_priority_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'foreign_priority.json'), 'w'))

        # load the government interest
        def government_interest_callback(data: List[str], result: dict):
            patent_id = data[0]
            result[patent_id]['asset']['market'].append(data[1])
        self.logger.critical('government_interest')
        patents = self.process_file(
            os.path.join(self.data_path, 'government_interest.tsv'),
            os.path.join(self.data_path, 'government_interest.json'),
            patents,
            government_interest_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'government_interest.json'), 'w'))

        # load the us_term_of_grant
        def us_term_of_grant_interest_callback(data: List[str], result: dict):
            patent_id = data[1]
            detail = {k: v for k, v in zip(self.US_TERM_OF_GRANT_HEADER, data[2:])}
            result[patent_id]['asset']['market'].append(format_html_table(detail))
        self.logger.critical('us_term_of_grant')
        patents = self.process_file(
            os.path.join(self.data_path, 'us_term_of_grant.tsv'),
            os.path.join(self.data_path, 'us_term_of_grant.json'),
            patents,
            us_term_of_grant_interest_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'us_term_of_grant.json'), 'w'))

        # load the nber tag
        def nber_callback(data: List[str], result: dict):
            patent_id = data[1]
            result[patent_id]['tag'].append(self.nber_category[data[2]])
            result[patent_id]['tag'].append(self.nber_subcategory[data[3]])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        self.logger.critical('nber')
        patents = self.process_file(
            os.path.join(self.data_path, 'nber.tsv'),
            os.path.join(self.data_path, 'nber.json'),
            patents,
            nber_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'nber.json'), 'w'))

        # load the uspc
        def uspc_callback(data: List[str], result: dict):
            patent_id = data[1]
            result[patent_id]['tag'].append(self.uspc_class[data[2]])
            result[patent_id]['tag'].append(self.uspc_subclass[data[3]])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        self.logger.critical('uspc')
        patents = self.process_file(
            os.path.join(self.data_path, 'uspc.tsv'),
            os.path.join(self.data_path, 'uspc.json'),
            patents,
            uspc_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'uspc.json'), 'w'))

        # load the uspc
        def uspc_current_callback(data: List[str], result: dict):
            patent_id = data[1]
            result[patent_id]['tag'].append(self.uspc_class[data[2]])
            result[patent_id]['tag'].append(self.uspc_subclass[data[3]])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        self.logger.critical('uspc_current')
        patents = self.process_file(
            os.path.join(self.data_path, 'uspc_current.tsv'),
            os.path.join(self.data_path, 'uspc_current.json'),
            patents,
            uspc_current_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'uspc_current.json'), 'w'))

        # load the wipo
        def wipo_callback(data: List[str], result: dict):
            patent_id = data[0]
            result[patent_id]['tag'].append(self.wipo_field[data[1]])
            result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        self.logger.critical('wipo')
        patents = self.process_file(
            os.path.join(self.data_path, 'wipo.tsv'),
            os.path.join(self.data_path, 'wipo.json'),
            patents,
            wipo_callback,
            lambda count: self.logger.debug('processed {} data'.format(count)))
        json.dump(patents, open(os.path.join(self.data_path, 'wipo.json'), 'w'))

        return patents

