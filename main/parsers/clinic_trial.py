# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import json
import logging
import os
from multiprocessing import Pool
from dateutil import parser
from collections import OrderedDict
import xmltodict

from base.template import create_user, create_product

log = logging.getLogger('clinic_trial')
log.setLevel(logging.DEBUG)


class ClinicalTrial(object):

    def __init__(self, source_directory):
        self.sourceDirectory = source_directory

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self) -> None:
        """
        Main function.
        """
        if os.path.exists(self.sourceDirectory + '.json'):
            log.warning('already processed {}'.format(self.sourceDirectory))
            return
        file_list = [os.path.join(self.sourceDirectory, file_name) for file_name in os.listdir(self.sourceDirectory) if
                     file_name.startswith("NCT")]
        result = []
        for file_name in file_list:
            log.info('process ' + file_name)
            result.append(self.process_file(file_name))
            # os.remove(file_name)
        with open(self.sourceDirectory + '.json', 'w') as fo:
            json.dump(result, fo, ensure_ascii=False)

    def histogram_indication(self, hist: dict=None) -> dict:
        """
        Computes the histogram of indication

        :param hist: base histogram is available, default {}
        :return: the computed histogram
        """
        file_list = [os.path.join(self.sourceDirectory, file_name) for file_name in os.listdir(self.sourceDirectory) if
                     file_name.startswith("NCT")]
        result = {} if hist is None else hist
        for file_name in file_list:
            log.info('process ' + file_name)
            trial = xmltodict.parse(open(file_name, "rb"))['clinical_study']
            if 'condition' not in trial:
                continue
            if isinstance(trial['condition'], list):
                for c in trial['condition']:
                    result[c] = result.get(c, 0) + 1
            else:
                result[trial['condition']] = result.get(trial['condition'], 0) + 1
        return result

    @staticmethod
    def _add_sponsor(data: dict) -> dict:
        """
        Add a sponsor for the clinical trial

        :param data: a dictionary contains the sponsor data
        :return: the added sponsor as Project
        """
        user = create_user()
        user['name'] = data['agency']
        user['type'] = 32
        if 'agency_class' in data:
            user['tag'] = data['agency_class']
        return user

    @staticmethod
    def _add_user(data: dict) -> dict:
        """
        Add an user's contact.

        :param data: a dictionary contains user information
        :return: an user
        """
        user = create_user()
        name = []
        if 'first_name' in data:
            name.append(data['first_name'])
        if 'middle_name' in data:
            name.append(data['middle_name'])
        if 'last_name' in data:
            name.append(data['last_name'])
        user['name'] = ' '.join(name)
        if 'role' in data:
            user['exp']['exp']['title'] = data['role']
        if 'affiliation' in data:
            user['exp']['exp']['company'] = data['affiliation']
        phone = []
        if 'phone' in data:
            phone.append(data['phone'])
        if 'phone_ext' in data:
            phone.append(data['phone_ext'])
        user['contact']['phone'] = '-'.join(phone)
        user['contact']['email'] = data['email'] if 'email' in data else ''
        if 'degrees' in data:
            if not user.title:
                user['edu']['degree'] = data['degrees']
        if len(user['name']) < 0:
            user['name'] = user['contact']['email'] if len(user['contact']['email']) > 0 else 'Anonymous'
        if len(user['abs']) < 0:
            user['abs'] = 'Principal Investigator'
        return user

    @staticmethod
    def _add_users_for_location(location: dict) -> list:
        users = []
        if 'contact' in location:
            users.append(ClinicalTrial._add_user(location['contact']))
            del location['contact']
        if 'contact_backup' in location:
            users.append(ClinicalTrial._add_user(location['contact_backup']))
            del location['contact_backup']
        if 'investigator' in location:
            if isinstance(location['investigator'], dict):
                users.append(ClinicalTrial._add_user(location['investigator']))
            else:
                users.extend([ClinicalTrial._add_user(user) for user in location['investigator']])
            del location['investigator']
        return users

    @staticmethod
    def _add_users(trial: dict) -> list:
        """
        Add contacts as users for the clinical trial.

        :param trial: a dictionary contains the clinical trial information
        """
        users = []
        if 'overall_official' in trial:
            if isinstance(trial['overall_official'], dict):
                users.append(ClinicalTrial._add_user(trial['overall_official']))
            else:
                users.extend([ClinicalTrial._add_user(user) for user in trial['overall_official']])
            del trial['overall_official']
        if 'overall_contact' in trial:
            users.append(ClinicalTrial._add_user(trial['overall_contact']))
        if 'overall_contact_backup' in trial:
            users.append(ClinicalTrial._add_user(trial['overall_contact_backup']))
            del trial['overall_contact_backup']
        if 'location' in trial:
            if isinstance(trial['location'], dict):
                users.extend(ClinicalTrial._add_users_for_location(trial['location']))
            else:
                [users.extend(ClinicalTrial._add_users_for_location(location)) for location in trial['location']]
        if 'clinical_results' in trial and 'point_of_contact' in trial['clinical_results']:
            users.append(ClinicalTrial._add_user(trial['clinical_results']['point_of_contact']))
            del trial['clinical_results']['point_of_contact']
        return users

    @staticmethod
    def _add_sponsors(trial: dict) -> list:
        """
        Add sponsors for this clinical trial.

        :param trial: a dictionary contains the clinical trial information
        :return: a Project which is the lead sponsor of the clinical trial
        """
        users = []
        # for principal investigator
        user = ClinicalTrial._add_sponsor(trial['sponsors']['lead_sponsor'])
        if 'overall_contact' in trial:
            if 'phone' in trial['overall_contact']:
                user['contact']['phone'] = trial['overall_contact']['phone']
            if 'phone_ext' in trial['overall_contact'] and len(trial['overall_contact']['phone_ext']) > 0:
                user['contact']['phone'] += '-' + trial['overall_contact']['phone_ext']
            if 'email' in trial['overall_contact']:
                user['contact']['email'] = trial['overall_contact']['email']
        # keep it for user
        # del trial['overall_contact']
        users.append(user)

        # for collaborators
        if 'collaborator' in trial['sponsors']:
            if isinstance(trial['sponsors']['collaborator'], dict):
                users.append(ClinicalTrial._add_sponsor(trial['sponsors']['collaborator']))
            else:
                users.extend([ClinicalTrial._add_sponsor(sponsor) for sponsor in trial['sponsors']['collaborator']])
        del trial['sponsors']
        return users

    @staticmethod
    def _find_type(trial: dict) -> list:
        """
        Find the types from the trial.

        :param trial: a dictionary contains the clinical trial information
        :return: types of trial as a list of strings
        """
        tag = [trial['study_type'], trial['overall_status']]
        if 'phase' in trial:
            tag.append(trial['phase'])
            del trial['phase']
        if 'last_known_status' in trial and trial['last_known_status'] != trial['overall_status']:
            tag.append(trial['last_known_status'])
        if 'last_known_status' in trial:
            del trial['last_known_status']
        del trial['study_type']
        if 'keyword' in trial:
            if isinstance(trial['keyword'], list):
                tag.extend(trial['keyword'])
            else:
                tag.append(trial['keyword'])
            del trial['keyword']
        if 'intervention' in trial:
            if isinstance(trial['intervention'], dict):
                tag.append(trial['intervention']['intervention_type'])
            else:
                tag.extend([intervention['intervention_type'] for intervention in trial['intervention']])
            # it contains more information then type
            # del trial['intervention']
        if 'biospec_retention' in trial:
            tag.append(trial['biospec_retention'])
            del trial['biospec_retention']
        if 'condition_browse' in trial:
            if isinstance(trial['condition_browse']['mesh_term'], list):
                tag.extend(trial['condition_browse']['mesh_term'])
            else:
                tag.append(trial['condition_browse']['mesh_term'])
            del trial['condition_browse']
        if 'intervention_browse' in trial:
            if isinstance(trial['intervention_browse']['mesh_term'], list):
                tag.extend(trial['intervention_browse']['mesh_term'])
            else:
                tag.append(trial['intervention_browse']['mesh_term'])
            del trial['intervention_browse']
        return tag

    @staticmethod
    def _get_status(trial: dict) -> int:
        """
        Get the status of the clinical trial.

        :param trial: a dictionary contains the clinical trial information
        :return: the status of the trial as a list of strings
        """
        if trial['overall_status'] in {'Not yet recruiting', 'Active, not recruiting'}:
            return 0
        elif trial['overall_status'] in {'Enrolling by invitation', 'Recruiting', 'Available'}:
            return 1
        elif trial['overall_status'] in {'Approved for marketing'}:
            return 2
        else:
            return 3

    def process_file(self, file: str) -> dict:
        trial = xmltodict.parse(open(file, "rb"))['clinical_study']
        # for principal investigator
        sponsors = self._add_sponsors(trial)
        # for user
        users = self._add_users(trial)
        # for clinical trial itself
        product = create_product()
        product['ref'] = trial['id_info']['nct_id']
        product['name'] = trial['brief_title']
        product['asset']['type'] = 2
        del trial['brief_title']
        if 'brief_summary' in trial:
            product['abs'] = trial['brief_summary']['textblock']
            del trial['brief_summary']
        else:
            product['abs'] = product['name']
        if 'overall_contact' in trial:
            if 'phone' in trial['overall_contact']:
                product['contact']['phone'] = trial['overall_contact']['phone']
            if 'phone_ext' in trial['overall_contact'] and len(trial['overall_contact']['phone_ext']) > 0:
                product['contact']['phone'] += '-' + trial['overall_contact']['phone_ext']
            if 'email' in trial['overall_contact']:
                product['contact']['email'] = trial['overall_contact']['email']
            del trial['overall_contact']
        # type
        product['tag'] = self._find_type(trial)
        try:
            product['created'] = parser.parse(trial['study_first_submitted']).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        try:
            product['updated'] = parser.parse(trial['last_update_submitted']).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        # stage
        product['asset']['stat'] = self._get_status(trial)
        # for other details
        del trial['overall_status']
        product['asset']['tech'] = "\n\n".join(self.to_markdown(trial))
        for s in sponsors:
            s['ref'] = product['ref']
        for u in users:
            u['ref'] = product['ref']
        return {'product': product, 'sponsors': sponsors, 'users': users}

    @staticmethod
    def to_markdown(data: dict, level: int = 1) -> list:
        output = []
        if isinstance(data, dict):
            if len(data.keys()) == 1 and 'textblock' in data:
                output.append(str(data['textblock']))
            else:
                for key in data:
                    output.append("#"*level)
                    output.extend(ClinicalTrial.to_markdown(data[key], level + 1))
        elif isinstance(data, list) or isinstance(data, tuple):
            for value in data:
                output.extend(ClinicalTrial.to_markdown(value, level))
        else:
            output.append(str(data))
        return output


def task(directory):
    log.critical('process ' + directory)
    with ClinicalTrial(directory) as t:
        t.run()
    # os.rmdir(directory)
    log.critical('job completed' + directory)


def histogram_task(directory):
    log.critical('process ' + directory)
    with ClinicalTrial(directory) as t:
        return t.histogram_indication()
    # os.rmdir(directory)
    log.critical('job completed' + directory)


if __name__ == '__main__':
    # list the category.
    sourceDirectory = "/Users/zhangtemplar/Downloads/clinictrial"
    dir_list = [os.path.join(sourceDirectory, folder) for folder in os.listdir(sourceDirectory) if
                folder.startswith("NCT")]
    pool = Pool(8)
    # for index in dir_list:
    #     pool.apply_async(task, args=(index,))
    histogram = {}
    for index in dir_list:
        pool.apply_async(histogram_task, args=(index,), callback=lambda h: histogram.update(h))
    pool.close()
    pool.join()
    json.dump(histogram, open(os.path.join(sourceDirectory, 'histogram.json'), 'w'), indent=2)
    result = OrderedDict(sorted(histogram.items(), key=lambda i: -(i[1])))
    json.dump(result, open(os.path.join(sourceDirectory, 'histogram_sorted.json'), 'w'), indent=2)
