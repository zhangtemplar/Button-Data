# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Process the patents data from http://www.patentsview.org/download/
"""
import os
from base.util import create_logger, format_datetime, remove_empty_string_from_array, format_html_table, unique
from base.template import create_product, create_user
import json


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

    def init_npr_subcategory(self, data_name):
        if os.path.exists(data_name[:-3] + 'json'):
            self.npr_subcategory = json.load(open(data_name[:-3] + 'json', 'r'))
            return
        first_line = True
        with open(data_name, 'r') as fi:
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                self.npr_subcategory[data[0]] = data[1]
        json.dump(self.npr_subcategory, open(data_name[:-3] + 'json', 'w'))

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
        self.init_cpc_subgroup(os.path.join(data_path, 'cpc_subsection.tsv'))
        self.nber_category = {}
        self.init_nber_category(os.path.join(data_path, 'nbr_category.tsv'))
        self.nber_subcategory = {}
        self.init_npr_subcategory(os.path.join(data_path, 'nbr_subcategory.tsv'))
        self.uspc_class = {}
        self.init_uspc_class(os.path.join(data_path, 'uspc_class.tsv'))
        self.uspc_subclass = {}
        self.init_uspc_subclass(os.path.join(data_path, 'uspc_subclass.tsv'))
        self.wipo_field = {}
        self.init_wipo_field(os.path.join(data_path, 'wipo_field.tsv'))
        self.uspto_class = {}
        self.init_uspto_class(os.path.join(data_path, 'mainclass_current.tsv'))

    PATENT_HEADER = [
        'id', 'type', 'number', 'country', 'date', 'abstract', 'title', 'kind', 'num_claims', 'filename', 'withdrawn']
    US_TERM_OF_GRANT_HEADER = ['lapse_of_patent', 'disclaimer_date', 'term_disclaimer', 'term_grant', 'term_extension']

    def process_patent(self):
        result = {}
        # load the patent
        with open(os.path.join(self.data_path, 'patent.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                d = {k: v for k, v in zip(self.PATENT_HEADER, line.split('\t'))}
                patent = create_product()
                patent['tag'].append(d['type'])
                patent['ref'].append(d['number'])
                patent['addr']['country'] = d['country']
                patent['updated'] = format_datetime(d['date'])
                patent['abs'] = d['abstract']
                patent['name'] = d['title']
                patent['tag'].append(d['kind'])
                patent['tag'] = remove_empty_string_from_array(patent['tag'])
                result[patent['id']] = patent
        json.dump(result, open(os.path.join(self.data_path, 'patent.json'), 'w'))
        # load the application
        with open(os.path.join(self.data_path, 'application.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_created = format_datetime(data[5])
                result[patent_id]['created'] = patent_created
        json.dump(result, open(os.path.join(self.data_path, 'application.json'), 'w'))
        # load the brief summary
        with open(os.path.join(self.data_path, 'brf_sum_text.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_intro = data[2]
                result[patent_id]['intro'] += patent_intro
        json.dump(result, open(os.path.join(self.data_path, 'brf_sum_text.json'), 'w'))
        # load the claim
        with open(os.path.join(self.data_path, 'claim.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_claim = data[2]
                result[patent_id]['asset']['market'] += patent_claim
        json.dump(result, open(os.path.join(self.data_path, 'claim.json'), 'w'))
        # load the cpc tag
        with open(os.path.join(self.data_path, 'cpc_current.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_tag = []
                patent_tag.append(self.CPC_CLASSIFICATION_SECTION[data[2]])
                patent_tag.append(self.cpc_subsection[data[3]])
                patent_tag.append(self.cpc_group[data[4]])
                patent_tag.append(self.cpc_subgroup[data[5]])
                result[patent_id]['tag'].extend(patent_tag)
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        json.dump(result, open(os.path.join(self.data_path, 'cpc_current.json'), 'w'))
        # load the foreign priority
        with open(os.path.join(self.data_path, 'foreign_priority.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                result[patent_id]['tag'].append(data[3])
                result[patent_id]['tag'].append(data[5])
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
                result[patent_id]['asset']['lic'].append(data[4])
        json.dump(result, open(os.path.join(self.data_path, 'foreign_priority.json'), 'w'))
        # load the government interest
        with open(os.path.join(self.data_path, 'government_interest.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[0]
                result[patent_id]['asset']['market'].append(data[1])
        json.dump(result, open(os.path.join(self.data_path, 'government_interest.json'), 'w'))
        # load the us_term_of_grant
        with open(os.path.join(self.data_path, 'us_term_of_grant.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                detail = {k: v for k, v in zip(self.US_TERM_OF_GRANT_HEADER, data[2:])}
                result[patent_id]['asset']['market'].append(format_html_table(detail))
        json.dump(result, open(os.path.join(self.data_path, 'us_term_of_grant.json'), 'w'))
        # load the nber tag
        with open(os.path.join(self.data_path, 'nber.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_tag = []
                patent_tag.append(self.nber_category[data[2]])
                patent_tag.append(self.nber_subcategory[data[3]])
                result[patent_id]['tag'].extend(patent_tag)
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        json.dump(result, open(os.path.join(self.data_path, 'nber.json'), 'w'))
        # load the uspc
        with open(os.path.join(self.data_path, 'uspc.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_tag = []
                patent_tag.append(self.uspc_class[data[2]])
                patent_tag.append(self.uspc_subclass[data[3]])
                result[patent_id]['tag'].extend(patent_tag)
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        json.dump(result, open(os.path.join(self.data_path, 'uspc.json'), 'w'))
        # load the uspc
        with open(os.path.join(self.data_path, 'uspc_current.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[1]
                patent_tag = []
                patent_tag.append(self.uspc_class[data[2]])
                patent_tag.append(self.uspc_subclass[data[3]])
                result[patent_id]['tag'].extend(patent_tag)
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        json.dump(result, open(os.path.join(self.data_path, 'uspc_current.json'), 'w'))
        # load the wipo
        with open(os.path.join(self.data_path, 'wipo.tsv'), 'r') as fi:
            first_line = True
            for line in fi:
                if first_line:
                    first_line = False
                    continue
                data = line.split('\t')
                patent_id = data[0]
                result[patent_id]['tag'].append(self.wipo_field[data[1]])
                result[patent_id]['tag'] = unique(result[patent_id]['tag'])
        json.dump(result, open(os.path.join(self.data_path, 'wipo.json'), 'w'))
        return result

