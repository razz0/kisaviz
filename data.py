#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle data
"""
# TODO: Switch to use pandas

import json
import logging
import os
import urllib.request
from collections import Counter
from datetime import timedelta, datetime

import pytz
from pytz import timezone
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

    def __init__(self, api_url='http://www.tringa.fi/kisa/index.php/api/', loglevel='INFO'):
        self.CONTEST_PERSIST_FILE = 'contest_{id}.json'
        self.CONTEST_LIST_FILE = 'contests.json'
        self.CACHE_TIME = 20 * 60  # seconds
        self.api_url = api_url
        self.contest_list_url = api_url + 'contests/'
        self.contest_data_url = api_url + 'contest_participations/{id}'
        self.contest_data = []
        self.tick_lists = {}

        logging.basicConfig(filename='kisaviz.log',
                            filemode='a',
                            level=getattr(logging, loglevel),
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.log = logging.getLogger(__name__)

    def _fetch_json_from_api_cached(self, url, cache_file):
        reload = False
        result = None

        try:
            if datetime.timestamp(datetime.now()) - os.path.getmtime(cache_file) > self.CACHE_TIME:
                reload = True
        except FileNotFoundError:
            reload = True

        if not reload:
            self.log.info('Reading data from cache file: %s' % cache_file)
            try:
                with open(cache_file, 'r') as fp:
                    result = json.load(fp)
            except Exception as e:
                print(e)

            if not len(result):
                reload = True

        if reload:
            self.log.info('Reading data from URL: %s' % url)
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                with open(cache_file, 'w') as fp:
                    json.dump(result, fp)
                    self.log.info('Data saved to cache file: %s' % cache_file)

        return result

    def read_contest_data(self, id):
        contest_data = self._fetch_json_from_api_cached(self.contest_data_url.format(id=id),
                                                        self.CONTEST_PERSIST_FILE.format(id=id))

        for person in contest_data:
            species = person.pop('species_json')
            person['tick_list'] = json.loads(species)

        self.contest_data = contest_data
        self.tick_lists = [person['tick_list'] for person in self.contest_data if len(person['tick_list'])]

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
        return Counter([sp for ticks in self.tick_lists for (sp, sp_date) in ticks.items() if sp_date == date_instance.date().isoformat()])

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
            values.update({single_date: ticks.get(single_date.date().isoformat(), 0)})

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
            ticks.update({single_date.date().isoformat(): get_all_commonest(self.get_by_date(single_date))})

        return sorted(ticks.items())

    def get_all_species(self):
        """
        Get all species from data
        """
        return sorted(set([sp for ticks in self.tick_lists for sp in ticks.keys()]))

    def get_date_limits(self):

        local = pytz.timezone ("Europe/Helsinki")

        minimum = '9999-99-99'
        maximum = '1111-11-11'

        for ticks in self.tick_lists:
            mini = min(ticks.values())
            maxi = max(ticks.values())
            if mini < minimum:
                minimum = mini
            if maxi > maximum:
                maximum = maxi

        minimum = local.localize(dateutil.parser.parse(minimum), is_dst=None)
        maximum = local.localize(dateutil.parser.parse(maximum), is_dst=None)

        minimum += timedelta(hours=2)  # FIX TIMEZONE, AS BOKEH SEEMS TO IGNORE TZ FROM DATA
        maximum += timedelta(hours=2)

        return minimum, maximum

    def get_contests(self):
        contests = self._fetch_json_from_api_cached(self.contest_list_url, self.CONTEST_LIST_FILE)
        return sorted(contests, key=lambda c: c['date_end'], reverse=True)


if __name__ == '__main__':
    kisa = PinnakisaData()

    contests = kisa.get_contests()

    print(contests[3])
    kisa.read_contest_data(contests[3]['id'])

    print(kisa.get_all_species())
    print(kisa.get_daily_popular_ticks(*kisa.get_date_limits()))
