# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSignUpForm.test_invalid 1'] = {
    'email': [
        'This field is required.'
    ],
    'password1': [
        'This field is required.'
    ],
    'password2': [
        'This field is required.'
    ],
    'username': [
        'This field is required.'
    ]
}
