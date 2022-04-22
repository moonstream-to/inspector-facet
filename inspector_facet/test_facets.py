import json
import os
import unittest

from . import facets

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestFacetsFromMoonwormCrawldata(unittest.TestCase):
    maxDiff = None

    def test_with_cu_lands_crawldata_until_27331689(self):
        crawldata_jsonl = os.path.join(FIXTURES_DIR, "cu-land-cuts.jsonl")
        expected_output_json = os.path.join(FIXTURES_DIR, "cu-land-facets.json")
        with open(expected_output_json, "r") as ifp:
            expected_output = json.load(ifp)

        events = facets.events_from_moonworm_crawldata(crawldata_jsonl)
        actual_output = facets.facets_from_events(events)

        self.assertDictEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
