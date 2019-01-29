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
import copy
from lxml import etree
from base.template import create_product, create_user


def remove_empty_string(tags):
    return [i for i in tags if len(i) > 0]


def parse_html(file):
    document = etree.parse(file, etree.HTMLParser())
    product = create_product()
    data_english = parse(document, 'cn')
    data_chinese = parse(document, 'en')
    product['name'] = data_chinese[u'注册题目']
    product['abs'] = data_chinese[u'研究目的']
    product['asset']['stat'] = data_english['Recruiting status']
    product['intro'] = data_chinese['药物成份或治疗方案详述']
    href = document.xpath("//body/div[4]/div[2]/a")
    product['ref'] = 'http://www.chictr.org.cn/' + (href[0].attrib['href'] if len(href) > 0 else '')

    product['tag'].append(data_chinese[u'研究疾病'])
    product['tag'].append(data_english[u'Target disease'])
    product['tag'].append(data_chinese[u'研究疾病代码'])
    product['tag'].append(data_english[u'Target disease code'])
    product['tag'].append(data_chinese[u'研究类型'])
    product['tag'].append(data_english[u'Study type'])
    product['tag'].append(data_chinese[u'研究所处阶段'])
    product['tag'].append(data_english[u'Study phase'])
    product['tag'].append(data_chinese[u'研究类型'])
    product['tag'].append(data_english[u'Study type'])
    product['tag'] = remove_empty_string(product['tag'])

    product['asset']['lic'].append(data_chinese['研究课题代号(代码)'])
    product['asset']['lic'].append(data_chinese['注册号'])
    product['asset']['lic'].append(data_chinese['伦理委员会批件文号'])
    product['asset']['lic'] = remove_empty_string(product['asset']['lic'])

    product['asset']['type'] = 2
    product['asset']['tech'] = dictionary_to_markdown(
        data_english,
        ['Study design', 'Inclusion criteria', 'Exclusion criteria', 'Study execute time', 'Interventions',
         'Countries of recruitment and research settings', 'Outcomes', 'Collecting sample(s) from participants',
         'Participant age', 'Gender',
         'Randomization Procedure (please state who generates the random number sequence and by what method)',
         'Blinding', 'The time of sharing IPD',
         'The way of sharing IPD”(include metadata and protocol, If use web-based public database, please provide the url)',
         'Data collection and Management (A standard data collection and management system include a CRF and an electronic data capture',
         'Data Managemen Committee'])
    product['asset']['tech'] += dictionary_to_markdown(
        data_chinese,
        ['研究设计', '纳入标准', '排除标准', '研究实施时间', '干预措施', '研究实施地点', '测量指标', '采集人体标本', '年龄范围',
         '性别', '随机方法（请说明由何人用什么方法产生随机序列）', '盲法', '原始数据公开时间',
         '共享原始数据的方式（说明：请填入公开原始数据日期和方式，如采用网络平台，需填该网络平台名称和网址）',
         '数据采集和管理（说明：数据采集和管理由两部分组成，一为病例记录表(Case Record Form, CRF)，二为电子采集和管理系统(Electronic Data Capture, EDC)，如ResMan即为一种基于互联网的EDC',
         '数据管理委员会'])

    applicant = create_user()
    applicant['name'] = data_chinese[u'申请注册联系人']
    applicant['contact']['phone'] = data_chinese[u'申请注册联系人电话']
    applicant['contact']['email'] = data_chinese[u'申请注册联系人电子邮件']
    applicant['contact']['website'] = data_chinese[u'申请单位网址(自愿提供)']
    applicant['addr'] = parse_address(data_english[u'Applicant address'])
    applicant['addr']['zip'] = data_chinese[u'申请注册联系人邮政编码']
    applicant['exp']['exp']['company'] = data_chinese[u'申请人所在单位']
    principal_investigator = create_user()
    principal_investigator['name'] = data_chinese[u'研究负责人']
    principal_investigator['contact']['phone'] = data_chinese[u'研究负责人电话']
    principal_investigator['contact']['email'] = data_chinese[u'研究负责人电子邮件']
    principal_investigator['contact']['website'] = data_chinese[u'研究负责人网址(自愿提供)']
    principal_investigator['addr'] = parse_address(data_english[u"Study leader's address"])
    principal_investigator['addr']['zip'] = data_chinese[u'研究负责人邮政编码']

    product['addr'] = copy.deepcopy(applicant['addr'])
    return {'product': product, 'applicant': applicant, 'principal_investigator': principal_investigator}


def parse_address(text):
    segments = text.split(", ")
    address = {"country": "", "line2": "", "city": "", "zip": "", "state": "", "line1": ""}
    if len(segments) == 1:
        address['line1'] = text
        address['city'] = 'Unknown'
        address['country'] = 'China'
    else:
        address['country'] = segments[-1]
        if len(segments) > 4:
            address['city'] = segments[-3]
            address['state'] = segments[-2]
        else:
            address['city'] = segments[-2]
        address['line1'] = segments[0]
        address['line2'] = segments[1]
    return address


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
        if os.path.exists(os.path.join(work_directory, file[:-len('html')] + 'json')):
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
