"""FAISS-backed Vector Memory for attack history and pattern recall.

This module gives the AI agents "experience" — the ability to recognize when
the same attacker (or a similar attack pattern) has been seen before.

How it works:
    1. Every processed incident gets embedded (raw_log + reasoning) and stored in FAISS.
    2. Before analyzing a new log, we query FAISS for the top-k most similar past incidents.
    3. If matches are found, they get injected into the LLM prompt as "Historical Context."
    4. This enables the AI to detect multi-stage attacks across time.

Technical Details:
    - Embeddings: sentence-transformers 'all-MiniLM-L6-v2' (384 dimensions, fast CPU inference)
    - Index: FAISS IndexFlatIP (inner product, cosine similarity after normalization)
    - Persistence: Index saved to disk at data/vector_index/
    - Metadata: Stored in a parallel JSON file alongside the FAISS index

Production Notes:
    - For >1M incidents, switch to IndexIVFFlat for faster search
    - For distributed deployments, switch to Pinecone or Weaviate
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from src.models.schemas import HistoricalMatch, IncidentReport

logger = logging.getLogger(__name__)

# Lazy-loaded globals to avoid import errors when deps aren't installed
_model = None
_index = None
_metadata: list[dict] = []
_index_dir: Optional[Path] = None
_initialized = False


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Sentence transformer model loaded: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not installed. Memory disabled.")
            return None
    return _model


def _ensure_index():
    """Ensure FAISS index is initialized."""
    global _index
    if _index is None:
        try:
            import faiss
            _index = faiss.IndexFlatIP(384)  # 384 = MiniLM-L6-v2 embedding dimension
            logger.info("FAISS index initialized (384 dimensions)")
        except ImportError:
            logger.warning("faiss-cpu not installed. Memory disabled.")
            return None
    return _index


def initialize(index_dir: str = "data/vector_index") -> bool:
    """Initialize the vector memory system.

    Loads existing index from disk if available, otherwise creates a new one.

    Args:
        index_dir: Directory to store/load the FAISS index and metadata.

    Returns:
        True if initialization was successful, False otherwise.
    """
    global _index, _metadata, _index_dir, _initialized

    _index_dir = Path(index_dir)
    _index_dir.mkdir(parents=True, exist_ok=True)

    model = _get_model()
    if model is None:
        return False

    index = _ensure_index()
    if index is None:
        return False

    # Try to load existing index
    index_path = _index_dir / "attack_index.faiss"
    meta_path = _index_dir / "attack_metadata.json"

    if index_path.exists() and meta_path.exists():
        try:
            import faiss
            _index = faiss.read_index(str(index_path))
            _metadata = json.loads(meta_path.read_text())
            logger.info("Loaded existing index: %d incidents", _index.ntotal)
        except Exception as e:
            logger.warning("Failed to load index: %s. Starting fresh.", e)
            _ensure_index()
            _metadata = []
    else:
        logger.info("No existing index found. Starting fresh.")

    _initialized = True
    return True


def add_incident(incident: IncidentReport) -> bool:
    """Embed and store a processed incident in the vector index.

    Args:
        incident: The completed incident report to store.

    Returns:
        True if the incident was successfully added.
    """
    if not _initialized:
        initialize()

    model = _get_model()
    index = _ensure_index()
    if model is None or index is None:
        return False

    # Create embedding text from the most informative fields
    embed_text = (
        f"Attack: {incident.attack_type.value} | "
        f"Severity: {incident.severity.value} | "
        f"IP: {incident.source_ip} | "
        f"Reasoning: {incident.reasoning} | "
        f"Log: {incident.indicators}"
    )

    try:
        # Encode and normalize for cosine similarity
        embedding = model.encode([embed_text], normalize_embeddings=True)
        index.add(np.array(embedding, dtype=np.float32))

        # Store metadata
        meta = {
            "event_id": incident.event_id,
            "timestamp": incident.timestamp,
            "attack_type": incident.attack_type.value,
            "severity": incident.severity.value,
            "source_ip": incident.source_ip,
            "confidence_score": incident.confidence_score,
            "reasoning": incident.reasoning[:200],
            "raw_log_snippet": embed_text[:150],
        }
        _metadata.append(meta)

        # Persist to disk
        _persist()

        logger.info("Incident added to memory: %s (total: %d)", incident.event_id, index.ntotal)
        return True

    except Exception as e:
        logger.error("Failed to add incident to memory: %s", e)
        return False


def search_similar(raw_log: str, k: int = 5) -> list[HistoricalMatch]:
    """Find the k most similar past incidents to a given log.

    Args:
        raw_log: The raw log text to compare against.
        k: Number of similar results to return.

    Returns:
        List of HistoricalMatch objects with similarity scores.
    """
    if not _initialized:
        initialize()

    model = _get_model()
    index = _ensure_index()
    if model is None or index is None or index.ntotal == 0:
        return []

    try:
        query_embedding = model.encode([raw_log], normalize_embeddings=True)
        scores, indices = index.search(np.array(query_embedding, dtype=np.float32), min(k, index.ntotal))

        matches = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(_metadata):
                continue
            meta = _metadata[idx]
            matches.append(HistoricalMatch(
                timestamp=meta.get("timestamp", ""),
                attack_type=meta.get("attack_type", "unknown"),
                severity=meta.get("severity", "info"),
                source_ip=meta.get("source_ip", ""),
                raw_log_snippet=meta.get("raw_log_snippet", ""),
                similarity_score=round(float(score), 3),
            ))

        # Filter out very low similarity matches
        matches = [m for m in matches if m.similarity_score > 0.3]
        logger.info("Memory search returned %d relevant matches", len(matches))
        return matches

    except Exception as e:
        logger.error("Memory search failed: %s", e)
        return []


def search_by_ip(ip_address: str) -> list[HistoricalMatch]:
    """Find all past incidents from a specific IP address.

    Args:
        ip_address: The IP address to search for.

    Returns:
        List of HistoricalMatch objects from this IP.
    """
    if not _initialized:
        initialize()

    matches = []
    for meta in _metadata:
        if meta.get("source_ip") == ip_address:
            matches.append(HistoricalMatch(
                timestamp=meta.get("timestamp", ""),
                attack_type=meta.get("attack_type", "unknown"),
                severity=meta.get("severity", "info"),
                source_ip=meta.get("source_ip", ""),
                raw_log_snippet=meta.get("raw_log_snippet", ""),
                similarity_score=1.0,
            ))

    logger.info("IP search for %s: %d past incidents found", ip_address, len(matches))
    return matches


def get_stats() -> dict:
    """Return statistics about the vector memory.

    Returns:
        Dict with total_incidents, unique_ips, and other stats.
    """
    if not _initialized:
        initialize()

    unique_ips = set(m.get("source_ip", "") for m in _metadata)
    attack_types = {}
    for m in _metadata:
        at = m.get("attack_type", "unknown")
        attack_types[at] = attack_types.get(at, 0) + 1

    return {
        "total_incidents": len(_metadata),
        "unique_ips": len(unique_ips),
        "attack_type_distribution": attack_types,
        "index_initialized": _initialized,
    }


def _persist() -> None:
    """Save the FAISS index and metadata to disk."""
    if _index_dir is None or _index is None:
        return

    try:
        import faiss
        index_path = _index_dir / "attack_index.faiss"
        meta_path = _index_dir / "attack_metadata.json"

        faiss.write_index(_index, str(index_path))
        meta_path.write_text(json.dumps(_metadata, indent=2))
    except Exception as e:
        logger.error("Failed to persist vector index: %s", e)
