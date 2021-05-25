import os

from .badwords import Badword


class ProfanityCheck:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    badword = Badword(os.path.join(__location__, 'badwords.json'))

    @classmethod
    def wordcheck(cls, *args, **kwargs):
        return cls.badword
