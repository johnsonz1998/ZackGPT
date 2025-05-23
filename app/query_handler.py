from memory_web import load_all_memory

def handle_memory_query_request(tags: list = None, agent: str = None) -> list:
    """
    Returns a filtered list of memory entries based on tag and/or agent.
    """
    all_memory = load_all_memory(agent=agent)
    results = []

    for category, entries in all_memory.items():
        for entry in entries:
            if tags:
                if not any(tag in entry.get("tags", []) for tag in tags):
                    continue
            results.append({
                "category": category,
                "text": entry["text"],
                "tags": entry.get("tags", []),
                "agents": entry.get("agents", []),
                "importance": entry.get("importance", "medium"),
                "created": entry.get("created"),
            })

    return results
