# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureTestCase

from azure.data.tables import TableServiceClient
from _shared.testcase import TableTestCase, SLEEP_DELAY
from preparers import CosmosPreparer

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                         '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                         '></StorageServiceStats> '


# --Test Class -----------------------------------------------------------------
class TableServiceStatsTest(AzureTestCase, TableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        assert stats is not None
        assert stats['geo_replication'] is not None

        assert stats['geo_replication']['status'] ==  'live'
        assert stats['geo_replication']['last_sync_time'] is not None

    def _assert_stats_unavailable(self, stats):
        assert stats is not None
        assert stats['geo_replication'] is not None

        assert stats['geo_replication']['status'] ==  'unavailable'
        assert stats['geo_replication']['last_sync_time'] is None

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda _: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY

    # TODO: Should we remove these both from cosmos sync/async?
    # --Test cases per service ---------------------------------------
    @pytest.mark.skip("JSON is invalid for cosmos")
    @CosmosPreparer()
    def test_table_service_stats_f(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        stats = tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        self._assert_stats_default(stats)

        self.sleep(SLEEP_DELAY)

    @pytest.mark.skip("JSON is invalid for cosmos")
    @CosmosPreparer()
    def test_table_service_stats_when_unavailable(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        stats = tsc.get_service_stats(raw_response_hook=self.override_response_body_with_unavailable_status)
        self._assert_stats_unavailable(stats)

        self.sleep(SLEEP_DELAY)
