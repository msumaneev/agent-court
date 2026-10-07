"""
Docket Deduplication Filter.
Compresses serial bursts and repetitive triggers into unified DocketItems with repeat_count.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from agent_court.core.models import DocketItem, IncidentType


class DocketFilter:
    """
    Collapses adjacent / repetitive anomaly events within a session.
    e.g. 20 consecutive command exit errors -> 1 Case with repeat_count=20.
    """

    def filter_dockets(self, items: List[DocketItem]) -> List[DocketItem]:
        if not items:
            return []

        deduped: List[DocketItem] = []
        # Grouping tracker: key -> index in deduped
        tracker: Dict[Tuple[str, IncidentType, str], int] = {}

        for item in items:
            # Normalize trigger signature: strip step numbers and specific variable values
            marker_prefix = item.trigger_marker[:60]
            key = (item.session_id, item.incident_type, marker_prefix)

            if key in tracker:
                idx = tracker[key]
                existing = deduped[idx]
                existing.repeat_count += 1
                # If existing had lower severity and current has higher, upgrade
                # Keep latest context or highest step
                if item.incident_step_index > existing.incident_step_index:
                    existing.incident_step_index = item.incident_step_index
            else:
                tracker[key] = len(deduped)
                deduped.append(item)

        return deduped
