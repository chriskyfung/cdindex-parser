"""Tests for cdindex_parser.tree — path reconstruction."""

from cdindex_parser.tree import build_paths


class TestBuildPaths:
    """Tests for build_paths — stack-based path reconstruction."""

    def test_flat_entries(self):
        entries = [(0, "A"), (0, "B"), (0, "C")]
        paths = list(build_paths(entries))
        assert paths == ["A", "B", "C"]

    def test_nested_entries(self):
        entries = [
            (0, "Root"),
            (1, "Sub"),
            (2, "Deep"),
        ]
        paths = list(build_paths(entries))
        assert paths == ["Root", "Root/Sub", "Root/Sub/Deep"]

    def test_sibling_depth_reset(self):
        entries = [
            (0, "Root"),
            (1, "Sub1"),
            (2, "Deep1"),
            (1, "Sub2"),
            (2, "Deep2"),
        ]
        paths = list(build_paths(entries))
        assert paths == [
            "Root",
            "Root/Sub1",
            "Root/Sub1/Deep1",
            "Root/Sub2",
            "Root/Sub2/Deep2",
        ]

    def test_depth_5_levels(self):
        entries = [
            (0, "L0"),
            (1, "L1"),
            (2, "L2"),
            (3, "L3"),
            (4, "L4"),
        ]
        paths = list(build_paths(entries))
        assert paths[-1] == "L0/L1/L2/L3/L4"

    def test_empty_input(self):
        paths = list(build_paths(iter([])))
        assert paths == []

    def test_single_entry(self):
        paths = list(build_paths([(0, "Only")]))
        assert paths == ["Only"]

    def test_depth_skips_back(self):
        """Going from depth 3 back to depth 0 should pop all."""
        entries = [
            (0, "A"),
            (1, "B"),
            (2, "C"),
            (0, "D"),
        ]
        paths = list(build_paths(entries))
        assert paths == ["A", "A/B", "A/B/C", "D"]
