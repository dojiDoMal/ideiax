from pytest import fixture


@fixture
def get_ip(ideax_views, mocker):
    patch = mocker.patch.object(ideax_views, 'get_ip')
    patch.return_value = '1.1.1.1'
    return patch


@fixture
def ideax_views():
    from .. import views  # noqa
    return views
