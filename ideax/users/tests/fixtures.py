from pytest import fixture


@fixture
def sign_up_data():
    return {
        'username': 'ideax',
        'email': 'ideax@dtplabs.in',
        'password1': 'secret32878#$',
        'password2': 'secret32878#$',
    }
