# -*- coding: utf-8 -*-


class Candidate(object):
    """ Location candidate to review and search location DB for """
    def __init__(self, text):
        self.text = text
        self.parents = set()
        self.children = set()
        # Whether this candidate is a valid location
        self.is_location = False
        # Whether any of candidate parent and their parents and so on is
        # a valid location
        self.has_parent_location = False

    def add_parent(self, parent):
        self.parents.add(parent)
        parent.children.add(self)

    def get_all_children(self):
        result = self.children.copy()
        for child in self.children:
            result |= child.get_all_children()
        return result

    def mark_as_location(self):
        self.is_location = True
        for child in self.get_all_children():
            child.has_parent_location = True

    def __repr__(self):
        return '{}: "{}"'.format(type(self).__name__, self.text)


class CandidateDB(object):
    def __init__(self, text, max_phrase_len=0):
        """
        Build candidates tree
        Args:
            text (str): original text to search for locations mentions
            max_phrase_len (int): max chunk length to split text into when
                creating location candidates
        """
        self.text = text
        self.db = list(list())
        words = text.split()
        if not max_phrase_len or max_phrase_len > len(words):
            max_phrase_len = len(words)
        for level, phrase_len in enumerate(range(max_phrase_len, 0, -1)):
            self.db.append(list())
            for start_idx in range(0, len(words) - phrase_len + 1):
                candidate_words = words[start_idx:start_idx + phrase_len]
                candidate = Candidate(' '.join(candidate_words))
                self.db[level].append(candidate)
                for parent_idx in (start_idx, start_idx - 1,):
                    if level < 1 or parent_idx < 0:
                        continue
                    try:
                        parent = self.db[level - 1][parent_idx]
                        candidate.add_parent(parent)
                    except IndexError:
                        pass

    def get_candidates(self):
        for level in self.db:
            for candidate in level:
                if not candidate.has_parent_location:
                    yield candidate

    def __repr__(self):
        return '{}: "{}"'.format(type(self).__name__, self.text)
