# coding=utf-8
__author__ = "Qiang Zhang"
__maintainer__ = "Qiang Zhang"
__email__ = "zhangtemplar@gmail.com"
"""
Build the structure for pubmed
"""
import os
import json
import xmltodict

from base.util import create_logger


def parse_mesh(data_file):
    result = {
        'A': {'name': 'Anatomy'},
        'B': {'name': 'Organisms'},
        'C': {'name': 'Diseases'},
        'D': {'name': 'Chemicals and Drugs'},
        'E': {'name': 'Analytical, Diagnostic and Therapeutic Techniques, and Equipment'},
        'F': {'name': 'Psychiatry and Psychology'},
        'G': {'name': 'Phenomena and Processes'},
        'H': {'name': 'Disciplines and Occupations'},
        'I': {'name': 'Anthropology, Education, Sociology, and Social Phenomena'},
        'J': {'name': 'Technology, Industry, and Agriculture'},
        'K': {'name': 'Humanities'},
        'L': {'name': 'Information Science'},
        'M': {'name': 'Named Groups'},
        'N': {'name': 'Health Care'},
        'V': {'name': 'Publication Characteristics'},
        'Z': {'name': 'Geographicals'},
    }
    logger = create_logger('pubmed.log')

    def process_record(_, record):
        name = record['DescriptorName']['String']
        logger.debug(name)
        if 'TreeNumberList' not in record or 'TreeNumber' not in record['TreeNumberList']:
            return True
        tree = record['TreeNumberList']['TreeNumber']
        if not isinstance(tree, list):
            tree = [tree]
        for t in tree:
            # special process the first part of the path
            path2 = t[1:].split('.')
            path = [t[0]]
            path.extend(path2)
            node = result
            for p in path:
                if p not in node:
                    node[p] = {}
                node = node[p]
            node['name'] = name
        return True

    logger.info('process {}'.format(data_file))
    try:
        xmltodict.parse(open(data_file, "rb"), item_depth=2, item_callback=process_record)
    except xmltodict.ParsingInterrupted:
        pass
    except Exception as e:
        raise e
    return dict(result)


def reformat_tree(source: dict) -> dict:
    mesh = {}
    for k in source:
        if not isinstance(source[k], dict) or k == 'name':
            continue
        mesh[source[k]['name']] = reformat_tree(source[k])
    return mesh


if __name__ == '__main__':
    mesh = parse_mesh(os.path.expanduser('~/Downloads/desc2019.xml'))
    json.dump(mesh, open(os.path.expanduser('~/Downloads/mesh.json'), 'w'))
    mesh = json.load(open(os.path.expanduser('~/Downloads/mesh.json'), 'r'))
    result = reformat_tree(mesh)
    json.dump(result, open(os.path.expanduser('~/Downloads/mesh2.json'), 'w'))
