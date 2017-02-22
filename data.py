#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle data
"""
# TODO: Switch to use pandas
# TODO: Add logging

import json
import os
import urllib.request
from collections import Counter
from datetime import timedelta, date, datetime

import dateutil.parser


def _daterange(start_date, end_date):  # TODO: use pandas.date_range
    '''
    Taken from http://stackoverflow.com/a/1060330/1816143
    '''
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class PinnakisaData:
    """
    Handle data from Pinnakisa-API.
    """

    def __init__(self, api_url='http://www.tringa.fi/kisa/index.php/api/'):
        self.PERSIST_FILE = '{id}.json'
        self.api_url = api_url
        self.contest_data_url = api_url + 'contest_participations/{id}'
        self.data = []
        self.tick_lists = {}

    def read_contest_data(self, id, cached='auto'):
        result = []
        reload = False

        if cached == 'auto':
            try:
                if datetime.timestamp(datetime.now()) - os.path.getmtime(self.PERSIST_FILE.format(id=id)) > 15 * 60:
                    reload = True
            except FileNotFoundError:
                reload = True

        if not reload:
            print('Reading data from local file')
            try:
                with open(self.PERSIST_FILE.format(id=id), 'r') as fp:
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
                with open(self.PERSIST_FILE.format(id=id), 'w') as fp:
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

    def get_species_cumulation(self, species, start_date=None, end_date=None):
        """
        Get the amount of species ticked for each date with zeros.
        """
        values = {}
        ticks = self.get_by_species(species)

        d2 = None
        if not start_date:
            d1, d2 = self.get_date_limits()
            start_date = d1
        if not end_date:
            end_date = d2 or self.get_date_limits()[1]

        for single_date in list(_daterange(start_date, end_date)) + [end_date]:
            values.update({single_date: ticks.get(single_date.isoformat(), 0)})

        return sorted(values.items())

    def get_daily_popular_ticks(self, start_date, end_date):
        """
        Get most popular tick for each date
        """

        def get_all_commonest(counter):
            common = counter.most_common() or [('', 0)]
            max_ticks = common[0][1]
            names = ", ".join(sorted(name for name, count in common if count == max_ticks))
            return names, max_ticks

        ticks = {}
        for single_date in list(_daterange(start_date, end_date)) + [end_date]:
            ticks.update({single_date.isoformat(): get_all_commonest(self.get_by_date(single_date))})

        return sorted(ticks.items())

    def get_all_species(self):
        """
        Get all species from data
        """
        return sorted(set([sp for ticks in self.tick_lists for sp in ticks.keys()]))

    def get_date_limits(self):

        minimum = '9999-99-99'
        maximum = '1111-11-11'

        for ticks in self.tick_lists:
            mini = min(ticks.values())
            maxi = max(ticks.values())
            if mini < minimum:
                minimum = mini
            if maxi > maximum:
                maximum = maxi

        minimum = dateutil.parser.parse(minimum).date()
        maximum = dateutil.parser.parse(maximum).date()

        return (minimum, maximum)

if __name__ == '__main__':
    kisa = PinnakisaData()
    # kisa.read_contest_data('3778f94604f8dd433ed80bbf63042198abd0cbea')
    kisa.read_contest_data('0ef446b826a8764703a63ca1fb17a3c924d82dcf')
    # kisa.read_contest_data('b315cf20217b2bb3c1331445b4cb6ab39db9e348')

    print(kisa.get_all_species())
    print(kisa.get_daily_popular_ticks(*kisa.get_date_limits()))
