# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUseTermForm.test_invalid 1'] = {
    'final_date': [
        'This field is required.'
    ],
    'init_date': [
        'This field is required.'
    ],
    'term': [
        'This field is required.'
    ]
}

snapshots['TestIdeaPhaseForm.test_invalid 1'] = {
    'name': [
        'This field is required.'
    ],
    'order': [
        'This field is required.'
    ]
}
