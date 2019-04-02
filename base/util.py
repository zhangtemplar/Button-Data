import re
import logging
import requests
import traceback
import hmac
from hashlib import sha1
from urllib.request import quote
from zhon.hanzi import punctuation
import string
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
    if isinstance(data[0], str):
        return '  - ' + '\n  - '.join(data)
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


def remove_head_tail_white_space(text: str) -> str:
    """
    Remove the heading and tailing white space character
    :param text: input text
    :return: a string
    """
    text = re.sub('^([\s%s]+)' % (punctuation + string.punctuation), '', text)
    return re.sub('([\s%s])$' % (punctuation + string.punctuation), '', text)


def extract_dictionary(data: dict, regex_pattern: str) -> dict:
    """
    Finds the sub dictionary whose keys match regex pattern.

    :param data: the input dict
    :param regex_pattern: regular pattern to match the key
    :return: the sub dictionary whose keys match regex pattern
    """
    pattern = re.compile(regex_pattern)
    result = {}
    for k in data:
        if len(pattern.findall(k)) > 0:
            result[k] = data[k]
    return result


def compute_signature(token: str, url: str, data: str=None) -> str:
    """
    Computes the signature for eve request.

    :param token: the token for the user to fire the request, which is usually obtained from redis
    :param url: the url of the request
    :param data: the request body in json format
    :return: the computed signature
    """
    token = token.encode('utf-8')
    url = quote(url, safe='?/=%:$').encode('utf-8')
    if isinstance(data, str):
        data = data.encode('utf-8')
    middle = hmac.new(token, url, sha1).hexdigest()
    print(middle)
    if isinstance(middle, str):
        middle = middle.encode('utf-8')
    truth = hmac.new(middle, data, sha1).hexdigest()
    return truth
