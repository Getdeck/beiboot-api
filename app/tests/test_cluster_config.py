from beiboot_api.config.types import Config


class TestK8sVersions:
    def test_list(self):
        cc = Config(k8s_versions="1.18.0,1.19.0,1.20.0")
        assert cc.k8s_versions == ["1.18.0", "1.19.0", "1.20.0"]

    def test_single_value(self):
        cc = Config(k8s_versions="1.20.0")
        assert cc.k8s_versions == ["1.20.0"]

    def test_empty(self):
        cc = Config(k8s_versions="")
        assert cc.k8s_versions == None  # noqa: E711

    def test_none(self):
        cc = Config(k8s_versions=None)
        assert cc.k8s_versions == None  # noqa: E711


class TestNodeCountMin:
    def test_valid(self):
        cc = Config(node_count_min=2)
        assert cc.node_count_min == 2

    def test_invalid(self):
        cc = Config(node_count_min=0)
        assert cc.node_count_min == 1
