from copy import deepcopy
from typing import Any, cast

from quantum_folk_lab.build_week import run_guided_exact
from scripts.verify_build_week_release import payloads_match_for_freshness


def test_python_patch_version_does_not_make_example_stale() -> None:
    saved = cast(dict[str, Any], run_guided_exact().to_dict())
    current = deepcopy(saved)
    saved["software_provenance"]["python"] = "3.13.5"
    current["software_provenance"]["python"] = "3.12.13"

    assert payloads_match_for_freshness(saved, current)
    assert saved["software_provenance"]["python"] == "3.13.5"
    assert current["software_provenance"]["python"] == "3.12.13"


def test_scientific_result_difference_remains_stale() -> None:
    saved = cast(dict[str, Any], run_guided_exact().to_dict())
    current = deepcopy(saved)
    current["exact_result"]["minimum_energy"] = 99.0

    assert not payloads_match_for_freshness(saved, current)
