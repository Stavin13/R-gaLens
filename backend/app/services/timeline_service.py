from datetime import datetime
from collections import defaultdict
from app.utils.logger import logger

class TimelineBuilder:
    def build_timeline(self, events: list) -> dict:
        logger.info(f"Building timeline from {len(events)} events.")
        
        # 1. Filter and Parse Dates
        valid_events = []
        for e in events:
            if hasattr(e, 'normalized_date') and e.normalized_date:
                try:
                    dt = datetime.fromisoformat(e.normalized_date)
                    valid_events.append({
                        "id": e.id,
                        "title": e.title,
                        "description": e.description,
                        "date": dt,
                        "date_str": e.date_str,
                        "type": e.event_type,
                        "entities": e.entities,
                        "sentence": e.sentence
                    })
                except Exception as err:
                    logger.warning(f"Failed to parse date for event {e.id}: {err}")

        # 2. Sort Chronologically
        valid_events.sort(key=lambda x: x["date"])

        # 3. Group by Decade
        decades = defaultdict(list)
        for e in valid_events:
            decade = (e["date"].year // 10) * 10
            # Serializing date for JSON
            event_copy = e.copy()
            event_copy["date"] = event_copy["date"].isoformat()
            decades[decade].append(event_copy)

        # 4. Build Relationship Graph
        nodes, edges = self._build_graph(valid_events)

        # 5. Statistics
        stats = {
            "total_events": len(valid_events),
            "start_year": valid_events[0]["date"].year if valid_events else None,
            "end_year": valid_events[-1]["date"].year if valid_events else None,
            "event_types": list(set(e["type"] for e in valid_events))
        }

        return {
            "events": [dict(e, date=e["date"].isoformat()) for e in valid_events],
            "decades": dict(decades),
            "graph": {"nodes": nodes, "edges": edges},
            "statistics": stats
        }

    def _build_graph(self, events: list) -> tuple:
        nodes = []
        edges = []
        entity_to_events = defaultdict(list)

        for e in events:
            node_id = f"event_{e['id']}"
            nodes.append({
                "id": node_id,
                "label": e["title"],
                "type": "event"
            })
            
            # Link via entities
            if e["entities"]:
                for ent in e["entities"]:
                    ent_name = ent.get("text")
                    if ent_name:
                        entity_to_events[ent_name].append(node_id)

        # Create edges between events that share entities
        for ent_name, event_ids in entity_to_events.items():
            if len(event_ids) > 1:
                for i in range(len(event_ids)):
                    for j in range(i + 1, len(event_ids)):
                        edges.append({
                            "source": event_ids[i],
                            "target": event_ids[j],
                            "label": f"Shared entity: {ent_name}"
                        })

        return nodes, edges

timeline_builder = TimelineBuilder()
