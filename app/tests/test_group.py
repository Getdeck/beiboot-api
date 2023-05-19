from beiboot_api.group import group_filter_and_selection


class TestGroup:
    def test_list(self):
        x_forwarded_groups = "beiboot-api-developer,beiboot-api-free"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert groups_filtered == ["developer", "free"]
        assert group_selected == "developer"

    def test_list_group_order(self):
        x_forwarded_groups = "beiboot-api-free"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert groups_filtered == ["free"]
        assert group_selected == "free"

    def test_list_empty(self):
        x_forwarded_groups = ""
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert groups_filtered == []
        assert group_selected == "default"

    def test_list_none(self):
        x_forwarded_groups = None
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert groups_filtered == []
        assert group_selected == "default"

    def test_list_invalid(self):
        x_forwarded_groups = "beiboot-api-invalid"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert groups_filtered == []
        assert group_selected == "default"
