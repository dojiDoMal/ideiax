from ...forms import SignUpForm
from ...views import SignUpView


class TestSignUpView:
    def test_get(self, rf):
        request = rf.get('/')
        view = SignUpView()
        view.request = request
        response = view.get(request)

        assert response.status_code == 200

    def test_invalid(self, rf, messages):
        data = {}
        request = rf.post('/', data)
        request._messages = messages
        view = SignUpView()
        view.request = request
        view.object = None
        response = view.form_invalid(SignUpForm(data))

        assert response.status_code == 200
        assert messages.is_error
        assert messages.messages == ['Invalid form!']

    def test_valid(self, sign_up_data, messages, mocker, db, rf):
        authenticate = mocker.patch('ideax.users.views.authenticate')
        login = mocker.patch('ideax.users.views.login')

        request = rf.post('/', sign_up_data)
        view = SignUpView()
        view.request = request
        view.object = None
        response = view.form_valid(SignUpForm(sign_up_data))

        authenticate.assert_called_once_with(
            username=sign_up_data['username'],
            password=sign_up_data['password1'])
        login.assert_called_once_with(request, authenticate.return_value)
        assert response.status_code == 302
        assert response.url == '/'
