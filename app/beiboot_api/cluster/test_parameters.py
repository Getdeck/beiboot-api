from decimal import Decimal
from unittest import TestCase

from cluster.types import Parameters, ServerResourcesRequestsCpu
from config.types import Config


class MinMaxDecimalValidator(TestCase):
    def test_valid(self):
        cluster_config = Config()
        parameters = Parameters(
            cluster_config=cluster_config,
            **{
                "SERVER_RESOURCES_REQUESTS_CPU": ServerResourcesRequestsCpu(value="1"),
            },
        )
        self.assertAlmostEqual(parameters.server_resources_requests_cpu.value, Decimal(1))

    def test_invalid_min(self):
        cluster_config = Config(
            server_resources_requests_cpu_min="0.2",
            server_resources_requests_cpu_max="0.8",
        )

        with self.assertRaises(ValueError):
            _ = Parameters(
                cluster_config=cluster_config,
                **{
                    "SERVER_RESOURCES_REQUESTS_CPU": ServerResourcesRequestsCpu(value="0.1"),
                },
            )

    def test_invalid_max(self):
        cluster_config = Config(
            server_resources_requests_cpu_min="0.2",
            server_resources_requests_cpu_max="0.8",
        )

        with self.assertRaises(ValueError):
            _ = Parameters(
                cluster_config=cluster_config,
                **{
                    "SERVER_RESOURCES_REQUESTS_CPU": ServerResourcesRequestsCpu(value="0.9"),
                },
            )
