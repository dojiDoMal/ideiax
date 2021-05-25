from pytest import mark, fixture
from flatten_dict import flatten

from ..mail_util import MailUtil, mail


class TestMail:
    @fixture
    def context(self):
        return {
            'idea': {
                'title': 'Conquer the world!',
                'get_current_phase': {
                    'description': "Let's conquer the world, pink!",
                },
                'author': {
                    'user': {
                        'first_name': 'Juracy',
                    },
                },
            },
        }

    @fixture
    def base_params(self, context):
        return (
            '[IdeiaX] - Mail test',
            'ideax/phase_change_email.html',
            context,
            ['test@gmail.com', 'ideax@gmail.com'],
        )

    @mark.skip
    def test_generate_messages(self, base_params, context, mocker):
        base_parts = (
            'charset="utf-8"',
            '<!DOCTYPE html>',
            'inovacao@dataprev.gov.br',
            'https://t.me/InovacaoDataprev',
            'Ideia<sup>x</sup>',
        )

        mocker.patch.object(mail, 'get_connection')
        mail_util = MailUtil()
        messages = mail_util.generate_messages(*base_params)
        assert len(messages) == 2
        assert messages[0].content_subtype == 'html'
        assert messages[0].subject == '[IdeiaX] - Mail test'
        assert messages[0].to == ['test@gmail.com']

        # Fix html entities
        context['idea']['get_current_phase']['description'] = 'Let&#39;s conquer the world, pink!'

        for part in base_parts + tuple(flatten(context).values()):
            assert part in messages[0].body

    def test_send_messages(self, base_params, mocker):
        mocker.patch('ideax.mail_util.mail')
        generate = mocker.patch.object(MailUtil, 'generate_messages')
        generate.return_value = []
        send = mocker.patch.object(MailUtil, 'send_mail')
        mail_util = MailUtil()
        mail_util.send_messages(*base_params)
        generate.assert_called_once_with(*base_params)
        send.assert_called_once_with([])

    def test_send_mail(self, mocker):
        conn = mocker.Mock()
        connection = mocker.patch.object(mail, 'get_connection')
        connection.return_value = conn
        mail_util = MailUtil()
        mail_util.send_mail([])
        conn.open.assert_called_once()
        conn.send_messages.assert_called_once_with([])
        conn.close.assert_called_once()
