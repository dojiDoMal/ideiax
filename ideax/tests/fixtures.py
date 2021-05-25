import logging

from base64 import b64decode
from datetime import date

from django.contrib.messages import constants
from django.utils import translation

from pytest import fixture


class FakeMessages:
    ''' mocks the Django message framework, makes it easier to get
    the messages out '''

    def __init__(self):
        self.messages = []
        self.levels = []

    def add(self, level, message, extra_tags):
        self.messages.append(str(message))
        self.levels.append(level)

    def __iter__(self):
        return iter(self.messages)

    @property
    def is_success(self):
        return self.levels[-1] == constants.SUCCESS

    @property
    def is_error(self):
        return self.levels[-1] == constants.ERROR

    @property
    def pop(self):
        return self.messages.pop()


class MockDate(date):
    fix_date = date(2010, 1, 1)

    @classmethod
    def today(cls):
        return cls.fix_date


@fixture
def test_image(settings):
    # https://www.daniweb.com/programming/software-development/code/440446/python2-python3-base64-encoded-image
    rainbow_jpg_b64 = '''\
        /9j/4AAQSkZJRgABAQEAyADIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB
        AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEB
        AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAoACgDASIA
        AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA
        AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3
        ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm
        p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA
        AwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx
        BhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK
        U1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3
        uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+VL4J
        /Aj4eeN/hNo+uan4a0mXWDo1pLNdNZQF7hvKh3TTOUP78f8ALWQk+aD1888+lfBf9lf4ceMvFF5p
        d54Y0q4jt7wwpHJY28q7dkZx/qzwDz0681vfst/8kU0n/sCWn/pNDX0/+x/DFJ8RNW8xd/8AxNB9
        7d/cTH06/wBM1/sn9Eb6OXhx4n/Rrx3FWeZHl9XPcuwuMl9fq4SlUrVVHGyp03Ko4cynCKUE1LVb
        p2P6H/aG5/gfCD6O/AHFfC+QZTgs3x/AuU4vF4zB4HC4XE18T/ZWGnPEVKtKjGVStNyc6lWT5pyv
        KTbk2fTnhX/glZ8DtU8Pw6hL8PPD8jyfxNpNmzen/Pv6cH2Ne5+Bf+COfwA1vQtQvrj4Z+G5JbeG
        R1ZtHseqOh6/Z/6j9K/Wn4Z6bY/8IPZ/6LGPuddw/wCWa/T/ACOOOn2F8JdL0+P4f+JpFtY1kTT7
        plbLfK29P85Nf8k/7TLxQ408GfF+XD3BvEOa5VgVi6tONHAYzEYakksTRhFOFKpBWtK2nTzZ/hX+
        zk+mDx34wfSXwfBnF1JZnk08fmVOWExs44ihy0alKMIyp1YTi7KTsrW00Suz+H39v/8AYw+D37P3
        w/8AFV54b8GaFY61BpN8YLiHTbWOSyZYZQsyhI/kuMY8mQ/6nAx+/A8or7I/4LJf8iV40/7Buof+
        iJqK/p36HvEeecV+FNLOM+zTGZnmGIx7dTE42tPFVbfVqElCM6znKMIvaKdr3drtn/Q59M/IMi4e
        4m8PMNkWT5dk+HxPAtDGV6OXYTD4SFbE1cwxHPXrKhSgqtVxjCHtJpz5IxjeysfnB+y3/wAkU0n/
        ALAlp/6TQ19Sfsdf8lD1b/sJ/wDsiV8t/st/8kU0n/sCWn/pNDX0/wDsezRx/ETVtzqv/E16N3wi
        Z6de3X+Vf9W/7PyUY/RK4h5pRing8Yk5O128wnZJvTvu1sfiH7WSMp/RS8M1GLk/+Ie5VpFNv/kU
        YTokf1C/DH/kRrP6r/6LWvsT4Uf8k68Vf9gy6/8ARkdfGXwwvrP/AIQez/0iE/Mv8S/3E/z+fbNf
        YXwlvrNvh/4ojWeFpDp10qr5i7mben5fX+Vf8NX7Y28/HxuKckswrXcU5JL67hm22lay9dvPQ/5m
        P2R9GtD6YWAc6VSK/tTNneUJJf7xR0d4pLa+/wCtv5Qf+CyX/IleNP8AsG6h/wCiJqKP+CyX/Ile
        NP8AsG6h/wCiJqK/sT6DX/JlcH/2Hf8AurQP+uz6c/8AyVnhr/2bzCf+p+JPx7+Cfx2+HXgj4TaP
        oWq+JtIi1c6NaJNaNewB7aTyoh5Uyl8pOSP3qHmIg5GcgemfBP8Aam+GfgrxReanf+J9It45rzzl
        kkv7dVZNiJ08zts+mc0UV/rd4cfSM8TeBvDpcEcO4/AYXInRr05U5YWtOvNVa3tJynUji6cJScnu
        6VrJLlPxrx44rxHirwDw7wfxbleTYjJsoyDAZThYYbC4mlXeGw2Co0ISq1K2MxEJ1pwgnUnGnCEp
        NtU4qyX6z+E/+CqvwH0nw/b6fJ8RfDaSx8bW1izV0yuP+eg7nHrnjqa908B/8Fj/ANnnQdB1DT7j
        4m+GIZLmGSMK2tWS9WT/AKeD16+45oor/Kj6RfgnwV4zcUvP+No5piMxdWU3PB4rD0KfNOcKj9yv
        g8U7c0U7c3kfxb4A+Cfhv4QeIlHjLgzh6hh87p1q9aNTGP29HnqzhKV6dGOGm1eKt+8uu5+Tn/BQ
        X9s34NftBfD/AMVWvhfxroF7rU2k3629rb6naSNfN5MvyQoj/vJ/+eMf/Lf3uP8AWlFFfp/gnwLk
        nh7wrU4fyCeO/s6ni/bU442vSrVISlThBwjOjQw8fZpU4uMXBuLbs0uVR/tLx98Q898Q8z4VzDPK
        WXUK+V5DLKcOssoV8NTnhqOLlWpyrRr4rFOVZOrKLnCVOLhGPucycn//2Q==
        '''

    return b64decode(rainbow_jpg_b64.encode())


@fixture(scope='function')
def messages():
    return FakeMessages()


@fixture
def debug():
    return logging.warn


@fixture
def mock_today():
    return MockDate


@fixture
def set_pt_br_language():
    translation.activate('pt_br')


@fixture
def ipsum():
    return """\
        Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco
        laboris nisi ut aliquip ex ea commodo consequat.

        Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint
        occaecat cupidatat non proident, sunt in culpa qui officia
        deserunt mollit anim id est laborum."""


@fixture
def pangram():
    return 'The quick brown fox jumps over the lazy dog'


@fixture
def pangram_pt_br():
    return '''\
        À noite, vovô Kowalsky vê o ímã cair no pé do pinguim queixoso e
        vovó põe açúcar no chá de tâmaras do jabuti feliz'''


@fixture
def common_user(mocker):
    user = mocker.Mock()
    user.username = 'common'
    user.first_name = 'Common'
    user.last_name = 'Idea'
    user.get_full_name = lambda: 'Common Idea'
    user.email = 'common.idea@dtplabs.in'
    user.has_perms.return_value = False
    return user


@fixture
def factory_user(mocker):
    """mock for user with a specific permission"""
    def user(permission):
        user = mocker.Mock()
        user.has_perms.side_effect = lambda permissions: permissions == (permission,)
        return user
    return user
