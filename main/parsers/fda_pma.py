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
from base.util import create_logger, remove_empty_string_from_array, dictionary_to_markdown
from base.template import create_product, create_relationship, add_record, create_company
from main.parsers.fda_510k import submission_type, third_party, get_product_code


def decision_code(code):
    """
    A four digit code reflecting the final decision for a PMA submission.

Value is one of the following
APPR = Approval: PMA has been approved.
WTDR = Withdrawal: PMA has been withdrawn.
DENY = Denial: PMA has been denied.
LE30 = 30 day notice acceptance (decision made in ≤30 days).
APRL = Reclassification after approval.
APWD = Withdrawal after approval.
GT30 = No decision made in 30 days.
APCV = Conversion after approval.
"""
    if code in {'APRL', 'LE30', 'APPR', 'APCV'}:
        return 2
    elif code in {'WTDR', 'DENY', 'APWD', 'GT30'}:
        return 3
    else:
        return 3


def main():
    product_code = get_product_code()
    log = create_logger('PMA')
    result = json.load(open('/home/jovyan/work/fda/device-pma-0001-of-0001.json', 'r'))
    log.critical(datetime.datetime.now())
    for r in result['results']:
        #     if client.data.entity.find_one({'ref': r.get('pma_number', r['openfda'].get('pma_number', ''))}) is not None:
        #         log.info('{} already exists'.format(r.get('pma_number', r['openfda'].get('pma_number', ''))))
        #         continue
        p = create_product()
        p['ref'] = r.get('pma_number', r['openfda'].get('pma_number', ''))
        p['name'] = r.get('trade_name', r['openfda'].get('trade_name', ''))
        p['abs'] = r.get('generic_name', r['openfda'].get('generic_name', p['name']))
        if len(p['abs']) < 1:
            p['abs'] = p['name']
        p['addr']['line1'] = r.get('address_1', r['openfda'].get('address_1', ''))
        p['addr']['line2'] = r.get('address_2', r['openfda'].get('address_2', ''))
        p['addr']['city'] = r.get('city', r['openfda'].get('city', ''))
        p['addr']['state'] = r.get('state', r['openfda'].get('state', ''))
        p['addr']['zip'] = r.get('zip_code', r['openfda'].get('zip_code', ''))
        p['addr']['country'] = r.get('country_code', r['openfda'].get('country_code', ''))
        p['asset']['type'] = 0
        p['tag'] = [
            r.get('advisory_committee_description', r['openfda'].get('advisory_committee_description', '')),
            r.get('medical_specialty_description', r['openfda'].get('medical_specialty_description', '')),
            'FDA',
            'Medical Device',
            'PMA']
        # p['tag'] is used for tags readable to common users, p['lic'] is used for tags specified for product.
        p['asset']['lic'] = [
            'FDA',
            'PMA',
            r.get('advisory_committee_description', r['openfda'].get('advisory_committee_description', '')),
            r['openfda'].get('medical_specialty_description', ''),
            r.get('product_code', r['openfda'].get('product_code', '')),
            r.get('regulation_number', r['openfda'].get('regulation_number', ''))]
        p['asset']['lic'].extend(third_party(r.get('third_party_flag', r['openfda'].get('third_party_flag', ''))))
        if len(r.get('expedited_review_flag', r['openfda'].get('expedited_review_flag', ''))) > 0:
            p['asset']['lic'].append('Expedited Review')
        if r.get('submission_type_id', r['openfda'].get('submission_type_id', '')) not in {'1', '2'} and \
                submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))) is not None:
            p['asset']['lic'].append(submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))))
            p['tag'].append(submission_type(r.get('submission_type_id', r['openfda'].get('submission_type_id', ''))))
        code = product_code.get(r.get('product_code', r['openfda'].get('product_code', '')), None)
        if code is not None:
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
        p['asset']['stat'] = decision_code(r.get('decision_code', r['openfda'].get('decision_code', '')))
        try:
            p['created'] = parser.parse(r.get('date_received', r['openfda'].get('date_received', None))).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        try:
            p['updated'] = parser.parse(r.get('decision_date', r['openfda'].get('decision_date', None))).strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pass
        p['intro'] = r.get('statement_or_summary', r['openfda'].get('statement_or_summary', ''))
        p['intro'] = dictionary_to_markdown({
            'Summary': r.get('supplement_number', r['openfda'].get('statement_or_summary', '')),
            'Supplement Reason': r.get('supplement_reason', r['openfda'].get('supplement_reason', '')),
            'Statement': r.get('ao_statement', r['openfda'].get('ao_statement', ''))})
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
