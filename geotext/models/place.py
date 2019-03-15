# -*- coding: utf-8 -*-


class Place(object):
    """ Geographic place """
    def __init__(self, key, name, search_field, population=None):
        """
        Args:
            key (str): unique key that identifies this place in the database
            name (str): location name, e.g. "London", "France", "California"
            search_field (str): canonized location name that will be used to
                search for this place, e.g. if name is "Washington, D.C.", then
                search field may be "washington dc". This field depends on the
                text processing algo you are using
            population (int): number of people living there or None if unknown
        """
        self._key = key
        self.name = name
        self.population = population
        self._search_field = search_field

    def __repr__(self):
        return '{}: {}'.format(type(self).__name__, self.name)


class PlaceDB(object):
    """ Geographic place database """
    def __init__(self):
        self._objects_by_key = dict()
        self._objects_by_text = dict()

    def add(self, place):
        self._objects_by_key[place._key] = place
        # TODO: store multiple places under one search field as it's not unique
        self._objects_by_text[place._search_field] = place

    def search(self, text):
        return self._objects_by_key.get(text) or self._objects_by_text.get(
            text
        )

    def all(self):
        for item in self._objects_by_key.values():
            yield item

    def __getitem__(self, item):
        return self._objects_by_key.get(item) or self._objects_by_text.get(
            item
        )

    def __contains__(self, item):
        if isinstance(item, Place):
            return item._key in self._objects_by_key
        return item in self._objects_by_key or item in self._objects_by_text
