"""Regression checks for the local catalog and defensive query renderer."""

from __future__ import annotations

import unittest

from osint_suite.catalog import CATEGORY_SOURCES, FIELD_DORK_PROFILES, generate_dorks, launch_url, toolkit_catalog
from osint_suite.validation import escape, validate_typed_target


class CatalogTests(unittest.TestCase):
    def test_catalog_generates_expected_coverage(self) -> None:
        dorks = generate_dorks("example.org", "domain")
        expected_categories = FIELD_DORK_PROFILES["domain"]
        self.assertEqual(len(CATEGORY_SOURCES), 19)
        self.assertEqual(len(dorks), 16 * len(expected_categories))
        self.assertEqual(len({dork.id for dork in dorks}), len(dorks))
        self.assertEqual({dork.category for dork in dorks}, set(expected_categories))
        self.assertTrue(all(dork.id.startswith("domain-") for dork in dorks))

    def test_every_category_is_reachable_from_some_field(self) -> None:
        """Every declared category must appear in at least one field profile."""
        referenced = {category for profile in FIELD_DORK_PROFILES.values() for category in profile}
        self.assertEqual(referenced, set(CATEGORY_SOURCES))

    def test_new_categories_generate_field_specific_dorks(self) -> None:
        cctv = generate_dorks("Hikvision DS-2CD2143", "cctv")
        records = generate_dorks("Ministry of Finance", "indian_records")
        self.assertIn("CCTV & Cameras", {dork.category for dork in cctv})
        self.assertIn("Indian Public Records", {dork.category for dork in records})
        self.assertTrue(all("Hikvision DS-2CD2143" in dork.query for dork in cctv))
        self.assertTrue(all("Ministry of Finance" in dork.query for dork in records))
        self.assertTrue(all("http" not in dork.query for dork in cctv))
        self.assertTrue(all(dork.id.startswith("cctv-") for dork in cctv))

    def test_catalog_is_target_specific(self) -> None:
        full_name_dorks = generate_dorks("Prajwal Sharma", "full_name")
        email_dorks = generate_dorks("abc@gmail.com", "email")
        self.assertEqual(len(full_name_dorks), 16 * len(FIELD_DORK_PROFILES["full_name"]))
        self.assertEqual(len(email_dorks), 16 * len(FIELD_DORK_PROFILES["email"]))
        self.assertTrue(all("Prajwal Sharma" in dork.query for dork in full_name_dorks))
        self.assertTrue(all("abc@gmail.com" in dork.query for dork in email_dorks))
        self.assertNotEqual({dork.category for dork in full_name_dorks}, {dork.category for dork in email_dorks})

    def test_queries_remain_public_search_strings(self) -> None:
        dorks = generate_dorks("example.org", "domain")
        self.assertTrue(all("http" not in dork.query for dork in dorks))
        domain_queries = [dork.query for dork in dorks if dork.category == "Domain"]
        self.assertIn("site:example.org", domain_queries)

    def test_launch_urls_are_encoded(self) -> None:
        url = launch_url("Google", 'site:example.org "annual report"')
        self.assertEqual(url, "https://www.google.com/search?q=site%3Aexample.org+%22annual+report%22")

    def test_toolkit_records_have_official_https_destinations(self) -> None:
        tools = toolkit_catalog()
        self.assertGreaterEqual(len(tools), 42)
        self.assertTrue(all(tool.homepage.startswith("https://") for tool in tools))

    def test_validation_and_html_escaping(self) -> None:
        self.assertEqual(validate_typed_target("domain", "example.org"), "example.org")
        self.assertEqual(escape('<script>alert("x")</script>'), "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;")
        with self.assertRaises(ValueError):
            validate_typed_target("email", "not-an-email")


if __name__ == "__main__":
    unittest.main()
