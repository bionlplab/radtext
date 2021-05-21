from abc import abstractmethod, ABC

UNCERTAINTY = "uncertainty"
NEGATION = "negation"

INCLUDE = 'include'
EXCLUDE = 'exclude'


class NegPattern(ABC):
    def __init__(self, id, category: str, pattern_str: str):
        self.id = id
        self.category = category
        self.pattern_str = pattern_str
        self.pattern_obj = self.compile()

    @abstractmethod
    def compile(self):
        raise NotImplementedError

    def __str__(self):
        return '[id=%s, category=%s, pattern=%s]' % (self.id, self.category, self.pattern_str)


class NegResult(ABC):
    def __init__(self, category: str, matcher, pattern: NegPattern, *args):
        self.category = category
        self.matchers = [matcher]
        self.patterns = [pattern]
        for i in range(0, len(args), 2):
            self.matchers.append(args[i])
            self.patterns.append(args[i+1])
        self.__span = self.get_span()
        self.__id = '-'.join(str(p.id) for p in self.patterns)
        self.__pattern_strs = '; '.join(p.pattern_str for p in self.patterns)
        self.__pattern_cats = '; '.join(p.category for p in self.patterns)

    def start(self):
        return self.__span[0]

    def end(self):
        return self.__span[1]

    def span(self):
        return self.__span

    @abstractmethod
    def get_span(self):
        raise NotImplementedError

    @property
    def id(self):
        return self.__id

    @property
    def pattern_strs(self):
        return self.__pattern_strs

    @property
    def pattern_cats(self):
        return self.__pattern_cats

    @classmethod
    def merge(cls, category: str, r1: 'NegResult', r2: 'NegResult') -> 'NegResult':
        args = []
        for m, p in zip(r1.matchers + r2.matchers, r1.patterns + r2.patterns):
            args.append(m)
            args.append(p)
        return cls(category, *args)

    def __str__(self):
        s = '[category=%s' % self.category
        for i, (m, p) in enumerate(zip(self.matchers, self.patterns)):
            s += ', match%d=%s, pattern%d=%s' % (i, m, i, p.pattern_str)
        s += ']'
        return s
