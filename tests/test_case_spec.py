import unittest
from dataclasses import replace

from datamystery.cases.margin_mirage import build_spec


class CaseSpecTests(unittest.TestCase):
    def test_sample_spec_is_valid(self) -> None:
        build_spec().validate()

    def test_narrative_and_generator_cannot_disagree_on_incident_date(self) -> None:
        spec = build_spec()
        invalid = replace(spec, incident_date="2026-04-01")
        with self.assertRaisesRegex(ValueError, "incident dates disagree"):
            invalid.validate()


if __name__ == "__main__":
    unittest.main()
