import json

from ..badwords import Badword


class TestBadWord:
    def test_empty(self, ipsum, pangram):
        bd = Badword()
        assert '' not in bd
        assert pangram not in bd
        assert ipsum not in bd

    def test_found(self, ipsum, pangram, pangram_pt_br):
        bd = Badword()
        bd.blacklist = ('jabuti', 'ipsum')
        # New pythonic way
        assert '' not in bd
        assert pangram not in bd
        assert ipsum in bd  # ipsum
        assert pangram_pt_br in bd  # jabuti
        # Old method
        assert not bd.search_badwords('')
        assert not bd.search_badwords(pangram)
        assert bd.search_badwords(ipsum)  # ipsum
        assert bd.search_badwords(pangram_pt_br)  # jabuti

    def test_load_json(self, mocker):
        bd = Badword()
        assert not list(bd)
        assert bd.blacklist == []

        words = 'word test'.split()
        mock_open = mocker.patch('builtins.open', create=True)
        mock_open.side_effect = (
            mocker.mock_open(read_data=json.dumps(words)).return_value,
        )
        assert bd.load_json('bad.json') == words
        mock_open.assert_called_once_with('bad.json')

    def test_init(self, mocker):
        mock_load_json = mocker.patch.object(Badword, 'load_json')
        mock_load_json.return_value = ['one', 'two']

        bd = Badword()
        mock_load_json.assert_not_called()
        assert list(bd) == []
        assert bd.blacklist == []

        bd = Badword('bad.json')
        mock_load_json.assert_called_once_with('bad.json')
        assert list(bd) == ['one', 'two']
        assert bd.blacklist == ['one', 'two']
