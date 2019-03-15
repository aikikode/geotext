# -*- coding: utf-8 -*-
import os

from geotext.models.city import City
from geotext.models.country import Country
from geotext.models.place_link import PlaceLink
from geotext.models.place import PlaceDB
from geotext.models.state import State
from geotext.text_utils import (
    replace_non_ascii, fix_location_name, canonize_location_name,
)

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data_path(path):
    return os.path.join(_ROOT, '..', 'data', path)


COUNTRIES_FILE = get_data_path('countryInfo.txt')
CITIES_FILE = get_data_path('cities15000.txt')
STATES_FILE = get_data_path('admin1CodesASCII.txt')

CITIES_ABBREVIATIONS_FILE = get_data_path('cities_abbreviations.txt')
COUNTRIES_ABBREVIATIONS_FILE = get_data_path('countries_abbreviations.txt')

NATIONALITIES_FILE = get_data_path('nationalities.txt')


def _read_data_file(
    filename, usecols=(0, 1), sep='\t', comment='#', population_field_num=None,
    filter_method=None
):
    """
    Parse data files from the data directory

    Data files are provided by GeoNames service: http://www.geonames.org/
    Files format defined in GeoNames readme file:
    http://download.geonames.org/export/dump/readme.txt

    Args:
        filename (str): Full path to file

        usecols (list of int): list of fields indexes to return, default [0, 1]
            The first element will be used as a key in case of conflict so keep
            it unique. Defaults to the first two columns of `filename`.

        sep (str):  Field delimiter, defaults to '\t'.

        comment (str): default '#'
            Indicates remainder of line should not be parsed. If found at the
            beginning of a line, the line will be ignored altogether. This
            parameter must be a single character.

        population_field_num (int): default None
            If set: this should define the field with location population count
            to use for conflicts resolution: if there're several locations with
            same name, the one with larger population will be taken.
            If set to None, only the last one will be taken.

        filter_method (method): default None
            Only lines that pass this filter are used
            Method receives one param: line split by defined separator into a
            list

    Returns:
        A list of tuples with specified fields of input file
    """

    d = dict()
    with open(filename, 'r') as f:
        location_population = dict()
        for line in f:
            if line.startswith(comment):
                continue
            columns = line.split(sep)
            if filter_method and not filter_method(columns):
                continue
            values = [
                replace_non_ascii(columns[idx].rstrip('\n'))
                for idx in usecols
            ]
            values[0] = fix_location_name(values[0])
            key = canonize_location_name(values[0])

            if population_field_num is not None:
                population = int(columns[population_field_num])
                if key in d and location_population[key] > population:
                    continue
                location_population[key] = population

            d[key] = values
    return d.values()


def create_country_db():
    country_db = PlaceDB()
    for (
        country_name, country_code, population,
    ) in _read_data_file(COUNTRIES_FILE, usecols=[4, 0, 7]):
        country_db.add(
            Country(
                country_code, country_name,
                canonize_location_name(country_name), int(population)
            )
        )
    return country_db


def create_state_db(country_db):
    state_db = PlaceDB()
    for data in _read_data_file(STATES_FILE):
        country_code = data[0].split('.')[0]
        state_db.add(
            State(
                data[0], data[1], canonize_location_name(data[1]),
                country_db[country_code]
            )
        )
    return state_db


def create_city_db(state_db, country_db):
    city_db = PlaceDB()
    # Field 14 is population, see
    # http://download.geonames.org/export/dump/readme.txt
    # for reference
    for (
        city_name, country_code, state_code_part, population,
    ) in _read_data_file(
        CITIES_FILE, usecols=[1, 8, 10, 14], population_field_num=14,
    ):
        if state_code_part:
            state_code = '{}.{}'.format(country_code, state_code_part)
            state = state_db[state_code]
        else:
            state = None
        country = country_db[country_code]
        city_db.add(
            City(
                city_name, city_name, canonize_location_name(city_name),
                int(population), state, country
            )
        )
    return city_db


def create_nationality_db(country_db):
    nationality_db = PlaceDB()
    for (
        nationality_name, country_code,
    ) in _read_data_file(NATIONALITIES_FILE):
        pass
        country = country_db[country_code]
        nationality_db.add(
            PlaceLink(
                nationality_name, nationality_name,
                canonize_location_name(nationality_name), country
            )
        )
    return nationality_db


def create_city_abbreviations_db(city_db):
    city_abbreviations_db = PlaceDB()
    for (
        city_abbrevation, city_name,
    ) in _read_data_file(CITIES_ABBREVIATIONS_FILE):
        city = city_db[canonize_location_name(city_name)]
        city_abbreviations_db.add(
            PlaceLink(
                city_abbrevation, city_abbrevation, city_abbrevation, city
            )
        )
    return city_abbreviations_db


def create_country_abbreviations_db(country_db):
    country_abbreviations_db = PlaceDB()
    for (
        country_abbrevation, country_code,
    ) in _read_data_file(COUNTRIES_ABBREVIATIONS_FILE):
        country = country_db[country_code]
        country_abbreviations_db.add(
            PlaceLink(
                country_abbrevation, country_abbrevation, country_abbrevation,
                country
            )
        )
    return country_abbreviations_db
