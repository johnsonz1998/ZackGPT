import pytest
import time
import asyncio
from src.zackgpt.core.logger import log_performance, PerformanceMetrics

@pytest.fixture
def perf_metrics():
    """Create a PerformanceMetrics instance."""
    return PerformanceMetrics()

def test_basic_performance_tracking(perf_metrics):
    """Test basic performance tracking functionality."""
    operation = "test_operation"
    
    # Start timing
    perf_metrics.start_timer(operation)
    time.sleep(0.1)  # Simulate work
    duration = perf_metrics.end_timer(operation)
    
    assert duration is not None
    assert duration >= 0.1
    assert duration < 0.2  # Should be close to 0.1

def test_nested_performance_tracking(perf_metrics):
    """Test nested performance tracking."""
    outer_op = "outer_operation"
    inner_op = "inner_operation"
    
    perf_metrics.start_timer(outer_op)
    time.sleep(0.1)
    
    perf_metrics.start_timer(inner_op)
    time.sleep(0.05)
    inner_duration = perf_metrics.end_timer(inner_op)
    
    outer_duration = perf_metrics.end_timer(outer_op)
    
    assert inner_duration >= 0.05
    assert outer_duration >= 0.15  # Should include inner operation time

def test_performance_decorator():
    """Test the performance logging decorator."""
    @log_performance("decorated_operation")
    def test_function():
        time.sleep(0.1)
        return "success"
    
    result = test_function()
    assert result == "success"

def test_async_performance_tracking():
    """Test performance tracking with async functions."""
    @log_performance("async_operation")
    async def async_function():
        await asyncio.sleep(0.1)
        return "async_success"
    
    result = asyncio.run(async_function())
    assert result == "async_success"

def test_performance_metrics_persistence(perf_metrics):
    """Test that performance metrics are properly stored."""
    operation = "persistent_operation"
    
    # Record multiple durations
    durations = []
    for _ in range(3):
        perf_metrics.start_timer(operation)
        time.sleep(0.1)
        duration = perf_metrics.end_timer(operation)
        durations.append(duration)
    
    # Verify all durations were recorded
    assert len(durations) == 3
    assert all(d >= 0.1 for d in durations)

def test_performance_error_handling(perf_metrics):
    """Test performance tracking with error handling."""
    operation = "error_operation"
    
    perf_metrics.start_timer(operation)
    try:
        raise ValueError("Test error")
    except ValueError:
        duration = perf_metrics.end_timer(operation)
        assert duration is not None

def test_concurrent_performance_tracking(perf_metrics):
    """Test performance tracking under concurrent load."""
    import threading
    
    def worker():
        for i in range(10):
            operation_name = f"concurrent_operation_{threading.current_thread().ident}_{i}"
            perf_metrics.start_timer(operation_name)
            time.sleep(0.01)
            duration = perf_metrics.end_timer(operation_name)
            assert duration is not None
            assert duration >= 0.005  # More lenient timing
    
    # Create multiple threads
    threads = [threading.Thread(target=worker) for _ in range(5)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def test_performance_metrics_aggregation(perf_metrics):
    """Test aggregation of performance metrics."""
    operation = "aggregated_operation"
    
    # Record multiple durations
    for _ in range(5):
        perf_metrics.start_timer(operation)
        time.sleep(0.1)
        perf_metrics.end_timer(operation)
    
    # Verify metrics were recorded
    assert operation in perf_metrics._metrics
    assert perf_metrics._metrics[operation]['duration'] is not None

def test_performance_decorator_with_args():
    """Test performance decorator with function arguments."""
    @log_performance("operation_with_args")
    def function_with_args(arg1, arg2, kwarg1=None):
        time.sleep(0.1)
        return arg1 + arg2 + (kwarg1 or 0)
    
    result = function_with_args(1, 2, kwarg1=3)
    assert result == 6

def test_performance_decorator_with_async_args():
    """Test performance decorator with async function arguments."""
    @log_performance("async_operation_with_args")
    async def async_function_with_args(arg1, arg2, kwarg1=None):
        await asyncio.sleep(0.1)
        return arg1 + arg2 + (kwarg1 or 0)
    
    result = asyncio.run(async_function_with_args(1, 2, kwarg1=3))
    assert result == 6 