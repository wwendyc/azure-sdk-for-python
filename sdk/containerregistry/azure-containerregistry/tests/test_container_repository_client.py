# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import pytest

from azure.containerregistry import (
    DeleteRepositoryResult,
    ContentProperties,
    RegistryArtifactOrderBy,
    RegistryArtifactProperties,
    ArtifactTagProperties,
    TagOrderBy,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from testcase import ContainerRegistryTestClass
from constants import TO_BE_DELETED, DOES_NOT_EXIST, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRepositoryClient(ContainerRegistryTestClass):
    @acr_preparer()
    def test_delete_tag(self, containerregistry_endpoint, containerregistry_resource_group):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_repository_client(containerregistry_endpoint, repo)

        tag_props = client.get_tag_properties(tag)
        assert tag_props is not None

        client.delete_tag(tag)
        self.sleep(5)
        with pytest.raises(ResourceNotFoundError):
            client.get_tag_properties(tag)

    @acr_preparer()
    def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, "DOES_NOT_EXIST123")

        with pytest.raises(ResourceNotFoundError):
            client.delete_tag("DOESNOTEXIST123")

    @acr_preparer()
    def test_get_properties(self, containerregistry_endpoint):
        repo_client = self.create_repository_client(containerregistry_endpoint, HELLO_WORLD)

        properties = repo_client.get_properties()
        assert isinstance(properties.writeable_properties, ContentProperties)

    @acr_preparer()
    def test_get_tag(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        tag = client.get_tag_properties("latest")

        assert tag is not None
        assert isinstance(tag, ArtifactTagProperties)
        assert tag.repository == client.repository

    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        count = 0
        for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)
        results_per_page = 2

        pages = client.list_registry_artifacts(results_per_page=results_per_page)
        page_count = 0
        for page in pages.by_page():
            reg_count = 0
            for tag in page:
                reg_count += 1
            assert reg_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        for artifact in client.list_registry_artifacts(order_by=RegistryArtifactOrderBy.LAST_UPDATE_TIME_DESCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on < prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        for artifact in client.list_registry_artifacts(order_by=RegistryArtifactOrderBy.LAST_UPDATE_TIME_ASCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on > prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_get_registry_artifact_properties(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        properties = client.get_registry_artifact_properties("latest")

        assert isinstance(properties, RegistryArtifactProperties)
        assert isinstance(properties.created_on, datetime)
        assert isinstance(properties.last_updated_on, datetime)

    @acr_preparer()
    def test_list_tags(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        tags = client.list_tags()
        assert isinstance(tags, ItemPaged)
        count = 0
        for tag in tags:
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_tags_by_page(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        results_per_page = 2

        pages = client.list_tags(results_per_page=results_per_page)
        page_count = 0
        for page in pages.by_page():
            tag_count = 0
            for tag in page:
                tag_count += 1
            assert tag_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    def test_list_tags_descending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        for tag in client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_DESCENDING):
            if prev_last_updated_on:
                assert tag.last_updated_on < prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_tags_ascending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        for tag in client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_ASCENDING):
            if prev_last_updated_on:
                assert tag.last_updated_on > prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_set_tag_properties(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repository, tag_identifier)])

        client = self.create_repository_client(containerregistry_endpoint, repository)

        tag_props = client.get_tag_properties(tag_identifier)
        permissions = tag_props.writeable_properties

        received = client.set_tag_properties(
            tag_identifier,
            ContentProperties(
                can_delete=False,
                can_list=False,
                can_read=False,
                can_write=False,
            ),
        )

        assert not received.writeable_properties.can_write
        assert not received.writeable_properties.can_read
        assert not received.writeable_properties.can_list
        assert not received.writeable_properties.can_delete

        client.set_tag_properties(
            tag_identifier,
            ContentProperties(
                can_delete=True,
                can_list=True,
                can_read=True,
                can_write=True,
            ),
        )

    @acr_preparer()
    def test_set_tag_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.get_resource_name("repo"))

        with pytest.raises(ResourceNotFoundError):
            client.set_tag_properties(DOES_NOT_EXIST, ContentProperties(can_delete=False))

    @acr_preparer()
    def test_set_manifest_properties(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("reposetmani")
        tag_identifier = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repository, tag_identifier)])

        client = self.create_repository_client(containerregistry_endpoint, repository)

        for artifact in client.list_registry_artifacts():
            permissions = artifact.writeable_properties

            received_permissions = client.set_manifest_properties(
                artifact.digest,
                ContentProperties(
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                ),
            )

            assert not received_permissions.writeable_properties.can_delete
            assert not received_permissions.writeable_properties.can_read
            assert not received_permissions.writeable_properties.can_list
            assert not received_permissions.writeable_properties.can_write

            # Reset and delete
            client.set_manifest_properties(
                artifact.digest,
                ContentProperties(
                    can_delete=True,
                    can_list=True,
                    can_read=True,
                    can_write=True,
                ),
            )
            client.delete()
            break

    @acr_preparer()
    def test_set_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.get_resource_name("repo"))

        with pytest.raises(ResourceNotFoundError):
            client.set_manifest_properties("sha256:abcdef", ContentProperties(can_delete=False))

    @acr_preparer()
    def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_image(HELLO_WORLD, [TO_BE_DELETED])

        reg_client = self.create_registry_client(containerregistry_endpoint)
        existing_repos = list(reg_client.list_repositories())
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_repository_client(containerregistry_endpoint, TO_BE_DELETED)
        result = repo_client.delete()
        assert isinstance(result, DeleteRepositoryResult)
        assert result.deleted_manifests is not None
        assert result.deleted_tags is not None

        existing_repos = list(reg_client.list_repositories())
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    def test_delete_repository_doesnt_exist(self, containerregistry_endpoint):
        repo_client = self.create_repository_client(containerregistry_endpoint, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            repo_client.delete()

    @acr_preparer()
    def test_delete_registry_artifact(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("repo")
        self.import_image(HELLO_WORLD, [repository])

        repo_client = self.create_repository_client(containerregistry_endpoint, repository)

        count = 0
        for artifact in repo_client.list_registry_artifacts():
            if count == 0:
                repo_client.delete_registry_artifact(artifact.digest)
            count += 1
        assert count > 0

        artifacts = []
        for a in repo_client.list_registry_artifacts():
            artifacts.append(a)

        assert len(artifacts) > 0
        assert len(artifacts) == count - 1
