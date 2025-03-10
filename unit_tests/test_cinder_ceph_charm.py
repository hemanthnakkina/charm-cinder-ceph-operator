#!/usr/bin/env python3

# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json

sys.path.append("lib")  # noqa
sys.path.append("src")  # noqa

import charm
import ops_sunbeam.test_utils as test_utils

from ops.testing import (
    Harness,
)


class _CinderCephOperatorCharm(charm.CinderCephOperatorCharm):

    openstack_release = "wallaby"

    def __init__(self, framework):
        self.seen_events = []
        self.render_calls = []
        super().__init__(framework)

    def _log_event(self, event):
        self.seen_events.append(type(event).__name__)

    def renderer(
        self,
        containers,
        container_configs,
        template_dir,
        openstack_release,
        adapters,
    ):
        self.render_calls.append(
            (
                containers,
                container_configs,
                template_dir,
                openstack_release,
                adapters,
            )
        )

    def _on_service_pebble_ready(self, event):
        super()._on_service_pebble_ready(event)
        self._log_event(event)


def add_complete_storage_backend_relation(harness: Harness) -> None:
    """Add complete storage-backend relation."""
    storage_backend_rel = harness.add_relation(
        "storage-backend", "cinder"
    )
    harness.add_relation_unit(
        storage_backend_rel, "cinder/0"
    )
    harness.update_relation_data(
        storage_backend_rel,
        "cinder",
        {
            "ready": json.dumps("true")
        }
    )


class TestCinderCephOperatorCharm(test_utils.CharmTestCase):

    PATCHES = []

    def setUp(self):
        super().setUp(charm, self.PATCHES)
        self.harness = test_utils.get_harness(
            _CinderCephOperatorCharm,
            container_calls=self.container_calls)
        self.addCleanup(self.harness.cleanup)

    def test_all_relations(self):
        self.harness.begin_with_initial_hooks()
        test_utils.add_complete_ceph_relation(self.harness)
        test_utils.add_complete_amqp_relation(self.harness)
        test_utils.add_complete_db_relation(self.harness)
        add_complete_storage_backend_relation(self.harness)
        test_utils.set_all_pebbles_ready(self.harness)
        self.assertTrue(self.harness.charm.relation_handlers_ready())
