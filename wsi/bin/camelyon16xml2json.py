import sys
import os
import argparse
import logging
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

from wsi.data.annotation import Formatter  # noqa

parser = argparse.ArgumentParser(description='Convert Camelyon16 xml format to'
                                 'internal json format')
parser.add_argument('xml_path', default=None, metavar='XML_PATH', type=str,
                    help='Path to the input Camelyon16 xml annotation')
parser.add_argument('json_path', default=None, metavar='JSON_PATH', type=str,
                    help='Path to the output annotation in json format')


def run(args):
    for xml_file in tqdm(os.listdir(args.xml_path)):
        xml_file_full = os.path.join(args.xml_path, xml_file)
        out_json = xml_file[:-4] + '.json'
        out_json_full  = os.path.join(args.json_path, out_json)

        Formatter.camelyon16xml2json(xml_file_full, out_json_full)


def main():
    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
