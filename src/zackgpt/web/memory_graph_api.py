"""
MemoryGraph Frontend Logging API
Handles collection and processing of frontend MemoryGraph logs
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..utils.logger import (
    debug_log, debug_error, debug_success, debug_info,
    log_learning_event, log_component_performance_update,
    log_performance_metric
)

router = APIRouter(prefix="/api/logs", tags=["frontend-logging"])

class MemoryGraphLogEntry(BaseModel):
    """Schema for MemoryGraph frontend log entries."""
    timestamp: str
    component: str
    event: str
    data: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None

class BatchLogRequest(BaseModel):
    """Schema for batch log requests."""
    logs: List[MemoryGraphLogEntry]

class LogResponse(BaseModel):
    """Response schema for log endpoints."""
    status: str
    message: str
    processed_count: Optional[int] = None

@router.post("/frontend", response_model=LogResponse)
async def log_frontend_event(log_entry: MemoryGraphLogEntry, request: Request):
    """
    Log a single frontend MemoryGraph event.
    
    This endpoint receives structured log data from the MemoryGraph React component
    and integrates it with the backend logging and analytics system.
    """
    try:
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
        except ValueError:
            timestamp = datetime.now()
        
        # Extract client information
        client_info = {
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": log_entry.user.get("userAgent", "unknown") if log_entry.user else "unknown",
            "url": log_entry.user.get("url", "unknown") if log_entry.user else "unknown",
            "viewport": log_entry.user.get("viewport", {}) if log_entry.user else {}
        }
        
        # Log the event with appropriate level based on event type
        if log_entry.event.startswith('error'):
            debug_error(f"MemoryGraph Frontend Error: {log_entry.event}", data={
                "event_data": log_entry.data,
                "performance": log_entry.performance,
                "client": client_info,
                "timestamp": timestamp.isoformat()
            })
        elif log_entry.event.startswith('warning'):
            debug_log(f"MemoryGraph Frontend Warning: {log_entry.event}", data={
                "event_data": log_entry.data,
                "performance": log_entry.performance,
                "client": client_info,
                "timestamp": timestamp.isoformat()
            }, prefix="⚠️")
        else:
            debug_info(f"MemoryGraph Frontend Event: {log_entry.event}", data={
                "event_data": log_entry.data,
                "performance": log_entry.performance,
                "client": client_info,
                "timestamp": timestamp.isoformat()
            })
        
        # Handle performance metrics
        if log_entry.performance:
            duration = log_entry.performance.get('duration')
            if duration is not None:
                log_performance_metric(
                    operation=f"frontend_{log_entry.event}",
                    duration=duration / 1000.0,  # Convert ms to seconds
                    success=True,
                    error_message=None
                )
        
        # Handle learning events for user interactions
        if log_entry.event.startswith('interaction_'):
            log_learning_event(
                event_type=f"frontend_{log_entry.event}",
                component_name="MemoryGraph",
                component_type="frontend_visualization",
                interaction_data=log_entry.data,
                performance_data=log_entry.performance,
                client_info=client_info,
                timestamp=timestamp.isoformat()
            )
        
        # Handle visualization performance events
        elif log_entry.event.startswith('viz_') or log_entry.event.startswith('performance_'):
            if log_entry.performance:
                node_count = log_entry.performance.get('nodeCount', 0)
                link_count = log_entry.performance.get('linkCount', 0)
                render_time = log_entry.performance.get('renderTime', 0)
                
                log_component_performance_update(
                    component_name="MemoryGraph",
                    success=True,
                    weight_before=0.0,  # Not applicable for visualization
                    weight_after=0.0,   # Not applicable for visualization
                    success_rate_before=1.0,
                    success_rate_after=1.0,
                    visualization_metrics={
                        "node_count": node_count,
                        "link_count": link_count,
                        "render_time_ms": render_time,
                        "event_type": log_entry.event
                    },
                    timestamp=timestamp.isoformat()
                )
        
        # Handle filter operations
        elif log_entry.event.startswith('filter_'):
            if log_entry.data:
                log_learning_event(
                    event_type=f"frontend_{log_entry.event}",
                    component_name="MemoryGraph",
                    component_type="frontend_filter",
                    filter_data=log_entry.data,
                    performance_data=log_entry.performance,
                    client_info=client_info,
                    timestamp=timestamp.isoformat()
                )
        
        debug_success(f"Frontend log processed successfully: {log_entry.event}")
        
        return LogResponse(
            status="success",
            message=f"Log entry for event '{log_entry.event}' processed successfully"
        )
        
    except Exception as e:
        debug_error(f"Failed to process frontend log entry: {log_entry.event}", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process log entry: {str(e)}"
        )

@router.post("/frontend/batch", response_model=LogResponse)
async def log_frontend_batch(batch_request: BatchLogRequest, request: Request):
    """
    Log multiple frontend MemoryGraph events in a batch.
    
    This endpoint is optimized for processing multiple log entries at once,
    reducing network overhead for high-frequency logging scenarios.
    """
    try:
        processed_count = 0
        failed_entries = []
        
        for i, log_entry in enumerate(batch_request.logs):
            try:
                # Process each log entry similar to single entry endpoint
                # but without individual HTTP responses
                
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.now()
                
                # Extract client information
                client_info = {
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": log_entry.user.get("userAgent", "unknown") if log_entry.user else "unknown",
                    "url": log_entry.user.get("url", "unknown") if log_entry.user else "unknown",
                    "viewport": log_entry.user.get("viewport", {}) if log_entry.user else {},
                    "batch_index": i,
                    "batch_size": len(batch_request.logs)
                }
                
                # Batch logging with reduced verbosity
                debug_info(f"Batch MemoryGraph Event [{i+1}/{len(batch_request.logs)}]: {log_entry.event}", data={
                    "event_data": log_entry.data,
                    "performance": log_entry.performance,
                    "client": client_info,
                    "timestamp": timestamp.isoformat()
                })
                
                # Handle performance metrics for batch
                if log_entry.performance:
                    duration = log_entry.performance.get('duration')
                    if duration is not None:
                        log_performance_metric(
                            operation=f"frontend_batch_{log_entry.event}",
                            duration=duration / 1000.0,
                            success=True
                        )
                
                # Handle learning events for batch
                if log_entry.event.startswith(('interaction_', 'filter_')):
                    log_learning_event(
                        event_type=f"frontend_batch_{log_entry.event}",
                        component_name="MemoryGraph",
                        component_type="frontend_visualization_batch",
                        interaction_data=log_entry.data,
                        performance_data=log_entry.performance,
                        client_info=client_info,
                        timestamp=timestamp.isoformat()
                    )
                
                processed_count += 1
                
            except Exception as e:
                debug_error(f"Failed to process batch entry {i}: {log_entry.event}", e)
                failed_entries.append({
                    "index": i,
                    "event": log_entry.event,
                    "error": str(e)
                })
        
        # Log batch summary
        log_learning_event(
            event_type="frontend_batch_complete",
            component_name="MemoryGraph",
            component_type="frontend_batch_logging",
            batch_summary={
                "total_entries": len(batch_request.logs),
                "processed_count": processed_count,
                "failed_count": len(failed_entries),
                "failed_entries": failed_entries
            },
            timestamp=datetime.now().isoformat()
        )
        
        debug_success(f"Frontend batch processed: {processed_count}/{len(batch_request.logs)} entries successful")
        
        return LogResponse(
            status="success" if len(failed_entries) == 0 else "partial_success",
            message=f"Processed {processed_count}/{len(batch_request.logs)} log entries successfully",
            processed_count=processed_count
        )
        
    except Exception as e:
        debug_error("Failed to process frontend log batch", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process log batch: {str(e)}"
        )

@router.get("/frontend/analytics")
async def get_memory_graph_analytics():
    """
    Get analytics summary for MemoryGraph frontend usage.
    
    This endpoint provides aggregated insights about how users interact
    with the MemoryGraph visualization component.
    """
    try:
        # This would typically query the analytics database
        # For now, return a summary structure
        
        analytics_summary = {
            "summary": {
                "total_events": 0,
                "unique_sessions": 0,
                "avg_session_duration": 0,
                "most_common_interactions": []
            },
            "performance": {
                "avg_render_time": 0,
                "avg_node_count": 0,
                "avg_link_count": 0,
                "performance_trends": []
            },
            "user_behavior": {
                "most_clicked_tags": [],
                "search_patterns": [],
                "filter_usage": []
            },
            "errors": {
                "error_rate": 0,
                "common_errors": [],
                "error_trends": []
            }
        }
        
        debug_info("MemoryGraph analytics requested", data=analytics_summary)
        
        return analytics_summary
        
    except Exception as e:
        debug_error("Failed to generate MemoryGraph analytics", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )

@router.delete("/frontend/logs")
async def clear_memory_graph_logs():
    """
    Clear stored MemoryGraph frontend logs.
    
    This endpoint is useful for development and testing purposes.
    In production, this might be restricted or require authentication.
    """
    try:
        # This would typically clear logs from the analytics database
        # For now, just log the action
        
        debug_info("MemoryGraph frontend logs cleared")
        
        return LogResponse(
            status="success",
            message="MemoryGraph frontend logs cleared successfully"
        )
        
    except Exception as e:
        debug_error("Failed to clear MemoryGraph logs", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear logs: {str(e)}"
        ) 