from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from trabalho2.settings import Settings, get_settings


class SettingsTestCase(unittest.TestCase):
    def test_defaults_build_expected_jdbc_url(self) -> None:
        settings = Settings()
        self.assertEqual(settings.jdbc_url, "jdbc:postgresql://localhost:5432/trabalho2")
        self.assertEqual(settings.landing_bucket, "landing-zone")
        self.assertEqual(settings.bronze_bucket, "bronze")

    def test_environment_values_override_defaults_for_new_instance(self) -> None:
        with patch.dict(
            os.environ,
            {
                "POSTGRES_HOST": "db",
                "POSTGRES_PORT": "5433",
                "POSTGRES_DB": "customdb",
                "LANDING_BUCKET": "raw-zone",
                "BRONZE_BUCKET": "silver-zone",
            },
            clear=False,
        ):
            settings = get_settings()

        self.assertEqual(settings.jdbc_url, "jdbc:postgresql://db:5433/customdb")
        self.assertEqual(settings.landing_bucket, "raw-zone")
        self.assertEqual(settings.bronze_bucket, "silver-zone")


if __name__ == "__main__":
    unittest.main()
