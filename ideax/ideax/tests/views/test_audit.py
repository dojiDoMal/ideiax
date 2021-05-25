from ....util import audit, logger


class TestAudit:
    def test_audit(self, mocker):
        mock = mocker.patch.object(logger, 'info')
        audit('test_user', '127.0.0.1', 'TEST', 'TestAudit', 444)
        mock.assert_called_once_with(
            '%(username)s|%(ip_addr)s|%(operation)s|%(class_name)s|%(object_id)s',
            {
                'username': 'test_user',
                'ip_addr': '127.0.0.1',
                'operation': 'TEST',
                'class_name': 'TestAudit',
                'object_id': 444,
            }
        )
