# -*- coding: utf-8 -*-
import pytest

from geotext import GeoText
from geotext.text_utils import get_words_counts


@pytest.mark.parametrize(
    (
        'limit,skip_nationalities,text,'
        'cities,countries,nationalities,states,country_mentions'
    ),
    [
        (
            0, False, 'London is a great city', ['London', ], [], [], [],
            [(u'GB', 1,), ],
        ),
        (
            0, False, 'Voronezh and New York',
            ['Voronezh', 'New York', ], [], [], [],
            [(u'RU', 1,), (u'US', 1,), ],
        ),
        (
            0, False,
            "I am from Washington. So I'm American, although I live in "
            "Manchester.",
            ['Washington', 'Manchester', ], [], ['United States', ], [],
            [(u'GB', 2,), (u'US', 1,), ],
        ),
        (
            0, True,
            "I am from Washington. So I'm American, although I live in "
            "Manchester.",
            ['Washington', 'Manchester', ], [], [], [],
            [(u'GB', 2,), ],
        ),
        (
            0, False, 'IT consultant from Germany', [], ['Germany', 'Italy', ],
            [], [], [(u'DE', 1,), (u'IT', 1,)],
        ),
        (
            0, False, 'germany london', ['London', ], ['Germany', ], [], [],
            [(u'GB', 1,), (u'DE', 1,), ],
        ),
        (
            0, False,
            'name of the munich writer, singer and photographer',
            ['Munich', 'Of', ], [], [], [],
            [(u'DE', 1,), (u'TR', 1,), ],
        ),
        (
            500000, False,
            'name of the munich writer, singer and photographer',
            ['Munich', ], [], [], [], [(u'DE', 1,), ],
        ),
        (
            0, False, 'Voronezh and NY', ['Voronezh', 'New York', ], [],
            [], [], [(u'RU', 1,), (u'US', 1,), ],
        ),
        (
            0, False, 'I live in Washington DC', ['Washington, D.C.', ],
            [], [], [], [(u'US', 1,), ],
        ),
        (
            0, False, 'I live in Washington D.C. but used to live in NY',
            ['Washington, D.C.', 'New York', ], [], [], [],
            [(u'US', 2,), ],
        ),
        (
            0, False, 'I am from Izumiōtsu but lived in Воронеж',
            ['Izumiotsu', 'Voronezh', ], [], [], [],
            [(u'RU', 1,), (u'JP', 1,), ],
        ),
        (
            0, False, 'It is sunny in California', [], [], [],
            ['California', ], [(u'US', 1,), ],
        ),
        (
            0, False, 'It is sunny in LA CA', ['Los Angeles'], [], [],
            ['California', ], [(u'US', 1,), ],
        ),
    ]
)
def test_read(
    limit, skip_nationalities, text, cities, countries, nationalities, states,
    country_mentions
):
    geo_text = GeoText()
    geo_text.read(
        text, min_population=limit, skip_nationalities=skip_nationalities
    )
    assert set(map(lambda c: c.name, geo_text.results.cities)) == set(cities)
    assert set(map(lambda c: c.name, geo_text.results.states)) == set(states)
    assert set(map(lambda c: c.name, geo_text.results.countries)) == set(
        countries
    )
    assert set(map(lambda c: c.name, geo_text.results.nationalities)) == set(
        nationalities
    )
    assert {
        (k._key, v) for k, v in geo_text.get_country_mentions().items()
    } == set(country_mentions)


@pytest.mark.parametrize(
    'phrases,result',
    [
        ([], set(),),
        (['hello', 'hi', ], {1, },),
        (['hello', 'hi', 'hello, world and all', ], {1, 4, },),
    ]
)
def test_get_words_counts(phrases, result):
    assert get_words_counts(phrases) == result
