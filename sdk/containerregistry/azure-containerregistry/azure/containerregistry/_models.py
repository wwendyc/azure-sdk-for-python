# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from typing import TYPE_CHECKING, Dict, Any
from ._generated.models import ContentProperties as GeneratedContentProperties

if TYPE_CHECKING:
    from ._generated.models import ManifestAttributesBase
    from ._generated.models import RepositoryProperties as GeneratedRepositoryProperties
    from ._generated.models import ArtifactTagProperties as GeneratedTagProperties


class ContentProperties(object):
    """Permissions of an artifact or tag

    :ivar bool can_delete: Ability to delete an artifact or tag
    :ivar bool can_list: Ability to list an artifact or tag
    :ivar bool can_read: Ability to read an artifact or tag
    :ivar bool can_write: Ability to write an artifact or tag
    """

    def __init__(self, **kwargs):
        """Create ContentPermissions for an artifact, tag, or manifest

        :keyword bool can_delete: Delete operation status for the object
        :keyword bool can_list: List operation status for the object
        :keyword bool can_read: Read operation status for the object
        :keyword bool can_write: Write operation status for the object
        """
        self.can_delete = kwargs.get("can_delete")
        self.can_list = kwargs.get("can_list")
        self.can_read = kwargs.get("can_read")
        self.can_write = kwargs.get("can_write")

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedContentProperties) -> ContentProperties
        return cls(
            can_delete=generated.can_delete,
            can_list=generated.can_list,
            can_read=generated.can_read,
            can_write=generated.can_write,
        )

    def _to_generated(self):
        # type: () -> GeneratedContentProperties
        return GeneratedContentProperties(
            can_delete=self.can_delete,
            can_list=self.can_list,
            can_read=self.can_read,
            can_write=self.can_write,
        )


class DeleteRepositoryResult(object):
    """Represents the digests and tags deleted when a repository is deleted

    :ivar List[str] deleted_manifests: Registry artifact digests that were deleted
    :ivar List[str] deleted_tags: Tags that were deleted
    """

    def __init__(self, **kwargs):
        self.deleted_manifests = kwargs.get("deleted_manifests", None)
        self.deleted_tags = kwargs.get("deleted_tags", None)

    @classmethod
    def _from_generated(cls, gen):
        return cls(
            deleted_tags=gen.deleted_tags,
            deleted_manifests=gen.deleted_manifests,
        )


class RegistryArtifactProperties(object):
    """Represents properties of a registry artifact

    :ivar str cpu_architecture: CPU Architecture of an artifact
    :ivar created_on: Time and date an artifact was created
    :vartype created_on: :class:`~datetime.datetime`
    :ivar str digest: Digest for the artifact
    :ivar last_updated_on: Time and date an artifact was last updated
    :vartype last_updated_on: :class:`~datetime.datetime`
    :ivar str operating_system: Operating system for the artifact
    :ivar List[str] references: References for the artifact
    :ivar str size: Size of the artifact
    :ivar List[str] tags: Tags associated with a registry artifact
    :ivar writeable_properties: Permissions for an artifact
    :vartype writeable_properties: :class:`~azure.containerregistry.ContentProperties`
    """

    def __init__(self, **kwargs):
        self.cpu_architecture = kwargs.get("cpu_architecture", None)
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.operating_system = kwargs.get("operating_system", None)
        self.references = kwargs.get("references", None)
        self.size = kwargs.get("size", None)
        self.tags = kwargs.get("tags", None)
        self.writeable_properties = kwargs.get("content_permissions", None)
        if self.writeable_properties:
            self.writeable_properties = ContentProperties._from_generated(self.writeable_properties)

    @classmethod
    def _from_generated(cls, generated):
        # type: (ManifestAttributesBase) -> RegistryArtifactProperties
        return cls(
            cpu_architecture=generated.architecture,
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            operating_system=generated.operating_system,
            size=generated.size,
            tags=generated.tags,
            content_permissions=generated.writeable_properties,
        )


class RepositoryProperties(object):
    """Model for storing properties of a single repository

    :ivar writeable_properties: Read/Write/List/Delete permissions for the repository
    :vartype writeable_properties: :class:`~azure.containerregistry.ContentProperties`
    :ivar created_on: Time the repository was created
    :vartype created_on: :class:`datetime.datetime`
    :ivar last_updated_on: Time the repository was last updated
    :vartype last_updated_on: :class:`datetime.datetime`
    :ivar int manifest_count: Number of manifest in the repository
    :ivar str name: Name of the repository
    :ivar str registry: Registry the repository belongs to
    :ivar int tag_count: Number of tags associated with the repository
    """

    def __init__(self, **kwargs):
        self.writeable_properties = kwargs.get("content_permissions", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.manifest_count = kwargs.get("manifest_count", None)
        self.name = kwargs.get("name", None)
        self.registry = kwargs.get("registry", None)
        self.tag_count = kwargs.get("tag_count", None)
        if self.writeable_properties:
            self.writeable_properties = ContentProperties._from_generated(self.writeable_properties)

    @classmethod
    def _from_generated(cls, generated):
        # type: (GeneratedRepositoryProperties) -> RepositoryProperties
        return cls(
            created_on=generated.created_on,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            manifest_count=generated.manifest_count,
            tag_count=generated.tag_count,
            content_permissions=generated.writeable_properties,
            registry=generated.additional_properties.get("registry", None),
        )


class RegistryArtifactOrderBy(str, Enum):
    """Enum for ordering registry artifacts"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class TagOrderBy(str, Enum):
    """Enum for ordering tags"""

    LAST_UPDATE_TIME_DESCENDING = "timedesc"
    LAST_UPDATE_TIME_ASCENDING = "timeasc"


class ArtifactTagProperties(object):
    """Model for storing properties of a single tag

    :ivar writeable_properties: Read/Write/List/Delete permissions for the tag
    :vartype writeable_properties: :class:`~azure.containerregistry.ContentProperties`
    :ivar created_on: Time the tag was created
    :vartype created_on: :class:`datetime.datetime`
    :ivar str digest: Digest for the tag
    :ivar last_updated_on: Time the tag was last updated
    :vartype last_updated_on: :class:`datetime.datetime`
    :ivar str name: Name of the image the tag corresponds to
    :ivar str repository: Repository the tag belongs to
    """

    def __init__(self, **kwargs):
        self.writeable_properties = kwargs.get("writeable_properties", None)
        self.created_on = kwargs.get("created_on", None)
        self.digest = kwargs.get("digest", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.name = kwargs.get("name", None)
        self.repository = kwargs.get("repository", None)
        if self.writeable_properties:
            self.writeable_properties = ContentProperties._from_generated(self.writeable_properties)

    @classmethod
    def _from_generated(cls, generated, **kwargs):
        # type: (GeneratedTagProperties, Dict[str, Any]) -> ArtifactTagProperties
        return cls(
            created_on=generated.created_on,
            digest=generated.digest,
            last_updated_on=generated.last_updated_on,
            name=generated.name,
            writeable_properties=generated.writeable_properties,
            repository=kwargs.get("repository", None),
        )
