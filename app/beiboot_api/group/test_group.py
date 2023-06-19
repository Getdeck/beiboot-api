from unittest import TestCase

from group.service import GroupService
from settings import get_settings


class GroupServiceTest(TestCase):
    def test_list(self):
        x_forwarded_groups = "api-group-developer,api-group-free"
        settings = get_settings()

        group_service = GroupService(settings=settings)
        group_selected = group_service.select(x_forwarded_groups=x_forwarded_groups)

        self.assertEqual(group_selected, "developer")

    def test_list_group_order(self):
        x_forwarded_groups = "api-group-free"
        settings = get_settings()

        group_service = GroupService(settings=settings)
        group_selected = group_service.select(x_forwarded_groups=x_forwarded_groups)

        self.assertEqual(group_selected, "free")

    def test_list_empty(self):
        x_forwarded_groups = ""
        settings = get_settings()

        group_service = GroupService(settings=settings)
        group_selected = group_service.select(x_forwarded_groups=x_forwarded_groups)

        self.assertEqual(group_selected, "default")

    def test_list_none(self):
        x_forwarded_groups = None
        settings = get_settings()

        group_service = GroupService(settings=settings)
        group_selected = group_service.select(x_forwarded_groups=x_forwarded_groups)

        self.assertEqual(group_selected, "default")

    def test_list_invalid(self):
        x_forwarded_groups = "api-group-invalid"
        settings = get_settings()

        group_service = GroupService(settings=settings)
        group_selected = group_service.select(x_forwarded_groups=x_forwarded_groups)

        self.assertEqual(group_selected, "default")
