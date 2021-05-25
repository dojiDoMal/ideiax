# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestIdeaForm.test_invalid 1'] = {
    'category': [
        'This field is required.'
    ],
    'oportunity': [
        'This field is required.'
    ],
    'solution': [
        'This field is required.'
    ],
    'summary': [
        'This field is required.'
    ],
    'target': [
        'This field is required.'
    ],
    'title': [
        'This field is required.'
    ]
}
