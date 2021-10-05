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

import unittest
import sys

sys.path.append("lib")  # noqa
sys.path.append("src")  # noqa

from ops.testing import Harness

import charm


class _CinderCephVictoriaOperatorCharm(charm.CinderCephVictoriaOperatorCharm):
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


class TestCinderCephOperatorCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(_CinderCephVictoriaOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_pebble_ready_handler(self):
        self.assertEqual(self.harness.charm.seen_events, [])
        self.harness.container_pebble_ready("cinder-volume")
        self.assertEqual(self.harness.charm.seen_events, ["PebbleReadyEvent"])
