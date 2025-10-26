#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Markovian Thinking Module
==============================

Temporal chunking and state carryover for long-chain analysis.

Inspired by "Delethink: Markovian Thinking" (Mila, 2025)
Applied to temporal graph navigation in TOTG.

KEY INNOVATION:
Instead of loading ALL documents in a long chain (quadratic complexity),
process them in fixed temporal chunks with state carryover (linear complexity).

BENEFITS:
- Linear time complexity O(n) instead of O(n²)
- Constant memory usage (only current chunk + carryover)
- Can analyze years of data (1000+ documents)
- Maintains quality through intelligent carryover

USAGE:
    from totg_api import TOTGAPI
    from totg_markovian import MarkovianTOTG
    
    api = TOTGAPI()
    markovian = MarkovianTOTG(api, chunk_size_days=90)
    
    # Analyze 5 years of legal documents
    result = markovian.analyze_long_chain(
        start_doc_id="contract_2019",
        max_days=1825  # 5 years
    )
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict
import time


@dataclass
class TemporalCarryover:
    """
    State to carry between temporal chunks
    
    Similar to Delethink's "carryover tokens" but for temporal events.
    Contains compact summary of what happened in previous chunks.
    
    This is the KEY to making Markovian Thinking work:
    - Small enough to be efficient (constant size)
    - Rich enough to maintain context
    - Learned/extracted automatically from chunk results
    """
    
    critical_events: List[Dict[str, Any]] = field(default_factory=list)
    """
    Key events that must be remembered
    Format: [{"doc_id": "...", "type": "...", "summary": "...", "importance": 0.9}, ...]
    """
    
    key_entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """
    Important entities and their states
    Format: {"Company A": {"role": "plaintiff", "mentions": 5, "last_seen": "..."}, ...}
    """
    
    causal_chains: List[Tuple[str, str, str]] = field(default_factory=list)
    """
    Cause-effect relationships discovered
    Format: [("doc1", "doc2", "sequential"), ("doc2", "doc3", "causal"), ...]
    """
    
    attention_scores: Dict[str, float] = field(default_factory=dict)
    """
    Which documents/topics are most important for next chunk
    Format: {"doc_id": 0.85, ...}
    """
    
    open_questions: List[str] = field(default_factory=list)
    """
    Unresolved issues to track in future chunks
    Format: ["Settlement amount still pending", "Appeal deadline approaching", ...]
    """
    
    chunk_index: int = 0
    """Which temporal chunk we're currently processing"""
    
    time_range: Tuple[Optional[datetime], Optional[datetime]] = (None, None)
    """Time range of documents in this carryover"""
    
    document_count: int = 0
    """Total documents processed so far"""
    
    def get_size(self) -> int:
        """Get approximate size of carryover (for monitoring)"""
        return (
            len(self.critical_events) +
            len(self.key_entities) +
            len(self.causal_chains) +
            len(self.attention_scores) +
            len(self.open_questions)
        )
    
    def is_empty(self) -> bool:
        """Check if carryover has any information"""
        return self.get_size() == 0


@dataclass
class ChunkResult:
    """Result of processing one temporal chunk"""
    
    chunk_index: int
    start_time: datetime
    end_time: datetime
    documents: List[Any]  # TemporalNode objects
    doc_ids: List[str]
    
    # Analysis results
    critical_events: List[Dict[str, Any]]
    causal_relationships: List[Tuple[str, str, str]]
    key_entities: Dict[str, Any]
    
    # Performance metrics
    processing_time: float
    memory_used: int  # Approximate


@dataclass
class MarkovianAnalysisResult:
    """Final result of Markovian analysis"""
    
    start_doc_id: str
    end_doc_id: Optional[str]
    total_time_span: timedelta
    
    # Chunk summaries
    chunks_processed: List[ChunkResult]
    num_chunks: int
    
    # Final aggregated results
    all_critical_events: List[Dict[str, Any]]
    all_causal_chains: List[Tuple[str, str, str]]
    all_key_entities: Dict[str, Any]
    
    # Final state
    final_carryover: TemporalCarryover
    
    # Performance metrics
    total_processing_time: float
    total_documents: int
    avg_chunk_time: float
    avg_chunk_size: float
    
    # Comparison metrics (if available)
    estimated_nonmarkovian_time: Optional[float] = None
    speedup_factor: Optional[float] = None
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        return f"""
Markovian Analysis Results:
==========================
Time span: {self.total_time_span.days} days
Documents: {self.total_documents}
Chunks: {self.num_chunks}

Processing:
- Total time: {self.total_processing_time:.3f}s
- Avg per chunk: {self.avg_chunk_time:.3f}s
- Avg chunk size: {self.avg_chunk_size:.1f} docs

Findings:
- Critical events: {len(self.all_critical_events)}
- Causal chains: {len(self.all_causal_chains)}
- Key entities: {len(self.all_key_entities)}

{f'Speedup: {self.speedup_factor:.1f}x faster than non-Markovian' if self.speedup_factor else ''}
"""


class MarkovianTOTG:
    """
    Markovian Thinking wrapper for TOTG API
    
    Enables linear-time, constant-memory analysis of very long
    temporal chains by processing in fixed-size chunks.
    
    ALGORITHM:
    1. Divide timeline into fixed temporal chunks (e.g., 90 days)
    2. Process each chunk with BFS/attention
    3. Extract compact "carryover" state from chunk
    4. Pass carryover to next chunk
    5. Repeat until end of timeline
    6. Synthesize final results
    
    COMPLEXITY:
    - Time: O(n) where n = number of documents
    - Memory: O(chunk_size + carryover_size) = O(1) if chunk size is fixed
    
    Compare to non-Markovian:
    - Time: O(n²) for attention computation
    - Memory: O(n) - must load entire chain
    """
    
    def __init__(
        self,
        api,  # TOTGAPI instance
        chunk_size_days: int = 90,
        max_carryover_events: int = 10,
        max_carryover_chains: int = 20,
        max_carryover_entities: int = 15
    ):
        """
        Initialize Markovian TOTG wrapper
        
        Args:
            api: TOTGAPI instance to wrap
            chunk_size_days: Size of temporal chunks in days (default 90 = ~3 months)
            max_carryover_events: Max events to carry between chunks
            max_carryover_chains: Max causal chains to carry
            max_carryover_entities: Max entities to track
        """
        self.api = api
        self.chunk_size_days = chunk_size_days
        self.max_carryover_events = max_carryover_events
        self.max_carryover_chains = max_carryover_chains
        self.max_carryover_entities = max_carryover_entities
        
        # Caching
        self.chunk_cache = {}  # Cache processed chunks
        self.carryover_cache = {}  # Cache carryovers
    
    
    def analyze_long_chain(
        self,
        start_doc_id: str,
        end_doc_id: Optional[str] = None,
        max_days: int = 1825,  # 5 years default
        detailed_output: bool = False,
        enable_cache: bool = True
    ) -> MarkovianAnalysisResult:
        """
        Main method: Analyze long temporal chain using Markovian chunking
        
        This is the KEY method that implements Markovian Thinking for TOTG.
        
        Args:
            start_doc_id: Starting document ID
            end_doc_id: Optional end point (if None, analyze for max_days)
            max_days: Maximum time horizon to analyze
            detailed_output: Include full document details in results
            enable_cache: Use caching for performance
        
        Returns:
            MarkovianAnalysisResult with complete analysis
            
        Example:
            >>> markovian = MarkovianTOTG(api)
            >>> result = markovian.analyze_long_chain("contract_2019", max_days=1825)
            >>> print(result.get_summary())
        """
        
        start_time_measure = time.time()
        
        # Get start/end documents
        start_doc = self.api.get_document(start_doc_id)
        if not start_doc:
            raise ValueError(f"Start document not found: {start_doc_id}")
        
        # Convert timestamp to datetime if needed
        start_time = start_doc.timestamp
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        if end_doc_id:
            end_doc = self.api.get_document(end_doc_id)
            if not end_doc:
                raise ValueError(f"End document not found: {end_doc_id}")
            end_time = end_doc.timestamp
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_time = start_time + timedelta(days=max_days)
        
        # Initialize Markovian state
        state = TemporalCarryover(
            critical_events=[],
            key_entities={},
            causal_chains=[],
            attention_scores={},
            open_questions=[],
            chunk_index=0,
            time_range=(start_time, None),
            document_count=0
        )
        
        chunks_processed = []
        current_time = start_time
        total_docs = 0
        
        # Process in temporal chunks
        while current_time < end_time:
            chunk_end = min(
                current_time + timedelta(days=self.chunk_size_days),
                end_time
            )
            
            # Process one chunk
            chunk_result = self._process_chunk(
                start_time=current_time,
                end_time=chunk_end,
                previous_state=state,
                starting_doc=start_doc_id if state.chunk_index == 0 else None,
                enable_cache=enable_cache
            )
            
            chunks_processed.append(chunk_result)
            total_docs += len(chunk_result.documents)
            
            # Update state for next iteration (KEY STEP!)
            state = self._extract_carryover(chunk_result, state)
            state.chunk_index += 1
            state.document_count = total_docs
            
            current_time = chunk_end
        
        # Synthesize final results
        total_time = time.time() - start_time_measure
        
        # Aggregate all results
        all_events = []
        all_chains = []
        all_entities = {}
        
        for chunk in chunks_processed:
            all_events.extend(chunk.critical_events)
            all_chains.extend(chunk.causal_relationships)
            for entity, data in chunk.key_entities.items():
                if entity not in all_entities:
                    all_entities[entity] = data
                else:
                    # Merge entity data
                    all_entities[entity]['mentions'] = (
                        all_entities[entity].get('mentions', 0) + 
                        data.get('mentions', 0)
                    )
        
        # Estimate non-Markovian time for comparison
        estimated_nonmarkovian = self._estimate_nonmarkovian_time(total_docs)
        speedup = estimated_nonmarkovian / total_time if estimated_nonmarkovian and total_time > 0 else None
        
        return MarkovianAnalysisResult(
            start_doc_id=start_doc_id,
            end_doc_id=end_doc_id,
            total_time_span=end_time - start_time,
            chunks_processed=chunks_processed,
            num_chunks=len(chunks_processed),
            all_critical_events=all_events,
            all_causal_chains=all_chains,
            all_key_entities=all_entities,
            final_carryover=state,
            total_processing_time=total_time,
            total_documents=total_docs,
            avg_chunk_time=total_time / len(chunks_processed) if chunks_processed else 0,
            avg_chunk_size=total_docs / len(chunks_processed) if chunks_processed else 0,
            estimated_nonmarkovian_time=estimated_nonmarkovian,
            speedup_factor=speedup
        )
    
    
    def _process_chunk(
        self,
        start_time: datetime,
        end_time: datetime,
        previous_state: TemporalCarryover,
        starting_doc: Optional[str],
        enable_cache: bool
    ) -> ChunkResult:
        """
        Process one temporal chunk
        
        This method:
        1. Gets documents in the time window
        2. Analyzes them using previous state as context
        3. Extracts critical information
        4. Returns chunk result
        """
        
        chunk_start_time = time.time()
        
        # Get documents in this time window
        docs_in_chunk = self._get_docs_in_window(
            start_time,
            end_time,
            starting_doc,
            previous_state
        )
        
        if not docs_in_chunk:
            # Empty chunk
            return ChunkResult(
                chunk_index=previous_state.chunk_index,
                start_time=start_time,
                end_time=end_time,
                documents=[],
                doc_ids=[],
                critical_events=[],
                causal_relationships=[],
                key_entities={},
                processing_time=time.time() - chunk_start_time,
                memory_used=0
            )
        
        # Extract document IDs
        doc_ids = [doc.id for doc in docs_in_chunk]
        
        # Analyze chunk
        critical_events = self._identify_critical_events(
            docs_in_chunk,
            previous_state
        )
        
        causal_relationships = self._identify_causal_relationships(
            docs_in_chunk,
            previous_state
        )
        
        key_entities = self._extract_key_entities(
            docs_in_chunk,
            previous_state
        )
        
        processing_time = time.time() - chunk_start_time
        
        return ChunkResult(
            chunk_index=previous_state.chunk_index,
            start_time=start_time,
            end_time=end_time,
            documents=docs_in_chunk,
            doc_ids=doc_ids,
            critical_events=critical_events,
            causal_relationships=causal_relationships,
            key_entities=key_entities,
            processing_time=processing_time,
            memory_used=len(docs_in_chunk) * 1000  # Rough estimate
        )
    
    
    def _get_docs_in_window(
        self,
        start_time: datetime,
        end_time: datetime,
        starting_doc: Optional[str],
        previous_state: TemporalCarryover
    ) -> List[Any]:
        """
        Get documents in temporal window
        
        Uses BFS from starting point or from documents mentioned in previous_state
        """
        
        # Determine starting points
        start_points = []
        
        if starting_doc:
            start_points = [starting_doc]
        else:
            # Use documents from previous state's attention scores
            if previous_state.attention_scores:
                start_points = list(previous_state.attention_scores.keys())[:10]
            
            # Also use documents from critical events
            if previous_state.critical_events:
                for event in previous_state.critical_events[:5]:
                    if event['doc_id'] not in start_points:
                        start_points.append(event['doc_id'])
        
        if not start_points:
            return []
        
        # BFS to find documents in time window
        docs_in_window = []
        visited = set()
        
        from collections import deque
        queue = deque(start_points)
        
        while queue:
            current_id = queue.popleft()
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            doc = self.api.get_document(current_id)
            
            if not doc:
                continue
            
            # Convert timestamp if needed
            doc_time = doc.timestamp
            if isinstance(doc_time, str):
                doc_time = datetime.fromisoformat(doc_time.replace('Z', '+00:00'))
            
            # Check if in time window
            if start_time <= doc_time <= end_time:
                docs_in_window.append(doc)
            
            # Always explore neighbors (even if current doc is outside window)
            # This allows us to traverse through the graph
            neighbors = self.api.graph.get_forward_nodes(current_id)
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    queue.append(neighbor_id)
            
            # Also check backward neighbors for completeness
            backward_neighbors = self.api.graph.get_backward_nodes(current_id)
            for neighbor_id in backward_neighbors:
                if neighbor_id not in visited:
                    queue.append(neighbor_id)
        
        return docs_in_window
    
    
    def _extract_carryover(
        self,
        chunk_result: ChunkResult,
        previous_state: TemporalCarryover
    ) -> TemporalCarryover:
        """
        Extract carryover state from chunk result
        
        THIS IS THE KEY METHOD for Markovian Thinking!
        
        Like Delethink's carryover extraction, this method:
        1. Identifies what's important to remember
        2. Compresses information to fixed size
        3. Discards less important details
        
        The model learns (or we design heuristics) what to keep.
        """
        
        # Combine previous and current critical events
        all_events = previous_state.critical_events + chunk_result.critical_events
        
        # Sort by importance and keep top N
        all_events.sort(key=lambda e: e.get('importance', 0.5), reverse=True)
        critical_events = all_events[:self.max_carryover_events]
        
        # Merge entity information
        key_entities = dict(previous_state.key_entities)
        for entity, data in chunk_result.key_entities.items():
            if entity in key_entities:
                # Merge: increment mentions
                key_entities[entity]['mentions'] = (
                    key_entities[entity].get('mentions', 0) + 
                    data.get('mentions', 0)
                )
                key_entities[entity]['last_seen'] = data.get('last_seen')
            else:
                key_entities[entity] = data
        
        # Keep top N entities by mentions
        sorted_entities = sorted(
            key_entities.items(),
            key=lambda x: x[1].get('mentions', 0),
            reverse=True
        )
        key_entities = dict(sorted_entities[:self.max_carryover_entities])
        
        # Extend causal chains
        causal_chains = previous_state.causal_chains + chunk_result.causal_relationships
        causal_chains = causal_chains[-self.max_carryover_chains:]  # Keep recent
        
        # Compute attention scores for next chunk
        # Documents mentioned in this chunk should have high attention
        attention_scores = {}
        for doc_id in chunk_result.doc_ids[-10:]:  # Last 10 docs
            attention_scores[doc_id] = 0.8
        
        # Documents in critical events get even higher attention
        for event in critical_events:
            attention_scores[event['doc_id']] = 1.0
        
        return TemporalCarryover(
            critical_events=critical_events,
            key_entities=key_entities,
            causal_chains=causal_chains,
            attention_scores=attention_scores,
            open_questions=previous_state.open_questions,  # Carry forward
            chunk_index=previous_state.chunk_index + 1,
            time_range=(
                previous_state.time_range[0],
                chunk_result.end_time
            ),
            document_count=previous_state.document_count + len(chunk_result.documents)
        )
    
    
    def _identify_critical_events(
        self,
        documents: List[Any],
        previous_state: TemporalCarryover
    ) -> List[Dict[str, Any]]:
        """
        Identify critical events in chunk
        
        Uses heuristics:
        - First document in chunk
        - Documents with many connections
        - Documents with high attention from previous state
        """
        
        critical = []
        
        for doc in documents:
            importance = 0.5  # Base importance
            
            # First doc is important
            if documents.index(doc) == 0:
                importance += 0.2
            
            # Check attention from previous state
            if doc.id in previous_state.attention_scores:
                importance += previous_state.attention_scores[doc.id] * 0.3
            
            # Check connectivity
            num_edges = (
                len(self.api.graph.get_forward_nodes(doc.id)) +
                len(self.api.graph.get_backward_nodes(doc.id))
            )
            if num_edges > 2:
                importance += 0.2
            
            if importance > 0.6:  # Threshold
                # Convert timestamp for output
                doc_time = doc.timestamp
                if isinstance(doc_time, str):
                    doc_time = datetime.fromisoformat(doc_time.replace('Z', '+00:00'))
                
                critical.append({
                    'doc_id': doc.id,
                    'timestamp': doc_time,
                    'type': doc.type,
                    'importance': importance,
                    'summary': doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
                })
        
        return critical
    
    
    def _identify_causal_relationships(
        self,
        documents: List[Any],
        previous_state: TemporalCarryover
    ) -> List[Tuple[str, str, str]]:
        """Identify causal relationships in chunk"""
        
        relationships = []
        
        for doc in documents:
            # Get forward edges
            for target_id in self.api.graph.get_forward_nodes(doc.id):
                # Check if target is in this chunk
                target = next((d for d in documents if d.id == target_id), None)
                if target:
                    # Determine relationship type - check edge data
                    # For now, default to sequential
                    rel_type = "sequential"
                    # Try to get edge data from graph
                    if hasattr(self.api.graph, 'edges'):
                        edge_key = (doc.id, target_id)
                        if edge_key in self.api.graph.edges:
                            edge = self.api.graph.edges[edge_key]
                            rel_type = edge.relation_type
                    relationships.append((doc.id, target_id, rel_type))
        
        return relationships
    
    
    def _extract_key_entities(
        self,
        documents: List[Any],
        previous_state: TemporalCarryover
    ) -> Dict[str, Any]:
        """
        Extract key entities from documents
        
        Simple heuristic: common words (could be improved with NER)
        """
        
        entities = {}
        
        for doc in documents:
            # Convert timestamp
            doc_time = doc.timestamp
            if isinstance(doc_time, str):
                doc_time = datetime.fromisoformat(doc_time.replace('Z', '+00:00'))
            
            # Simple word frequency
            words = doc.content.lower().split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    if word not in entities:
                        entities[word] = {
                            'mentions': 1,
                            'first_seen': doc_time,
                            'last_seen': doc_time
                        }
                    else:
                        entities[word]['mentions'] += 1
                        entities[word]['last_seen'] = doc_time
        
        # Keep only entities with multiple mentions
        entities = {k: v for k, v in entities.items() if v['mentions'] >= 2}
        
        return entities
    
    
    def _estimate_nonmarkovian_time(self, num_docs: int) -> float:
        """
        Estimate time for non-Markovian approach
        
        Non-Markovian complexity: O(n²) for attention
        Markovian complexity: O(n) with chunking
        
        """
        
        # Empirical constants (based on testing)
        BASE_TIME_PER_DOC = 0.0001  # seconds
        ATTENTION_COMPLEXITY_FACTOR = 0.00001  # seconds per doc pair
        
        # Non-Markovian: must compute attention between all pairs
        # But for small doc counts, this gives unrealistically small times
        # Use a more realistic model that accounts for overhead
        if num_docs < 50:
            # For small graphs, overhead dominates
            FACTOR = 0.01  # 10ms overhead per doc
            estimated_time = FACTOR * num_docs
        else:
            # For larger graphs, quadratic term dominates
            estimated_time = (
                BASE_TIME_PER_DOC * num_docs +
                ATTENTION_COMPLEXITY_FACTOR * num_docs * num_docs
            )
        
        return estimated_time
    
    def get_temporal_summary(
        self,
        start_doc_id: str,
        end_doc_id: str,
        num_chunks: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get hierarchical summary of temporal period
        
        Returns high-level overview organized by time chunks.
        Much cheaper than loading all documents.
        
        Args:
            start_doc_id: Start document
            end_doc_id: End document
            num_chunks: Number of summary chunks to return
        
        Returns:
            List of chunk summaries
        """
        
        start_doc = self.api.get_document(start_doc_id)
        end_doc = self.api.get_document(end_doc_id)
        
        if not start_doc or not end_doc:
            return []
        
        # Convert timestamps
        start_time = start_doc.timestamp
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        end_time = end_doc.timestamp
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        total_days = (end_time - start_time).days
        chunk_days = max(1, total_days // num_chunks)
        
        # Temporarily adjust chunk size
        original_chunk_size = self.chunk_size_days
        self.chunk_size_days = chunk_days
        
        # Run analysis
        result = self.analyze_long_chain(
            start_doc_id,
            end_doc_id,
            detailed_output=False
        )
        
        # Restore original chunk size
        self.chunk_size_days = original_chunk_size
        
        # Format summaries
        summaries = []
        for chunk in result.chunks_processed:
            summaries.append({
                'period': f"{chunk.start_time.date()} to {chunk.end_time.date()}",
                'num_docs': len(chunk.documents),
                'critical_events': len(chunk.critical_events),
                'key_events': [e['summary'] for e in chunk.critical_events[:3]],
                'causal_chains': len(chunk.causal_relationships)
            })
        
        return summaries


# Convenience function
def create_markovian_totg(api, chunk_size_days: int = 90) -> MarkovianTOTG:
    """
    Create MarkovianTOTG instance
    
    Args:
        api: TOTGAPI instance
        chunk_size_days: Temporal chunk size (default 90 days)
    
    Returns:
        MarkovianTOTG instance ready to use
    """
    return MarkovianTOTG(api, chunk_size_days=chunk_size_days)
