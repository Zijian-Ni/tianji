"""
五行分析 (Five Elements Analysis) for BaZi charts.

Counts and analyzes the distribution of the Five Elements (木火土金水)
across all stems and branches in a four-pillar chart.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from tianji.calendar.heavenly_stems import Element, HeavenlyStem
from tianji.calendar.earthly_branches import EarthlyBranch


# Element scores for branch hidden stems (main/middle/residual weights)
_HIDDEN_STEM_WEIGHTS = (1.0, 0.6, 0.4)


@dataclass
class FiveElementsAnalysis:
    """Result of Five Elements analysis for a BaZi chart."""

    # Raw counts (stems only)
    stem_counts: Counter = field(default_factory=Counter)

    # Weighted scores (including branch hidden stems)
    weighted_scores: dict[Element, float] = field(default_factory=dict)

    # Branch counts (primary element only)
    branch_counts: Counter = field(default_factory=Counter)

    def total_score(self, element: Element) -> float:
        """Get the total weighted score for an element."""
        return self.weighted_scores.get(element, 0.0)

    def strongest_element(self) -> Element:
        """Return the element with the highest weighted score."""
        return max(self.weighted_scores, key=lambda e: self.weighted_scores[e])

    def weakest_element(self) -> Element:
        """Return the element with the lowest weighted score."""
        return min(self.weighted_scores, key=lambda e: self.weighted_scores[e])

    def missing_elements(self) -> list[Element]:
        """Return elements with zero score."""
        return [e for e in Element if self.weighted_scores.get(e, 0) == 0]

    def summary(self) -> str:
        """Return a formatted summary string."""
        parts = []
        for e in Element:
            score = self.weighted_scores.get(e, 0)
            parts.append(f"{e.value}:{score:.1f}")
        return "  ".join(parts)

    def display(self) -> None:
        """Print the Five Elements analysis."""
        print("\n五行分析 (Five Elements Analysis)")
        print("─" * 40)
        for e in Element:
            score = self.weighted_scores.get(e, 0)
            bar = "█" * int(score * 2)
            print(f"  {e.value}: {score:4.1f}  {bar}")
        missing = self.missing_elements()
        if missing:
            print(f"  缺失 (Missing): {', '.join(e.value for e in missing)}")
        print("─" * 40)


def analyze_five_elements(
    stems: list[HeavenlyStem],
    branches: list[EarthlyBranch],
    include_hidden_stems: bool = True,
) -> FiveElementsAnalysis:
    """
    Analyze Five Elements distribution in a BaZi chart.

    Args:
        stems: List of 4 heavenly stems (year, month, day, hour)
        branches: List of 4 earthly branches
        include_hidden_stems: Whether to include branch hidden stems (藏干)

    Returns:
        FiveElementsAnalysis with counts and weighted scores
    """
    analysis = FiveElementsAnalysis()

    # Initialize all elements to 0
    for e in Element:
        analysis.weighted_scores[e] = 0.0

    # Count stem elements (weight = 1.0 each)
    for stem in stems:
        analysis.stem_counts[stem.element] += 1
        analysis.weighted_scores[stem.element] = (
            analysis.weighted_scores.get(stem.element, 0) + 1.0
        )

    # Count branch elements
    for branch in branches:
        analysis.branch_counts[branch.element] += 1

        if include_hidden_stems:
            hidden = branch.get_hidden_stems()
            for i, hs in enumerate(hidden):
                weight = _HIDDEN_STEM_WEIGHTS[i] if i < len(_HIDDEN_STEM_WEIGHTS) else 0.3
                analysis.weighted_scores[hs.element] = (
                    analysis.weighted_scores.get(hs.element, 0) + weight
                )
        else:
            # Just count branch's primary element at weight 0.5
            analysis.weighted_scores[branch.element] = (
                analysis.weighted_scores.get(branch.element, 0) + 0.5
            )

    return analysis


def elements_from_chart(chart) -> FiveElementsAnalysis:
    """
    Convenience function: analyze Five Elements from a BaZiChart.

    Args:
        chart: A BaZiChart instance

    Returns:
        FiveElementsAnalysis
    """
    return analyze_five_elements(
        stems=chart.all_stems,
        branches=chart.all_branches,
    )
