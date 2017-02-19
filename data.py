#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle data
"""
import json
import os
import urllib.request
from collections import Counter
from datetime import timedelta, date, datetime

# TODO: Add logging


def _daterange(start_date, end_date):
    '''
    Taken from http://stackoverflow.com/a/1060330/1816143
    '''
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class PinnakisaData:
    """
    Map tabular data (currently pandas DataFrame) to RDF. Create a class instance of each row.
    """

    def __init__(self, api_url='http://www.tringa.fi/kisa/index.php/api/'):
        self.PERSIST_FILE = 'pinnakisa.json'
        self.api_url = api_url
        self.contest_data_url = api_url + 'contest_participations/{id}'
        self.data = []
        self.tick_lists = {}

    def read_contest_data(self, id, cached='auto'):
        result = []
        reload = False

        if cached == 'auto':
            if datetime.timestamp(datetime.now()) - os.path.getmtime(self.PERSIST_FILE) > 60*60:
                reload = True

        if not reload:
            print('Reading data from local file')
            try:
                with open(self.PERSIST_FILE, 'r') as fp:
                    result = json.load(fp)
            except Exception as e:
                print(e)
            if not len(result):
                reload = True

        if reload:
            print('Reading data from API')
            req = urllib.request.Request(self.contest_data_url.format(id=id))
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                with open(self.PERSIST_FILE, 'w') as fp:
                    json.dump(result, fp)
                    print('Data saved to local file')

        for person in result:
            species = person.pop('species_json')
            person['tick_list'] = json.loads(species)

        self.data = result
        self.tick_lists = [person['tick_list'] for person in self.data if len(person['tick_list'])]

    def get_by_species(self, species):
        """
        Get the amount of dates when a species has been ticked
        """
        return Counter([ticks.get(species) for ticks in self.tick_lists if ticks.get(species)])

    def get_by_date(self, date_instance):
        """
        Count ticked species for a given date

        :param date_instance: instance of datetime.date
        """
        return Counter([sp for ticks in self.tick_lists for (sp, sp_date) in ticks.items() if sp_date == date_instance.isoformat()])

    def get_species_cumulation(self, species, start_date, end_date):
        """
        Get the amount of species ticked for each date with zeros.
        """
        values = {}
        ticks = Counter(self.get_by_species(species))

        for single_date in _daterange(start_date, end_date):
            values.update({single_date.isoformat(): ticks.get(single_date.isoformat(), 0)})

        return sorted(values.items())

    def get_daily_popular_ticks(self, start_date, end_date):
        """
        Get most popular tick for each date
        """
        ticks = {}
        for single_date in _daterange(start_date, end_date):
            ticks.update({single_date.isoformat(): (self.get_by_date(single_date).most_common(1) or [''])[0]})

        return sorted(ticks.items())

if __name__ == 'main':
    kisa = PinnakisaData()
    kisa.read_contest_data('3778f94604f8dd433ed80bbf63042198abd0cbea')

    print(kisa.get_by_species('FRICOE'))
    print()
    print(kisa.get_by_date(date(2017, 2, 18)))
    print()

    print(kisa.get_species_cumulation('CORRAX', date(2017, 1, 1), date(2017, 2, 28)))
    print()
    print(kisa.get_daily_popular_ticks(date(2017, 1, 1), date(2017, 2, 28)))

