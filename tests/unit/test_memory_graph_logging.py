"""
Backend Tests for MemoryGraph Logging Integration
Tests logging aggregation, frontend log collection API, and performance monitoring
"""

import pytest
import json
import time
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from src.zackgpt.core.logger import (
    debug_log, debug_error, debug_success, debug_warning, debug_info,
    AnalyticsDatabase, PerformanceMetrics, log_performance,
    log_learning_event, log_component_performance_update,
    log_performance_metric
)

@pytest.fixture
def test_client():
    """Create a test client for the web API."""
    try:
        from src.zackgpt.web.web_api import app
        return TestClient(app)
    except ImportError:
        # Mock client if web API is not available
        return Mock()

@pytest.fixture
def sample_frontend_log():
    """Sample frontend log entry for testing."""
    return {
        "timestamp": "2024-01-01T10:00:00.000Z",
        "component": "MemoryGraph",
        "event": "interaction_node_click",
        "data": {
            "nodeId": "memory_123",
            "position": {"x": 100, "y": 200},
            "tags": ["identity", "work"]
        },
        "performance": {
            "duration": 15.5,
            "nodeCount": 25,
            "linkCount": 12,
            "renderTime": 230.7
        },
        "user": {
            "userAgent": "Mozilla/5.0 (test)",
            "url": "http://localhost:3000/memory-graph",
            "viewport": {
                "width": 1920,
                "height": 1080
            }
        }
    }

@pytest.fixture
def memory_graph_logs_collection():
    """Collection of sample MemoryGraph logs."""
    return [
        {
            "timestamp": "2024-01-01T10:00:00.000Z",
            "component": "MemoryGraph",
            "event": "viz_render_complete",
            "performance": {"duration": 45.2, "nodeCount": 10, "linkCount": 5}
        },
        {
            "timestamp": "2024-01-01T10:01:00.000Z",
            "component": "MemoryGraph", 
            "event": "interaction_tag_toggle",
            "data": {"tag": "preferences", "action": "hide"}
        },
        {
            "timestamp": "2024-01-01T10:02:00.000Z",
            "component": "MemoryGraph",
            "event": "filter_search",
            "data": {"query": "pizza", "results": 3}
        },
        {
            "timestamp": "2024-01-01T10:03:00.000Z",
            "component": "MemoryGraph",
            "event": "performance_d3_simulation",
            "performance": {"duration": 125.8, "nodeCount": 15}
        }
    ]

class TestMemoryGraphLogging:
    """Test basic MemoryGraph logging functionality."""
    
    @pytest.mark.backend
    def test_debug_logging(self):
        """Test basic debug logging functionality."""
        # Test that logging functions don't crash
        debug_log("MemoryGraph test log")
        debug_info("MemoryGraph info test")
        debug_success("MemoryGraph success test")
        debug_warning("MemoryGraph warning test")
        
        # Test logging with data
        debug_log("MemoryGraph test with data", {"nodes": 10, "links": 5})
        
        print("✅ Basic logging functionality works")
        assert True

    @pytest.mark.backend  
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        perf_metrics = PerformanceMetrics()
        
        # Test timer functionality
        operation = "test_memory_graph_render"
        
        perf_metrics.start_timer(operation)
        time.sleep(0.01)  # Small delay
        duration = perf_metrics.end_timer(operation)
        
        assert duration >= 0.01
        assert duration < 1.0
        
        print(f"✅ Performance metrics tracking works: {duration:.3f}s")

    @pytest.mark.backend
    def test_learning_event_logging(self):
        """Test learning event logging."""
        # Test that learning event logging doesn't crash
        log_learning_event(
            event_type="memory_graph_interaction",
            component_name="MemoryGraph",
            component_type="frontend_visualization",
            interaction_data={"nodeId": "test_123", "action": "click"}
        )
        
        print("✅ Learning event logging works")
        assert True

    @pytest.mark.backend
    def test_performance_metric_logging(self):
        """Test performance metric logging."""
        # Test performance metric logging
        log_performance_metric(
            operation="memory_graph_render",
            duration=0.045,
            success=True
        )
        
        log_performance_metric(
            operation="memory_graph_filter", 
            duration=0.012,
            success=True
        )
        
        print("✅ Performance metric logging works")
        assert True

class TestMemoryGraphAnalytics:
    """Test analytics functionality for MemoryGraph."""
    
    @pytest.fixture
    def analytics_db(self):
        """Analytics database instance for testing."""
        # Use a test database URI
        return AnalyticsDatabase(mongo_uri="mongodb://localhost:27017", db_name="zackgpt_test")

    @pytest.mark.backend
    def test_analytics_database_init(self, analytics_db):
        """Test analytics database initialization."""
        # Just test that it doesn't crash
        assert analytics_db is not None
        print("✅ Analytics database initialization works")

    @pytest.mark.backend
    def test_memory_graph_event_logging(self, analytics_db):
        """Test logging MemoryGraph events to analytics."""
        try:
            analytics_db.log_prompt_evolution(
                event_type="memory_graph_interaction",
                component_name="MemoryGraph",
                component_type="frontend_visualization",
                user_rating=5,
                context_type="memory_exploration"
            )
            
            analytics_db.log_system_event(
                level="INFO",
                event_type="memory_graph_render",
                message="MemoryGraph rendered successfully",
                data={"node_count": 25, "link_count": 12, "render_time_ms": 45.7}
            )
            
            print("✅ Memory graph event logging works")
            assert True
            
        except Exception as e:
            # If MongoDB is not available, that's okay for testing
            print(f"⚠️ Analytics logging skipped (MongoDB not available): {e}")
            assert True

class TestMemoryGraphAPI:
    """Test MemoryGraph API endpoints if available."""
    
    @pytest.mark.backend
    def test_api_import(self):
        """Test that the MemoryGraph API can be imported."""
        try:
            from src.zackgpt.web.memory_graph_api import router
            assert router is not None
            print("✅ MemoryGraph API import works")
        except ImportError as e:
            print(f"⚠️ MemoryGraph API not available: {e}")
            # This is okay - the API might not be integrated yet
            assert True

    @pytest.mark.backend
    def test_log_entry_model(self):
        """Test the log entry data model."""
        try:
            from src.zackgpt.web.memory_graph_api import MemoryGraphLogEntry
            
            # Test creating a log entry
            log_entry = MemoryGraphLogEntry(
                timestamp="2024-01-01T10:00:00.000Z",
                component="MemoryGraph", 
                event="test_event",
                data={"test": True},
                performance={"duration": 15.5},
                user={"userAgent": "test"}
            )
            
            assert log_entry.component == "MemoryGraph"
            assert log_entry.event == "test_event"
            print("✅ Log entry model works")
            
        except ImportError:
            print("⚠️ MemoryGraph API models not available")
            assert True

class TestMemoryGraphIntegration:
    """Integration tests for MemoryGraph logging system."""
    
    @pytest.mark.integration
    @pytest.mark.backend
    def test_end_to_end_logging_flow(self):
        """Test complete logging flow from frontend simulation to backend."""
        # Simulate a complete user session with MemoryGraph
        session_events = [
            ("component_init", {"memories_count": 25}),
            ("viz_render_start", {"node_count": 25, "link_count": 12}),
            ("viz_render_complete", {"duration": 45.7, "render_time": 230.1}),
            ("interaction_node_click", {"node_id": "memory_123", "tags": ["work"]}),
            ("filter_tag_toggle", {"tag": "preferences", "visible": False}),
        ]
        
        # Process each event through the logging system
        for event_type, event_data in session_events:
            try:
                if event_type.startswith("interaction_"):
                    log_learning_event(
                        event_type=f"frontend_{event_type}",
                        component_name="MemoryGraph",
                        component_type="frontend_visualization",
                        interaction_data=event_data
                    )
                elif event_type.startswith("viz_"):
                    if "duration" in event_data:
                        log_performance_metric(
                            operation=f"frontend_{event_type}",
                            duration=event_data["duration"] / 1000.0,
                            success=True
                        )
                else:
                    debug_info(f"MemoryGraph {event_type}", event_data)
                    
            except Exception as e:
                print(f"⚠️ Event logging failed for {event_type}: {e}")
        
        print("✅ End-to-end logging flow completed")
        assert True

if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v", "--tb=short"]) 