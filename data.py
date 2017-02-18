#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle data
"""
import json
import urllib.request


class PinnakisaData:
    """
    Map tabular data (currently pandas DataFrame) to RDF. Create a class instance of each row.
    """

    def __init__(self, api_url='http://www.tringa.fi/kisa/index.php/api/'):
        self.api_url = api_url
        self.contest_data_url = api_url + 'contest_participations/{id}'
        self.data = None

    def read_contest_data(self, id):
        req = urllib.request.Request(self.contest_data_url.format(id=id))
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

        for person in result:
            species = person.pop('species_json')
            person['species'] = json.loads(species)

        self.data = result

kisa = PinnakisaData()
kisa.read_contest_data('3778f94604f8dd433ed80bbf63042198abd0cbea')
print(len(kisa.data))

