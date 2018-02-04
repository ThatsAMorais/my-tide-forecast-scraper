#!/usr/bin/python
"""
Tide Forecast Scraper

Scrapes the daytime low-tides from www.tide-forecast.com and reports
them in a parseable format.
"""

import datetime
import json
import re
import sys
import time

import requests
from lxml import html


class TideForecastPage:
    """
    A tide forecast scraper
    """
    TIDE_FORECAST_BY_LOCATION = 'https://www.tide-forecast.com/locations'
    ALL_DAYS = 'tides/latest'
    TIDE_TABLE = '//*[@id="main"]/section/table'
    LOW_TIDES_KEY = 'low-tides'

    def scrape_low_tides(self, locations):
        """
        Scrapes "useful" low-tide times(during the day) for a set of locations
        """
        location_map = dict()
        for location_name in locations:
            if location_name:
                location, beach_only = self._normalize_location_name(location_name)
                location_map[location] = self._scrape_location(location, beach_only)
        return location_map

    @staticmethod
    def _read(url):
        """
        Request a page and parse it into an lxml tree
        """
        page = requests.get(url)
        return html.fromstring(page.content)

    def _scrape_location(self, location, beach_only=None):
        """
        Scrapes a single location for a number of data points for all days available on the page
        """
        location_page = self._read(
            '/'.join((self.TIDE_FORECAST_BY_LOCATION, location, self.ALL_DAYS))
        )
        tide_table = location_page.xpath(self.TIDE_TABLE)
        if not tide_table:
            # Try the beach-only name
            location_page = self._read(
                '/'.join((self.TIDE_FORECAST_BY_LOCATION, beach_only, self.ALL_DAYS))
            )
            tide_table = location_page.xpath(self.TIDE_TABLE)

        result = dict()
        if tide_table:
            result[self.LOW_TIDES_KEY] = self._parse_daylight_low_tide(tide_table[0])

        return result

    @staticmethod
    def _parse_daylight_low_tide(table, max_days=None):
        """
        Parse the tide table into a set of time's mapped to tide height (ft), excluding
        times after sunset and before sunrise
        """

        low_tides = dict()
        days = 0
        daylight = False
        for tr in table.xpath('.//tr'):
            fields = tr.xpath('.//td')
            fields.reverse()

            if fields[0].text_content() == 'Sunrise':
                daylight = True
                days += 1
                continue

            if not daylight:
                continue

            if fields[0].text_content() == 'Sunset':
                daylight = False
                if max_days is not None and days >= max_days:
                    break
                continue
            if fields[0].text_content() == 'Low Tide':
                height_field = fields[1].text_content().replace('(', '').replace(')', '')
                low_tides[fields[4].text_content().strip()] = height_field
        return low_tides

    @staticmethod
    def _normalize_location_name(location):
        """
        Converts a location name, containing spaces and commas, to a hyphenated string suitable for
        querying tide-forecast via URL.
        """
        beach, city = location.split(', ')
        return ' '.join((beach, city)).replace(' ', '-'), beach.replace(' ', '-')


def main(*args):
    """
    Read the tide forecast page, parse, query based on input, return results.
    """
    input_filename = args[1]
    tide_forecast_page = TideForecastPage()
    results = tide_forecast_page.scrape_low_tides(
        locations=[line.strip() for line in open(input_filename)]
    )

    with open(datetime.datetime.now().date().isoformat(), 'w') as outfile:
        json.dump(results, outfile, indent=4)
    print(json.dumps(results, indent=4))

if __name__ == '__main__':
    main(*sys.argv)
