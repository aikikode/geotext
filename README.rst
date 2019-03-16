===============================
geotext
===============================

GeoText extracts countries, nationalities, states and cities mentions from text.

It gets a block of text as input and produces a tuple of `Place` objects as a result representing detected countries, nationalities, states and cities.

Each `Place` object has the following fields:

- `name`: name of the palce, e.g. 'London', 'New York' for cities; 'France', 'Germany' for countries, etc.

- `population`: number of people living in this place, available only for cities and countries

Also there're additional place-specific fields.

`City` has:

- `state`: (optional, None by default) a `State` object representing region of the city, e.g. "State: California, United States"

-  `country`: a `Country` (`Place`) object of this city

`State` has:

- `country`: a `Country` (`Place`) object of this state/region

`Nationality` object is the same as `Country` object ans represents countries mentioned by nationality.

See usage below for details.

* Free software: MIT license

Usage
-----
.. code-block:: python

        from geotext import GeoText

        geo_text = GeoText()
        geo_text.read(
            "I'm French, but live in NY. "
            "I like to visit my friends in France from time to time."
        )
        geo_text.results
        # Results(
        #     countries=(Country: France,),
        #     nationalities=(Country: France,),
        #     states=(),
        #     cities=(City: New York, New York, United States,)
        # )
        [city.name for city in geo_text.results.cities]
        # ['New York']
        city = geo_text.results.cities[0]
        city.__dict__
        # {'_key': 'New York',
        #  'name': 'New York',
        #  'population': 8175133,
        #  '_search_field': 'new york',
        #  'state': State: New York, United States,
        #  'country': Country: United States}
        [country.name for country in geo_text.results.countries]
        # ['France']
        geo_text.get_country_mentions()
        # OrderedDict([(Country: France, 2), (Country: United States, 1)])

        GeoText('Voronezh and NY').get_country_mentions()
        # OrderedDict([(Country: Russia, 1), (Country: United States, 1)])

        GeoText('I live in Izumiōtsu').results.cities
        # (City: Izumiotsu, Osaka, Japan,)

        # Take only large cities into account
        GeoText().read(
            'Voronezh and New York', min_population=1000000
        ).get_country_mentions()
        # OrderedDict([(Country: United States, 1)])

Features
--------
- Fast
- Data from http://www.geonames.org licensed under the Creative Commons Attribution 3.0 License.

Similar projects
----------------
`geography
<https://github.com/ushahidi/geograpy>`_: geography is more advanced and bigger in scope compared to geotext and can do everything geotext does. On the other hand geotext is leaner: has no external dependencies, is faster (re vs nltk) and also depends on libraries and data covered with more permissive licenses.
