# -*- coding: utf-8 -*-

import re
from collections import namedtuple, Counter, OrderedDict

from geotext.models.candidate import CandidateDB
from geotext.tasks import db_tasks
from geotext.text_utils import get_words_counts, replace_non_ascii


class GeoText(object):
    """
    Extract cities, states and countries from the text

    Examples
    --------

    >>> geo_text = GeoText()
    >>> geo_text.read('London is a great city')
    >>> geo_text.results
    Results(countries=(), nationalities=(), states=(), cities=(City: London, England, United Kingdom,))
    >>> city = geo_text.results.cities[0]
    >>> city.__dict__
    {'_key': 'London',
     '_search_field': 'london',
     'country': Country: United Kingdom,
     'name': 'London',
     'population': 7556900,
     'state': State: England, United Kingdom}

    >>> GeoText().read('New York, Texas, and also China').get_country_mentions()
    OrderedDict([(Country: United States, 2), (Country: China, 1)])
    """  # noqa
    LOCATION_REGEX = r"[A-Z]+[a-z]*(?:[ '-][A-Z]+[a-z]*)*"
    GeoDB = namedtuple(
        'GeoDB',
        'country_db,state_db,city_db,nationality_db,city_abbreviation_db,'
        'country_abbreviation_db'
    )
    Results = namedtuple('Results', 'countries,nationalities,states,cities')

    def __init__(self, text=''):
        self.results = GeoText.Results((), (), (), ())
        self.text = text
        self._build_geodb()
        if text:
            self.read(text)

    def _build_geodb(self):
        """
        Load information from the data directory
        """
        country_db = db_tasks.create_country_db()
        state_db = db_tasks.create_state_db(country_db)
        city_db = db_tasks.create_city_db(state_db, country_db)
        nationality_db = db_tasks.create_nationality_db(country_db)
        city_abbreviation_db = db_tasks.create_city_abbreviations_db(city_db)
        country_abbreviation_db = db_tasks.create_country_abbreviations_db(
            country_db
        )
        self._geodb = GeoText.GeoDB(
            country_db, state_db, city_db, nationality_db,
            city_abbreviation_db, country_abbreviation_db
        )
        self._max_location_length = self._get_locations_length()[0]

    def _get_locations_length(self):
        words_counts = set()
        for collection in self._geodb:
            words_counts |= get_words_counts(
                [place._search_field for place in collection.all()]
            )
        return sorted(words_counts, reverse=True)

    def _get_candidates(self, text):
        text = replace_non_ascii(text)
        # Remove dots from acronyms:
        text = re.sub(r'\.(?![a-z]{2})', '', text, flags=re.IGNORECASE)
        # Replace other symbols with spaces
        # TODO: improve this, since DB has unicode symbols in cities
        text = re.sub(r'[^\w]+', ' ', text).strip()

        return CandidateDB(
            text, max_phrase_len=self._max_location_length
        ).get_candidates()

    def read(self, text, min_population=0, skip_nationalities=False):
        self.text = text
        candidates = self._get_candidates(text)
        (
            countries, nationalities, states, cities,
        ) = self._get_locations_from_candidates(
            candidates, min_population, skip_nationalities
        )
        self.results = GeoText.Results(
            countries, nationalities, states, cities
        )
        return self

    def get_country_mentions(self):
        states_to_ignore = set()
        countries_to_ignore = set()
        country_mentions = []
        for city in self.results.cities:
            country_mentions.append(city.country)
            if city.state:
                states_to_ignore.add(city.state)
            countries_to_ignore.add(city.country)
        for state in self.results.states:
            if state in states_to_ignore:
                continue
            country_mentions.append(state.country)
            countries_to_ignore.add(state.country)
        for country in self.results.countries:
            if country in countries_to_ignore:
                continue
            country_mentions.append(country)
        for nationality in self.results.nationalities:
            if nationality in countries_to_ignore:
                continue
            country_mentions.append(nationality)
        return OrderedDict(
            Counter(country_mentions).most_common()
        )

    def _get_locations_from_candidates(
        self, candidates, min_population, skip_nationalities
    ):
        countries, nationalities, states, cities = set(), set(), set(), set()
        for candidate in candidates:
            # When iterating over the candidates we apply the following
            # priorities:
            # 1) Cities abbreviations: NYC or LA (since e.g. LA usually
            #    means Los Angeles, not Louisiana)
            # 2) US short states names: "CA" (California)
            # 3) Countries + country codes: "GB", "RU"
            # 4) Nationalities (treated as countries found)
            # 5) Countries abbreviations: other shortcuts, like "USA" or "UK"
            # 6) Cities
            # 7) Full text state names: "Texas"

            # 1
            city_abbrev_match = self._geodb.city_abbreviation_db.search(
                candidate.text
            )
            if (
                city_abbrev_match
                and (city_abbrev_match.place.population >= min_population)
            ):
                cities.add(city_abbrev_match.place)
                candidate.mark_as_location()
                continue

            # 2
            state_match = (
                self._geodb.state_db.search('US.{}'.format(candidate.text))
            )
            if (
                state_match
                and state_match.country.population >= min_population
            ):
                states.add(state_match)
                candidate.mark_as_location()
                continue

            # 3
            country_match = (
                self._geodb.country_db.search(candidate.text)
                or self._geodb.country_db.search(candidate.text.lower())
            )
            if country_match and country_match.population >= min_population:
                countries.add(country_match)
                candidate.mark_as_location()
                continue

            # 4
            if not skip_nationalities:
                nationality_match = self._geodb.nationality_db.search(
                    candidate.text.lower()
                )
                if (
                    nationality_match
                    and nationality_match.place.population >= min_population
                ):
                    nationalities.add(nationality_match.place)
                    candidate.mark_as_location()
                    continue

            # 5
            country_abbrev_match = self._geodb.country_abbreviation_db.search(
                candidate.text
            )
            if (
                country_abbrev_match
                and country_abbrev_match.place.population >= min_population
            ):
                countries.add(country_abbrev_match.place)
                candidate.mark_as_location()
                continue

            # 6
            city_match = self._geodb.city_db.search(candidate.text.lower())
            if city_match and city_match.population >= min_population:
                cities.add(city_match)
                candidate.mark_as_location()
                continue

            # 7
            state_match = (
                self._geodb.state_db.search(candidate.text.lower())
            )
            if (
                state_match
                and state_match.country.population >= min_population
            ):
                states.add(state_match)
                candidate.mark_as_location()
                continue
        return (
            tuple(countries), tuple(nationalities), tuple(states),
            tuple(cities),
        )
