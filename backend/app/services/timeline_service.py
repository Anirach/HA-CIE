"""
Timeline Service for assessment history visualization.
Provides time-series data for animated graph transitions.
"""

from datetime import date, timedelta
from typing import Optional
import random

from app.services.standards_service import StandardsService


class TimelineService:
    """Service for managing timeline data and assessment snapshots."""
    
    def __init__(self):
        self.standards_service = StandardsService()
        self._snapshots: list[dict] = []
        self._generate_sample_snapshots()
    
    def _generate_sample_snapshots(self):
        """Generate sample assessment snapshots over time."""
        chapters = self.standards_service.get_all_chapters()
        parts = self.standards_service.get_parts()
        
        # Create a mapping from chapter id to part number
        chapter_to_part = {}
        for part in parts:
            for chapter in part.chapters:
                chapter_to_part[chapter.id] = part.number
        
        # Generate 6 quarterly snapshots (1.5 years of data)
        base_date = date.today() - timedelta(days=540)  # Start 18 months ago
        
        # Initial scores (lower)
        initial_scores = {}
        for chapter in chapters:
            # Start with scores between 1.5 and 3.0
            initial_scores[chapter.id] = round(random.uniform(1.5, 3.0), 2)
        
        for i in range(6):
            snapshot_date = base_date + timedelta(days=90 * i)
            
            # Build chapter scores with gradual improvement
            chapter_scores = {}
            changes = []
            
            for chapter in chapters:
                chapter_id = chapter.id
                base_score = initial_scores[chapter_id]
                
                # Progressive improvement with some variation
                improvement = i * 0.35 * random.uniform(0.7, 1.3)
                noise = random.uniform(-0.15, 0.15)
                score = min(5.0, base_score + improvement + noise)
                score = round(score, 2)
                
                # Calculate change from previous snapshot
                if i > 0:
                    prev_score = self._snapshots[-1]["scores"].get(chapter_id, base_score)
                    change = round(score - prev_score, 2)
                    if abs(change) > 0.1:
                        changes.append({
                            "chapter_id": chapter_id,
                            "chapter_name": chapter.name,
                            "previous_score": prev_score,
                            "new_score": score,
                            "change": change,
                            "part": chapter_to_part.get(chapter_id, "I"),
                        })
                
                chapter_scores[chapter_id] = score
            
            # Calculate overall metrics
            scores_list = list(chapter_scores.values())
            overall_score = round(sum(scores_list) / len(scores_list), 2)
            
            # Determine accreditation level
            min_score = min(scores_list)
            if overall_score >= 4.0 and min_score >= 3.0:
                level = "Advanced HA"
            elif overall_score >= 3.5 and min_score >= 2.5:
                level = "HA"
            elif overall_score >= 3.0 and min_score >= 2.0:
                level = "Pre-HA"
            else:
                level = "Not Accredited"
            
            snapshot = {
                "id": f"snapshot-{i+1}",
                "index": i,
                "date": snapshot_date.isoformat(),
                "label": snapshot_date.strftime("%b %Y"),
                "overall_score": overall_score,
                "accreditation_level": level,
                "scores": chapter_scores,
                "changes": sorted(changes, key=lambda x: abs(x["change"]), reverse=True),
                "summary": {
                    "improved": len([c for c in changes if c["change"] > 0]),
                    "declined": len([c for c in changes if c["change"] < 0]),
                    "unchanged": len(chapters) - len(changes),
                }
            }
            
            self._snapshots.append(snapshot)
    
    def get_all_snapshots(self) -> list[dict]:
        """Get all available timeline snapshots."""
        return [
            {
                "id": s["id"],
                "index": s["index"],
                "date": s["date"],
                "label": s["label"],
                "overall_score": s["overall_score"],
                "accreditation_level": s["accreditation_level"],
                "summary": s["summary"],
            }
            for s in self._snapshots
        ]
    
    def get_snapshot(self, index: int) -> Optional[dict]:
        """Get a specific snapshot by index."""
        if 0 <= index < len(self._snapshots):
            return self._snapshots[index]
        return None
    
    def get_snapshot_comparison(self, from_index: int, to_index: int) -> dict:
        """Compare two snapshots and return detailed changes."""
        from_snapshot = self.get_snapshot(from_index)
        to_snapshot = self.get_snapshot(to_index)
        
        if not from_snapshot or not to_snapshot:
            return {"error": "Invalid snapshot indices"}
        
        chapters = self.standards_service.get_all_chapters()
        parts = self.standards_service.get_parts()
        
        # Create a mapping from chapter id to part number
        chapter_to_part = {}
        for part in parts:
            for chapter in part.chapters:
                chapter_to_part[chapter.id] = part.number
        
        changes = []
        
        for chapter in chapters:
            chapter_id = chapter.id
            from_score = from_snapshot["scores"].get(chapter_id, 0)
            to_score = to_snapshot["scores"].get(chapter_id, 0)
            change = round(to_score - from_score, 2)
            
            changes.append({
                "chapter_id": chapter_id,
                "chapter_name": chapter.name,
                "part": chapter_to_part.get(chapter_id, "I"),
                "from_score": from_score,
                "to_score": to_score,
                "change": change,
                "change_percent": round((change / from_score * 100) if from_score > 0 else 0, 1),
            })
        
        # Sort by absolute change
        changes = sorted(changes, key=lambda x: abs(x["change"]), reverse=True)
        
        return {
            "from_snapshot": {
                "id": from_snapshot["id"],
                "date": from_snapshot["date"],
                "label": from_snapshot["label"],
                "overall_score": from_snapshot["overall_score"],
            },
            "to_snapshot": {
                "id": to_snapshot["id"],
                "date": to_snapshot["date"],
                "label": to_snapshot["label"],
                "overall_score": to_snapshot["overall_score"],
            },
            "overall_change": round(to_snapshot["overall_score"] - from_snapshot["overall_score"], 2),
            "changes": changes,
            "summary": {
                "improved": len([c for c in changes if c["change"] > 0.1]),
                "declined": len([c for c in changes if c["change"] < -0.1]),
                "unchanged": len([c for c in changes if abs(c["change"]) <= 0.1]),
            }
        }
    
    def get_chapter_history(self, chapter_id: str) -> dict:
        """Get score history for a specific chapter across all snapshots."""
        history = []
        for snapshot in self._snapshots:
            if chapter_id in snapshot["scores"]:
                history.append({
                    "date": snapshot["date"],
                    "label": snapshot["label"],
                    "score": snapshot["scores"][chapter_id],
                    "overall": snapshot["overall_score"],
                })
        
        # Calculate trend
        if len(history) >= 2:
            first_score = history[0]["score"]
            last_score = history[-1]["score"]
            total_change = round(last_score - first_score, 2)
            trend = "improving" if total_change > 0.2 else "declining" if total_change < -0.2 else "stable"
        else:
            total_change = 0
            trend = "stable"
        
        chapter = next(
            (c for c in self.standards_service.get_all_chapters() if c.id == chapter_id),
            None
        )
        
        # Get part number for the chapter
        parts = self.standards_service.get_parts()
        chapter_part = "Unknown"
        for part in parts:
            for ch in part.chapters:
                if ch.id == chapter_id:
                    chapter_part = part.number
                    break
        
        return {
            "chapter_id": chapter_id,
            "chapter_name": chapter.name if chapter else "Unknown",
            "part": chapter_part,
            "history": history,
            "trend": trend,
            "total_change": total_change,
        }


# Global instance
_timeline_service: Optional[TimelineService] = None


def get_timeline_service() -> TimelineService:
    """Get or create the timeline service instance."""
    global _timeline_service
    if _timeline_service is None:
        _timeline_service = TimelineService()
    return _timeline_service

