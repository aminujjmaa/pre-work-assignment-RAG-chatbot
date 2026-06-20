import re
from typing import List, Dict, Any


def chunk_pages(
    pages: List[Dict[str, Any]],
    chunk_size_words: int = 500,
    overlap_words: int = 80,
) -> List[Dict[str, Any]]:
    """
    Sliding-window word-based chunker with overlap.
    Each chunk carries metadata: page range, chunk index.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_idx = 0

    # Build a flat list of (word, page_num) pairs
    word_page_pairs: List[tuple] = []
    for page in pages:
        words = page["text"].split()
        for w in words:
            word_page_pairs.append((w, page["page_num"]))

    total = len(word_page_pairs)
    if total == 0:
        return chunks

    start = 0
    while start < total:
        end = min(start + chunk_size_words, total)
        segment = word_page_pairs[start:end]

        words_only = [w for w, _ in segment]
        pages_only = [p for _, p in segment]

        text = " ".join(words_only)
        # Restore paragraph breaks heuristically
        text = re.sub(r" ([A-Z][a-z])", r"\n\1", text)

        chunks.append({
            "chunk_idx": chunk_idx,
            "text": text,
            "word_count": len(words_only),
            "page_start": pages_only[0],
            "page_end": pages_only[-1],
        })
        chunk_idx += 1

        if end == total:
            break
        start = end - overlap_words  # sliding window with overlap

    return chunks
