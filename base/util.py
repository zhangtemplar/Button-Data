import re


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
    for m in re.finditer(r'(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})', input):
        return m.group()
    return ''

def normalize_phone(input):
    for m in re.finditer(r'^[0-9+\-\ \.]{10,}', input):
        return m.group()
    return ''
