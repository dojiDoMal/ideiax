from ...forms import SignUpForm


class TestSignUpForm:
    def test_invalid(self, snapshot):
        form = SignUpForm({})
        assert not form.is_valid()
        assert len(form.errors) == 4
        snapshot.assert_match(form.errors)

    def test_valid(self, sign_up_data, db, snapshot):
        """Check for uniqueness needs database"""
        form = SignUpForm(sign_up_data)
        assert form.is_valid()

    def test_invalid_password_check(self, sign_up_data, db):
        sign_up_data['password1'] = '12345678'
        sign_up_data['password2'] = '12345679'
        form = SignUpForm(sign_up_data)
        assert not form.is_valid()
        assert form.errors['password2'] == [
            "The two password fields didn't match.",
        ]

    def test_invalid_password_common(self, sign_up_data, db):
        sign_up_data['password1'] = '12345678'
        sign_up_data['password2'] = '12345678'
        form = SignUpForm(sign_up_data)
        assert not form.is_valid()
        assert form.errors['password2'] == [
            'This password is too common.',
            'This password is entirely numeric.',
        ]

    def test_invalid_password_username(self, sign_up_data, db):
        sign_up_data['password1'] = sign_up_data['username']
        sign_up_data['password2'] = sign_up_data['username']
        form = SignUpForm(sign_up_data)
        assert not form.is_valid()
        assert form.errors['password2'] == [
            'The password is too similar to the username.',
            'This password is too short. It must contain at least 8 characters.',
        ]
