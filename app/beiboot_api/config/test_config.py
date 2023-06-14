from datetime import timedelta
from decimal import Decimal
from unittest import TestCase

from config.types import Config


class K8sVersionsValidator(TestCase):
    def test_list(self):
        cc = Config(k8s_versions="1.18.0,1.19.0,1.20.0")
        self.assertListEqual(cc.k8s_versions, ["1.18.0", "1.19.0", "1.20.0"])

    def test_single_value(self):
        cc = Config(k8s_versions="1.20.0")
        self.assertListEqual(cc.k8s_versions, ["1.20.0"])

    def test_empty(self):
        cc = Config(k8s_versions="")
        self.assertIsNone(cc.k8s_versions)

    def test_none(self):
        cc = Config(k8s_versions=None)
        self.assertIsNone(cc.k8s_versions)


class NodeCountMinValidator(TestCase):
    def test_valid(self):
        cc = Config(node_count_min=2)
        self.assertEquals(cc.node_count_min, 2)

    def test_invalid(self):
        cc = Config(node_count_min=0)
        self.assertEquals(cc.node_count_min, 1)


class TimedeltaValidator(TestCase):
    def test_valid(self):
        cc = Config(lifetime_limit="5m")
        self.assertEqual(cc.lifetime_limit, timedelta(minutes=5))

    def test_valid_timedelta(self):
        cc = Config(lifetime_limit=timedelta(minutes=5))
        self.assertEqual(cc.lifetime_limit, timedelta(minutes=5))

    def test_invalid(self):
        self.assertRaises(ValueError, Config, lifetime_limit="bla")


class ComputeValidator(TestCase):
    def test_valid(self):
        cc = Config(server_resources_requests_cpu_min="1")
        self.assertEqual(cc.server_resources_requests_cpu_min, Decimal(1))

    def test_valid_m(self):
        cc = Config(server_resources_requests_cpu_min="1m")
        self.assertAlmostEqual(cc.server_resources_requests_cpu_min, Decimal(0.001))

    def test_invalid_memory(self):
        self.assertRaises(ValueError, Config, server_resources_requests_cpu_min="1K")

    def test_invalid_format(self):
        cc = Config(server_resources_requests_cpu_min="a1")
        self.assertIsNone(cc.server_resources_requests_cpu_min)


class MemoryValidator(TestCase):
    def test_valid_k(self):
        cc = Config(server_resources_requests_memory_min="1k")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1000))

    def test_valid_K(self):
        cc = Config(server_resources_requests_memory_min="1K")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1000))

    def test_valid_M(self):
        cc = Config(server_resources_requests_memory_min="1M")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1000000))

    def test_valid_G(self):
        cc = Config(server_resources_requests_memory_min="1G")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1000000000))

    def test_valid_Ki(self):
        cc = Config(server_resources_requests_memory_min="1Ki")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1024))

    def test_valid_Mi(self):
        cc = Config(server_resources_requests_memory_min="1Mi")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1048576))

    def test_valid_Gi(self):
        cc = Config(server_resources_requests_memory_min="1Gi")
        self.assertEqual(cc.server_resources_requests_memory_min, Decimal(1073741824))

    def test_invalid(self):
        self.assertRaises(ValueError, Config, server_resources_requests_memory_min="bla")

    def test_invalid_compute(self):
        self.assertRaises(ValueError, Config, server_resources_requests_memory_min="0.5")

    def test_invalid_format(self):
        cc = Config(server_resources_requests_memory_min="a1K")
        self.assertIsNone(cc.server_resources_requests_memory_min)
