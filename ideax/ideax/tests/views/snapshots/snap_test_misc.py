# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestNonMiscView.test_get_phases 1'] = [
    (
        1,
        'Discussion'
    ),
    (
        2,
        'Evaluation'
    ),
    (
        3,
        'Ideation'
    ),
    (
        4,
        'Approval'
    ),
    (
        5,
        'Evolution'
    ),
    (
        6,
        'Done'
    ),
    (
        7,
        'Archived'
    ),
    (
        8,
        'Paused'
    )
]
