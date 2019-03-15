========
Usage
========

To use geotext in a project::

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
