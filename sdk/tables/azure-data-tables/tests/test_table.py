# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

import sys
import locale
import os
from datetime import datetime, timedelta

from devtools_testutils import AzureTestCase

from azure.data.tables import (
    ResourceTypes,
    AccountSasPermissions,
    TableSasPermissions,
    CorsRule,
    RetentionPolicy,
    UpdateMode,
    AccessPolicy,
    TableAnalyticsLogging,
    Metrics,
    TableServiceClient,
    TableItem,
    generate_account_sas,
    ResourceTypes
)
from azure.core.credentials import AzureSasCredential
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    HeadersPolicy,
    ContentDecodePolicy,
)
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError
)

from _shared.testcase import TableTestCase
from preparers import TablesPreparer
# ------------------------------------------------------------------------------

TEST_TABLE_PREFIX = 'pytablesync'


# ------------------------------------------------------------------------------

class StorageTableTest(AzureTestCase, TableTestCase):

    # --Helpers-----------------------------------------------------------------
    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = ts.get_table_client(table_name)
        return table

    def _delete_table(self, ts, table):
        if table:
            try:
                ts.delete_table(table.table_name)
            except ResourceNotFoundError:
                pass

    def _delete_all_tables(self, ts):
        for table in ts.list_tables():
            try:
                ts.delete_table(table.name)
            except ResourceNotFoundError:
                pass

    # --Test cases for tables --------------------------------------------------

    @TablesPreparer()
    def test_create_properties(self, tables_storage_account_name, tables_primary_storage_account_key):
        # # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()
        # Act
        created = ts.create_table(table_name)

        # Assert
        assert created.table_name == table_name

        properties = ts.get_service_properties()
        ts.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
        # have to wait for return to service
        p = ts.get_service_properties()
        # have to wait for return to service
        ts.set_service_properties(minute_metrics= Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5)))

        ps = ts.get_service_properties()
        ts.delete_table(table_name)

    @TablesPreparer()
    def test_create_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table_name = self._get_table_reference()

        # Act
        created = ts.create_table(table_name)

        # Assert
        assert created.table_name == table_name
        ts.delete_table(table_name)

    @TablesPreparer()
    def test_create_table_fail_on_exist(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        # Act
        created = ts.create_table(table_name)
        with pytest.raises(ResourceExistsError):
            ts.create_table(table_name)

        name_filter = "TableName eq '{}'".format(table_name)
        existing = list(ts.query_tables(name_filter))

        # Assert
        assert created is not None
        ts.delete_table(table_name)

    @TablesPreparer()
    def test_query_tables_per_page(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table_name = "mytable"

        for i in range(5):
            ts.create_table(table_name + str(i))

        query_filter = "TableName eq 'mytable0' or TableName eq 'mytable1' or TableName eq 'mytable2'"
        table_count = 0
        page_count = 0
        for table_page in ts.query_tables(query_filter, results_per_page=2).by_page():

            temp_count = 0
            for table in table_page:
                temp_count += 1
            assert temp_count <= 2
            page_count += 1
            table_count += temp_count

        assert page_count == 2
        assert table_count == 3

        for i in range(5):
            ts.delete_table(table_name + str(i))

        if self.is_live:
            self.sleep(10) # wait for tables to be deleted before proceeding

    @TablesPreparer()
    def test_create_table_if_exists(self, tables_storage_account_name, tables_primary_storage_account_key):
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        t0 = ts.create_table(table_name)
        t1 = ts.create_table_if_not_exists(table_name)

        assert t0 is not None
        assert t1 is not None
        assert t0.table_name == t1.table_name
        ts.delete_table(table_name)

    @TablesPreparer()
    def test_create_table_if_exists_new_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        t = ts.create_table_if_not_exists(table_name)

        assert t is not None
        assert t.table_name ==  table_name
        ts.delete_table(table_name)

    @TablesPreparer()
    def test_query_tables(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        t = self._create_table(ts)

        # Act
        tables = list(ts.list_tables())

        # Assert
        for table_item in tables:
            assert isinstance(table_item,  TableItem)

        assert tables is not None
        assert len(tables) >=  1
        assert tables[0] is not None
        ts.delete_table(t.table_name)

        if self.is_live:
            self.sleep(10) # wait for tables to be deleted before proceeding

    @TablesPreparer()
    def test_query_tables_with_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        t = self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(t.table_name)
        tables = list(ts.query_tables(name_filter))

        for table_item in tables:
            assert isinstance(table_item,  TableItem)

        # Assert
        assert tables is not None
        assert len(tables) ==  1
        ts.delete_table(t.table_name)

        self._delete_all_tables(ts)

        if self.is_live:
            self.sleep(10) # wait for tables to be deleted before proceeding

    @TablesPreparer()
    def test_query_tables_with_num_results(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        prefix = 'listtable'
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_list = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_list)

        # Act
        small_page = []
        big_page = []
        for s in next(ts.list_tables(results_per_page=3).by_page()):
            small_page.append(s)
            assert s.name.startswith(prefix)
        for t in next(ts.list_tables().by_page()):
            big_page.append(t)
            assert t.name.startswith(prefix)

        # Assert
        assert len(small_page) ==  3
        assert len(big_page) >=  4

        self._delete_all_tables(ts)

        if self.is_live:
            self.sleep(10) # wait for tables to be deleted before proceeding

    @TablesPreparer()
    def test_query_tables_with_marker(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        prefix = 'listtable'
        table_names = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_names)

        # Act
        generator1 = ts.list_tables(results_per_page=2).by_page()
        next(generator1)
        generator2 = ts.list_tables(results_per_page=2).by_page(
            continuation_token=generator1.continuation_token)
        next(generator2)

        tables1 = generator1._current_page
        tables2 = generator2._current_page

        # Assert
        assert len(tables1) ==  2
        assert len(tables2) ==  2
        assert tables1 != tables2

        self._delete_all_tables(ts)

        if self.is_live:
            self.sleep(10) # wait for tables to be deleted before proceeding

    @TablesPreparer()
    def test_delete_table_with_existing_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = self._create_table(ts)

        # Act
        deleted = ts.delete_table(table_name=table.table_name)
        existing = list(ts.query_tables("TableName eq '{}'".format(table.table_name)))

        # Assert
        assert deleted is None
        assert len(existing) ==  0

    @TablesPreparer()
    def test_delete_table_with_non_existing_table_fail_not_exist(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        # Act
        with pytest.raises(HttpResponseError):
            ts.delete_table(table_name)

    @TablesPreparer()
    def test_get_table_acl(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = self._create_table(ts)
        try:
            # Act
            acl = table.get_table_access_policy()

            # Assert
            assert acl is not None
            assert len(acl) ==  0
        finally:
            ts.delete_table(table.table_name)

    @TablesPreparer()
    def test_set_table_acl_with_empty_signed_identifiers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = self._create_table(ts)
        try:
            # Act
            table.set_table_access_policy(signed_identifiers={})

            # Assert
            acl = table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  0
        finally:
            ts.delete_table(table.table_name)

    @TablesPreparer()
    def test_set_table_acl_with_empty_signed_identifier(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = self._create_table(ts)
        try:
            # Act
            table.set_table_access_policy(signed_identifiers={'empty': None})
            # Assert
            acl = table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  1
            assert acl['empty'] is not None
            assert acl['empty'].permission is None
            assert acl['empty'].expiry is None
            assert acl['empty'].start is None
        finally:
            ts.delete_table(table.table_name)

    @TablesPreparer()
    def test_set_table_acl_with_signed_identifiers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = self._create_table(ts)
        client = ts.get_table_client(table_name=table.table_name)

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(start=datetime.utcnow() - timedelta(minutes=5),
                                             expiry=datetime.utcnow() + timedelta(hours=1),
                                             permission='r')
        try:
            client.set_table_access_policy(signed_identifiers=identifiers)
            # Assert
            acl = client.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  1
            assert 'testid' in acl
        finally:
            ts.delete_table(table.table_name)

    @TablesPreparer()
    def test_set_table_acl_too_many_ids(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with pytest.raises(ValueError):
                table.set_table_access_policy(signed_identifiers=identifiers)
        finally:
            ts.delete_table(table.table_name)

    @pytest.mark.live_test_only
    @TablesPreparer()
    def test_account_sas(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = self._create_table(tsc)
        try:
            entity = {
                'PartitionKey': u'test',
                'RowKey': u'test1',
                'text': u'hello',
            }
            table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)

            entity['RowKey'] = u'test2'
            table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)

            token = generate_account_sas(
                tables_storage_account_name,
                tables_primary_storage_account_key,
                resource_types=ResourceTypes(object=True),
                permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            account_url = self.account_url(tables_storage_account_name, "table")

            service = self.create_client_from_credential(TableServiceClient, token, account_url=account_url)

            # Act

            sas_table = service.get_table_client(table.table_name)
            entities = list(sas_table.list_entities())

            # Assert
            assert len(entities) ==  2
            assert entities[0].text ==  u'hello'
            assert entities[1].text ==  u'hello'
        finally:
            self._delete_table(table=table, ts=tsc)


class TestTablesUnitTest(TableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"

    def test_unicode_create_table_unicode_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)

        table_name = u'啊齄丂狛狜'

        # Act
        with pytest.raises(ValueError) as excinfo:
            tsc.create_table(table_name)

            assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)

    def test_create_table_invalid_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            tsc.create_table(invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    def test_delete_table_invalid_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            tsc.delete_table(invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    def test_azurite_url(self):
        account_url = "https://127.0.0.1:10002/my_account"
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)

        assert tsc.account_name == "my_account"
        assert tsc.url == "https://127.0.0.1:10002/my_account"
        assert tsc.location_mode == "primary"
        assert tsc.credential.account_key == self.tables_primary_storage_account_key
        assert tsc.credential.account_name == "my_account"