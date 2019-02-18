# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Add documentation of this module here.
"""
import json
import os
import datetime
from dateutil import parser
from base.util import create_logger, remove_empty_string_from_array
from base.template import create_product, create_relationship, add_record, create_company


def get_product_code():
    product_code = json.load(open(os.path.expanduser('~/work/fda/device-classification-0001-of-0001.json'), 'r'))
    print(product_code.keys())
    print(len(product_code['results']))
    print(product_code['results'][0])
    product_code = {p['product_code']: p for p in product_code['results']}
    return product_code


def submission_type(input):
    # based on https://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/Overview/ClassifyYourDevice/ucm051668.htm#sti
    if input == '1':
        return '510K'
    elif input == '2':
        return 'PMA'
    elif input == '3':
        return 'Contact ODE'
    elif input == '4':
        return '510K Exempt'
    elif input == '6':
        return 'Humanitarian Device Exemption'
    elif input == '7':
        return 'Enforcement Discretion'
    elif input == '8':
        return 'Emergency Use Authorization'
    else:
        return None


def third_party(code):
    # https://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/GuidanceDocuments/ucm094450.htm
    if code == 'A':
        return ['Accredited Persons Program']
    elif code == 'M':
        return ['Mutual Recognition Agreement']
    elif code == 'B':
        return ['Accredited Persons Program', 'Mutual Recognition Agreement']
    elif code == 'P':
        return ['Accredited Persons Expansion Pilot Program']
    else:
        return []


def map_status(status):
    if status in {'WD', 'DD', 'DE', 'NE', 'SC', 'SL', 'RE', 'UD', 'UO', 'UR', 'OD', 'CR', 'ND', 'NF', 'NR'}:
        return 3
    else:
        return 2


def main():
    product_code = get_product_code()
    log = create_logger('510K')
    result = json.load(open(os.path.expanduser('~/work/fda/device-classification-0001-of-0001.json'), 'r'))
    log.critical(datetime.datetime.now())
    for r in result['results']:
        p = create_product()
        p['name'] = r.get('device_name', r['openfda'].get('device_name', ''))
        p['ref'] = r.get('k_number', r['openfda'].get('k_number', ''))
        p['addr']['line1'] = r.get('address_1', r['openfda'].get('address_1', ''))
        p['addr']['line2'] = r.get('address_2', r['openfda'].get('address_2', ''))
        p['addr']['city'] = r.get('city', r['openfda'].get('city', ''))
        p['addr']['state'] = r.get('state', r['openfda'].get('state', ''))
        p['addr']['zip'] = r.get('zip_code', r['openfda'].get('zip_code', ''))
        p['addr']['country'] = r.get('country_code', r['openfda'].get('country_code', ''))
        p['intro'] = r.get('statement_or_summary', r['openfda'].get('statement_or_summary', ''))
        p['asset']['type'] = 0
        p['tag'] = [
            r.get('advisory_committee_description', r['openfda'].get('advisory_committee_description', '')),
            r.get('medical_specialty_description', r['openfda'].get('medical_specialty_description', '')),
            'FDA',
            'Medical Device',
            '510K']
        # p['tag'] is used for tags readable to common users, p['lic'] is used for tags specified for product.
        p['asset']['lic'] = [
            'FDA',
            '510K',
            r.get('clearance_type', r['openfda'].get('clearance_type', '')),
            r.get('advisory_committee_description', r['openfda'].get('advisory_committee_description', '')),
            r['openfda'].get('medical_specialty_description', ''),
            r.get('product_code', r['openfda'].get('product_code', '')),
            r.get('regulation_number', r['openfda'].get('regulation_number', '')),
            r.get('decision_description', r['openfda'].get('decision_description', '')), ]
        p['asset']['lic'].extend(third_party(r.get('third_party_flag', r['openfda'].get('third_party_flag', ''))))
        if len(r.get('expedited_review_flag', r['openfda'].get('expedited_review_flag', ''))) > 0:
            p['asset']['lic'].append('Expedited Review')
        if r.get('submission_type_id', r['openfda'].get('submission_type_id', '')) not in {'1', '2'} and \
                submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))) is not None:
            p['asset']['lic'].append(
                submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))))
            p['tag'].append(submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))))
        code = product_code.get(r.get('product_code', r['openfda'].get('product_code', '')), None)
        if code is not None:
            p['abs'] = code['device_name']
            p['asset']['lic'].extend([
                'Class ' + code['device_class'],
                'GMP Exempt' if code['gmp_exempt_flag'] == 'N' else 'GMP Required',
            ])
            p['tag'].append('Class ' + code['device_class'])
            if code['implant_flag'] != 'N':
                p['asset']['lic'].append('Implant')
                p['tag'].append('Implant')
            if code['life_sustain_support_flag'] != 'N':
                p['asset']['lic'].append('Life Sustain Support')
                p['tag'].append('Life Sustain Support')
        else:
            p['abs'] = p['name']
        p['asset']['stat'] = map_status(r.get('decision_code', r['openfda'].get('decision_code', '')))
        try:
            p['created'] = parser.parse(r.get('date_received', r['openfda'].get('date_received', None))).strftime(
                "%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        try:
            p['updated'] = parser.parse(r.get('decision_date', r['openfda'].get('decision_date', None))).strftime(
                "%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        p['asset']['lic'] = remove_empty_string_from_array(p['asset']['lic'])
        p['tag'] = remove_empty_string_from_array(p['tag'])
        a = create_company()
        a['name'] = r.get('applicant', r['openfda'].get('applicant', ''))
        a['abs'] = 'A Medical Device Company'
        a['addr'] = p['addr']
        a['tag'] = p['tag']
        a['group']['parentId'] = '000000000000000000000000'
        # contact is just the name of contact

        response = add_record('entity', [p, a])
        if response['_status'] != 'OK':
            log.error('fail to create record for {}'.format(p['name']))
            continue
        applicant_product = create_relationship(response['_items'][1]['_id'], response['_items'][0]['_id'])
        applicant_product['type'] = 7
        applicant_product['name'] = 'Applicant'
        applicant_product['abs'] = 'Applicant'
        response = add_record('relationship', [applicant_product])
        if response['_status'] != 'OK':
            log.error('fail to create relationship for {}'.format(p['name']))
        else:
            log.debug('added {} to the system'.format(p['name']))
    log.critical(datetime.datetime.now())
