# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCategoryImageForm.test_invalid 1'] = {
    'category': [
        'This field is required.'
    ],
    'description': [
        'This field is required.'
    ],
    'image': [
        'This field is required.'
    ]
}
