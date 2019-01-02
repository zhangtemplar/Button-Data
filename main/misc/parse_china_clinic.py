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
import re

from dateutil import parser
from lxml import etree


def create_user():
    return {
        "id": "",
        "password": "",
        "name": "",
        "abstract": "",
        "keyword": [],
        "detail": "",
        "title": "",
        "company": "",
        "education": "",
        "website": "",
        "email": "",
        "phone": "",
        "address": {
            "address1": "",
            "address2": "",
            "city": "",
            "state": "",
            "country": "",
            "zip": ""
        },
        "type": 0,
        "capital": {
            "amount": 0,
            "unit": ""
        },
        "netCapital": {
            "amount": 0,
            "unit": ""
        },
        "credit": 0,
        "refer": "00000000000000000000000000000000",
        "legal": "",
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/user.png",
        "authority": {
            "mac": "",
            "wechat": "",
            "linkedin": "",
            "google": "",
            "facebook": ""
        }
    }

def create_product():
    return {
        "id": "",
        "projectId": "",
        "name": "",
        "logo": "https://buttondata.oss-cn-shanghai.aliyuncs.com/product.png",
        "abstract": "",
        "detail": {
            "market": "",
            "introduction": "",
            "technique": ""
        },
        "time": 0,
        "price": {
            "cost": 0.0,
            "exw": 0.0,
            "market": 0.0
        },
        "type": [],
        "status": "",
        "license": [],
        "credit": 0
    }


def parse_html(file):
    document = etree.parse(file, etree.HTMLParser())
    product = create_product()
    data_english = parse(document, 'cn')
    data_chinese = parse(document, 'en')
    product['name'] = data_chinese[u'注册题目']
    product['time'] = parser.parse(data_chinese[u'注册时间']).timestamp()
    product['abstract'] = data_chinese[u'研究目的']
    product['status'] = data_english['Recruiting status']

    product['type'].append('Clinic Trial')
    product['type'].append(u'临床测试')
    product['type'].append(data_chinese[u'研究疾病'])
    product['type'].append(data_english[u'Target disease'])
    product['type'].append(data_chinese[u'研究疾病代码'])
    product['type'].append(data_english[u'Target disease code'])
    product['type'].append(data_chinese[u'研究类型'])
    product['type'].append(data_english[u'Study type'])
    product['type'].append(data_chinese[u'研究所处阶段'])
    product['type'].append(data_english[u'Study phase'])
    product['type'].append(data_chinese[u'研究类型'])
    product['type'].append(data_english[u'Study type'])

    product['license'].append('Clinic Trial')
    product['license'].append(u'临床测试')
    product['license'].append(data_chinese['研究课题代号(代码)'])
    product['license'].append(data_chinese['注册号'])
    product['license'].append(data_chinese['伦理委员会批件文号'])

    applicant = create_user()
    applicant['name'] = data_chinese[u'申请注册联系人']
    applicant['phone'] = data_chinese[u'申请注册联系人电话']
    applicant['email'] = data_chinese[u'申请注册联系人电子邮件']
    applicant['website'] = data_chinese[u'申请单位网址(自愿提供)']
    applicant['address']['address1'] = data_chinese[u'申请注册联系人通讯地址']
    applicant['address']['address2'] = data_english[u'Applicant address']
    applicant['address']['zip'] = data_chinese[u'申请注册联系人邮政编码']
    applicant['company'] = data_chinese[u'申请人所在单位']
    principal_investigator = create_user()
    principal_investigator['name'] = data_chinese[u'研究负责人']
    principal_investigator['phone'] = data_chinese[u'研究负责人电话']
    principal_investigator['email'] = data_chinese[u'研究负责人电子邮件']
    principal_investigator['website'] = data_chinese[u'研究负责人网址(自愿提供)']
    principal_investigator['address']['address1'] = data_chinese[u'研究负责人通讯地址']
    principal_investigator['address']['address2'] = data_english[u"Study leader's address"]
    principal_investigator['address']['zip'] = data_chinese[u'研究负责人邮政编码']

    product['detail']['introduction'] = dictionary_to_markdown(
        data_english, ['Objectives of Study', 'Description for medicine or protocol of treatment in detail'])
    product['detail']['introduction'] += dictionary_to_markdown(data_chinese, ['药物成份或治疗方案详述'])

    product['detail']['technique'] = dictionary_to_markdown(
        data_english,
        ['Study design', 'Inclusion criteria', 'Exclusion criteria', 'Study execute time', 'Interventions',
         'Countries of recruitment and research settings', 'Outcomes', 'Collecting sample(s) from participants',
         'Participant age', 'Gender',
         'Randomization Procedure (please state who generates the random number sequence and by what method)',
         'Blinding', 'The time of sharing IPD',
         'The way of sharing IPD”(include metadata and protocol, If use web-based public database, please provide the url)',
         'Data collection and Management (A standard data collection and management system include a CRF and an electronic data capture',
         'Data Managemen Committee'])
    product['detail']['technique'] += dictionary_to_markdown(
        data_chinese,
        ['研究设计', '纳入标准', '排除标准', '研究实施时间', '干预措施', '研究实施地点', '测量指标', '采集人体标本', '年龄范围',
         '性别', '随机方法（请说明由何人用什么方法产生随机序列）', '盲法', '原始数据公开时间',
         '共享原始数据的方式（说明：请填入公开原始数据日期和方式，如采用网络平台，需填该网络平台名称和网址）',
         '数据采集和管理（说明：数据采集和管理由两部分组成，一为病例记录表(Case Record Form, CRF)，二为电子采集和管理系统(Electronic Data Capture, EDC)，如ResMan即为一种基于互联网的EDC',
         '数据管理委员会'])
    return {'product': product, 'applicant': applicant, 'principal_investigator': principal_investigator}


def list_to_table(data):
    if len(data) < 1:
        return ''
    keys = sorted(data[0].keys())
    result = ' | '.join(keys)
    result += '\n'
    result += ' | '.join(['---' for _ in keys])
    for d in data:
        result += '\n'
        result += ' | '.join([d[k] for k in keys])
    return result


def dictionary_to_markdown(data: dict, keys=None):
    if keys is None:
        keys = data.keys()
    result = ''
    for k in keys:
        if k not in data:
            continue
        if isinstance(data[k], list):
            result += '# {}\n\n{}\n\n'.format(k, list_to_table(data[k]))
        else:
            result += '# {}\n\n{}\n\n'.format(k, data[k])
    return result


def remove_blank(text):
    match = re.findall(r'\S[\s\S]*\S', text, re.UNICODE)
    return match[0] if len(match) > 0 else ''


def remove_tail_colon(text):
    if text is not None and len(text) > 0:
        return text[:-1]
    else:
        return ''


def select_language(language):
    return "[not(contains(@class,'{}'))]".format(language)


def parse_table(table, language):
    data = {}
    for row in table.xpath("tr{}".format(select_language(language))):
        columns = row.xpath("td{}".format(select_language(language)))
        if len(columns) < 2:
            logging.warning("some is wrong with the table")
            continue
        # for row with embedded table
        if len(columns[1].xpath("table/tbody")) > 0:
            key = remove_tail_colon(remove_blank(columns[0].xpath("p{}".format(select_language(language)))[0].text))
            data[key] = []
            for sub_table in columns[1].xpath("table/tbody"):
                data[key].append(parse_table(sub_table, language))
        else:
            for i in range(0, len(columns) - 1, 2):
                if len(columns[i].xpath("p{}".format(select_language(language)))) < 1:
                    continue
                key = remove_tail_colon(remove_blank(columns[i].xpath("p{}".format(select_language(language)))[0].text))
                value = columns[i + 1].xpath("p{}".format(select_language(language)))
                if len(value) < 1:
                    data[key] = remove_blank(columns[i + 1].text)
                else:
                    data[key] = remove_blank(value[0].text)
    logging.debug(data)
    return data


def parse(document, language):
    data = {}
    for table in document.xpath("//div[@class='ProjetInfo_ms']/table/tbody"):
        data.update(parse_table(table, language))
    logging.debug(data)
    return data


def download_china_clinic():
    logging.basicConfig(level=logging.INFO)
    work_directory = os.path.expanduser('~/Downloads/clinic')
    for file in os.listdir(work_directory):
        if not file.endswith('html'):
            continue
        logging.info('process {}'.format(file))
        try:
            data = parse_html(os.path.join(work_directory, file))
            with open(os.path.join(work_directory, file[:-len('html')] + 'json'), 'w') as fo:
                json.dump(data, fo, ensure_ascii=False)
        except Exception as e:
            logging.error('failed to process {}'.format(file))
            logging.error(e)


if __name__ == '__main__':
    download_china_clinic()
