from group.helper import group_filter_and_selection


class TestGroup:
    def test_list(self):
        x_forwarded_groups = "getdeck-api-developer,getdeck-api-free"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert set(groups_filtered) == set(["developer", "free"])
        assert group_selected == "developer"

    def test_list_group_order(self):
        x_forwarded_groups = "getdeck-api-free"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert set(groups_filtered) == set(["free"])
        assert group_selected == "free"

    def test_list_empty(self):
        x_forwarded_groups = ""
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert set(groups_filtered) == set([])
        assert group_selected == "default"

    def test_list_none(self):
        x_forwarded_groups = None
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert set(groups_filtered) == set([])
        assert group_selected == "default"

    def test_list_invalid(self):
        x_forwarded_groups = "getdeck-api-invalid"
        groups_filtered, group_selected = group_filter_and_selection(x_forwarded_groups=x_forwarded_groups)

        assert set(groups_filtered) == set([])
        assert group_selected == "default"
