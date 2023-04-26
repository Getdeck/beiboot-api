from beiboot_api.cluster_config.types import ClusterConfig


class TestK8sVersions:
    def test_list(self):
        cc = ClusterConfig(k8s_versions="1.18.0,1.19.0,1.20.0")
        assert cc.k8s_versions == ["1.18.0", "1.19.0", "1.20.0"]

    def test_single_value(self):
        cc = ClusterConfig(k8s_versions="1.20.0")
        assert cc.k8s_versions == ["1.20.0"]

    def test_empty(self):
        cc = ClusterConfig(k8s_versions="")
        assert cc.k8s_versions == None  # noqa: E711

    def test_none(self):
        cc = ClusterConfig(k8s_versions=None)
        assert cc.k8s_versions == None  # noqa: E711


class TestNodeCountMin:
    def test_valid(self):
        cc = ClusterConfig(node_count_min=2)
        assert cc.node_count_min == 2

    def test_invalid(self):
        cc = ClusterConfig(node_count_min=0)
        assert cc.node_count_min == 1
