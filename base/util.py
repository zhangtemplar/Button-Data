import re
import logging
import requests
import traceback

from base.credential import AMAP_KEY


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


def normalize_email(input):
    for m in re.finditer(
            r'(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})',
            input):
        return m.group()
    return ''


def normalize_phone(input):
    for m in re.finditer(r'^[0-9+\-\ \.]{10,}', input):
        return m.group()
    return ''


def create_logger(name):
    log = logging.getLogger(name)
    log.handlers = []
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.FileHandler(name))
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    log.addHandler(stream_handler)
    return log


def remove_empty_string_from_array(array):
    return list(set([a for a in array if len(a) > 0]))


def parse_chinese_address(text: str) -> dict or None:
    """
    Use 高德地图地理/逆地理编码 to parse chinese address
    :param text: a free form chinese address
    :return: the parsed address as an object if possible, otherwise null
    """
    try:
        response = requests.get('https://restapi.amap.com/v3/geocode/geo?address={}&output=JSON&key={}'.format(
            text, AMAP_KEY)).json()
        if 'geocodes' in response and len(response['geocodes']) > 0:
            return {
                'city': response['geocodes'][0]['city'],
                'country': 'China',
                'state': response['geocodes'][0]['province'],
                'zip': response['geocodes'][0]['adcode'],
                'line1': ''.join(response['geocodes'][0]['street']) + ' ' + ''.join(response['geocodes'][0]['number']),
                'line2': response['geocodes'][0]['district'] + ' ' + ''.join(response['geocodes'][0]['township']),
            }
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return None


def extract_phone(text):
    if not isinstance(text, str):
        return []
    result = []
    for m in re.finditer('\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text):
        result.append(m.group())
    return result
