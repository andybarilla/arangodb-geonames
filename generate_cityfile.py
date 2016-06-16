#!/usr/bin/env python3
import argparse
from collections import namedtuple
import csv
import io
import json
import zipfile

import requests

GEONAMES_SOURCE = "http://download.geonames.org/export/zip/{}.zip"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--country_code',
                        default='US',
                        dest='country_code',
                        help="2 letter country code to download from geonames")
    parser.add_argument('--local_file',
                        default=None,
                        dest='local_file',
                        help='path to local file to import')
    parser.add_argument('--output_file',
                        default='cities.json',
                        dest='output_file',
                        help="output file name")
    args = parser.parse_args()

    of = open(args.output_file, 'w')

    if args.local_file is None:
        country_codes = args.country_code.split(',')
        for country_code in country_codes:
            try:
                r = requests.get(GEONAMES_SOURCE.format(country_code))
            except ConnectionError as e:
                raise Exception('Error downloading source: {}'.format(e))
            zf = zipfile.ZipFile(io.BytesIO(r.content))

            for info in zf.infolist():
                if info.filename == 'readme.txt':
                    continue

                import_file(io.TextIOWrapper(zf.open(info.filename)), of)
    else:
        import_file(open(args.local_file), of)

    of.close()


def import_file(f, of):

    Record = namedtuple('Record', (
        'country_code',
        'postal_code',
        'city_name',
        'admin_name1',
        'admin_code1',
        'admin_name2',
        'admin_code2',
        'admin_name3',
        'admin_code3',
        'latitude',
        'longitude',
        'accuracy',
    ))

    reader = csv.reader(f, delimiter='\t')
    cnt = 0
    cities = {}
    last_country_code = None

    for row in map(Record._make, reader):
        if last_country_code != row.country_code:
            dump_cities(cities, of)
            cities = {}
            last_country_code = row.country_code

        try:
            name = row.city_name
            state = get_state_abbr(row.country_code, row.admin_name1)
            country_code = row.country_code
            city_key = '{}.{}.{}'.format(name,
                                         state,
                                         country_code).replace(' ', '_')
            if state == '' and country_code == 'US':
                continue

            if state == '':
                label = '{}, {}'.format(name, country_code)
                state = None
            else:
                label = '{}, {}'.format(name, state)

            if city_key not in cities.keys():
                cnt += 1
                cities[city_key] = {'_key': '{}{}'.format(country_code, cnt),
                                    'name': row.city_name,
                                    'state': row.admin_name1,
                                    'country_code': row.country_code,
                                    'label': label,
                                    'postal_codes': []}

            try:
                if row.latitude:
                    location = [float(row.latitude), float(row.longitude)]
            except:
                location = None
                print(row)

            cities[city_key]['postal_codes'].append(
                {
                    'postal_code': row.postal_code,
                    'location': location,
                })

        except Exception as e:
            print(row)

    dump_cities(cities, of)


def get_state_abbr(country_code, state_name):
    # You might want to write a function to convert
    # state names to abbreviations
    return state_name


def dump_cities(cities, of):
    for city in cities.values():
        json.dump(city, of)
        of.write('\n')


if __name__ == '__main__':
    main()
