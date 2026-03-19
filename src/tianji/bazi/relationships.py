"""
刑冲合害 (Branch Relationships) analysis for BaZi.

This module analyzes interactions between earthly branches in a chart:
- 六合 (Six Harmonies): Two branches combine
- 三合 (Three Harmonies): Three branches form a strong element
- 六冲 (Six Conflicts): Two branches oppose each other
- 三刑 (Three Punishments): Two or three branches punish each other
- 六害 (Six Harms): Two branches harm each other
- 自刑 (Self-Punishment): Same branch duplicated
"""

from __future__ import annotations

from dataclasses import dataclass

from tianji.calendar.earthly_branches import (
    EarthlyBranch,
    SIX_HARMONIES,
    THREE_HARMONIES,
    SIX_CONFLICTS,
    THREE_PUNISHMENTS,
    SIX_HARMS,
    Element,
)


@dataclass
class BranchRelationship:
    """A relationship found between branches."""
    kind: str              # 六合, 三合, 六冲, 三刑, 六害, 自刑
    branches: list[str]    # Branch chars involved
    result_element: Element | None = None
    description: str = ""

    def __str__(self) -> str:
        branches_str = "".join(self.branches)
        if self.result_element:
            return f"{self.kind}({branches_str}→{self.result_element.value})"
        return f"{self.kind}({branches_str})"


@dataclass
class RelationshipsAnalysis:
    """Complete relationships analysis for a set of branches."""
    branches: list[str]  # All branch chars in the chart
    relationships: list[BranchRelationship]

    def has_kind(self, kind: str) -> bool:
        """Check if a specific relationship type exists."""
        return any(r.kind == kind for r in self.relationships)

    def display(self) -> None:
        """Print relationships analysis."""
        print("\n刑冲合害分析 (Branch Relationships)")
        print("─" * 40)
        if not self.relationships:
            print("  无明显刑冲合害关系")
        for r in self.relationships:
            print(f"  {r}")
        print("─" * 40)


def analyze_relationships(branches: list[EarthlyBranch]) -> RelationshipsAnalysis:
    """
    Analyze all branch relationships in a chart.

    Args:
        branches: List of earthly branches (typically 4 from chart)

    Returns:
        RelationshipsAnalysis with all found relationships
    """
    chars = [b.char for b in branches]
    relationships: list[BranchRelationship] = []

    # Check 六合 (Six Harmonies)
    for b1, b2, element in SIX_HARMONIES:
        if b1 in chars and b2 in chars:
            relationships.append(BranchRelationship(
                kind="六合",
                branches=[b1, b2],
                result_element=element,
                description=f"{b1}{b2}合{element.value}",
            ))

    # Check 三合 (Three Harmonies)
    for b1, b2, b3, element in THREE_HARMONIES:
        count = sum(1 for b in [b1, b2, b3] if b in chars)
        if count >= 2:
            found = [b for b in [b1, b2, b3] if b in chars]
            relationships.append(BranchRelationship(
                kind="三合" if count == 3 else "半三合",
                branches=found,
                result_element=element,
                description=f"{''.join(found)}{'三合' if count == 3 else '半合'}{element.value}局",
            ))

    # Check 六冲 (Six Conflicts)
    for b1, b2 in SIX_CONFLICTS:
        if b1 in chars and b2 in chars:
            relationships.append(BranchRelationship(
                kind="六冲",
                branches=[b1, b2],
                description=f"{b1}{b2}相冲",
            ))

    # Check 三刑 (Three Punishments)
    for punishment_group in THREE_PUNISHMENTS:
        if len(punishment_group) == 3:
            b1, b2, b3 = punishment_group
            found = [b for b in punishment_group if b in chars]
            if len(found) >= 2:
                relationships.append(BranchRelationship(
                    kind="三刑",
                    branches=found,
                    description=f"{''.join(found)}相刑",
                ))
        elif len(punishment_group) == 2:
            b1, b2 = punishment_group
            if b1 == b2:
                # Self-punishment (自刑): same branch appears twice
                if chars.count(b1) >= 2:
                    relationships.append(BranchRelationship(
                        kind="自刑",
                        branches=[b1, b2],
                        description=f"{b1}自刑",
                    ))
            elif b1 in chars and b2 in chars:
                relationships.append(BranchRelationship(
                    kind="相刑",
                    branches=[b1, b2],
                    description=f"{b1}{b2}相刑",
                ))

    # Check 六害 (Six Harms)
    for b1, b2 in SIX_HARMS:
        if b1 in chars and b2 in chars:
            relationships.append(BranchRelationship(
                kind="六害",
                branches=[b1, b2],
                description=f"{b1}{b2}相害",
            ))

    return RelationshipsAnalysis(branches=chars, relationships=relationships)


def relationships_from_chart(chart) -> RelationshipsAnalysis:
    """
    Analyze branch relationships from a BaZiChart.

    Args:
        chart: A BaZiChart instance

    Returns:
        RelationshipsAnalysis
    """
    return analyze_relationships(chart.all_branches)
