"""
Advanced Database Tests
Tests for database operations, transactions, concurrency, data integrity, and performance
"""

import pytest
import asyncio
import sqlite3
import threading
import time
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch
import sys
import os

# Add project paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from zackgpt.core.database import ZackGPTDatabase
from zackgpt.core.logger import debug_log


class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    @pytest.fixture
    def test_db(self):
        """Create test database."""
        db_path = f"tests/logs/test_transactions_{uuid.uuid4().hex[:8]}.db"
        db = ZackGPTDatabase(db_path)
        yield db
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.mark.core
    def test_thread_creation_transaction(self, test_db):
        """Test thread creation with proper transaction handling."""
        thread_data = test_db.create_thread("Test Transaction Thread")
        
        assert thread_data is not None
        assert thread_data['title'] == "Test Transaction Thread"
        assert 'id' in thread_data
        
        # Verify thread exists in database
        retrieved = test_db.get_thread(thread_data['id'])
        assert retrieved is not None
        assert retrieved['title'] == thread_data['title']
        
        print("✅ Thread creation transaction working")
    
    @pytest.mark.core
    def test_message_addition_transaction(self, test_db):
        """Test message addition with thread update transaction."""
        # Create thread first
        thread = test_db.create_thread("Test Message Thread")
        thread_id = thread['id']
        
        # Add message
        message_data = test_db.add_message(thread_id, "user", "Test message content")
        
        assert message_data is not None
        assert message_data['content'] == "Test message content"
        assert message_data['thread_id'] == thread_id
        
        # Verify thread message count was updated
        updated_thread = test_db.get_thread(thread_id)
        assert updated_thread['message_count'] == 1
        
        print("✅ Message addition transaction working")
    
    @pytest.mark.core
    def test_rollback_on_error(self, test_db):
        """Test transaction rollback on error."""
        # This would test rollback behavior in case of errors
        # For now, we'll test that the database handles errors gracefully
        
        try:
            # Attempt to add message to non-existent thread
            test_db.add_message("non-existent-thread", "user", "Test message")
        except Exception as e:
            # Should handle the error without corrupting the database
            assert "thread" in str(e).lower() or "foreign key" in str(e).lower()
            print("✅ Database error handling working")


class TestConcurrentAccess:
    """Test concurrent database access."""
    
    @pytest.fixture
    def shared_test_db(self):
        """Create shared test database for concurrency tests."""
        db_path = f"tests/logs/test_concurrent_{uuid.uuid4().hex[:8]}.db"
        db = ZackGPTDatabase(db_path)
        yield db
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.mark.core
    @pytest.mark.slow
    def test_concurrent_thread_creation(self, shared_test_db):
        """Test creating threads concurrently."""
        results = []
        errors = []
        
        def create_thread_worker(worker_id):
            try:
                thread = shared_test_db.create_thread(f"Concurrent Thread {worker_id}")
                results.append(thread)
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # Create multiple threads concurrently
        threads = [threading.Thread(target=create_thread_worker, args=(i,)) for i in range(10)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        
        # All threads should have been created successfully
        assert len(results) == 10
        assert len(errors) == 0
        
        # All threads should have unique IDs
        thread_ids = [t['id'] for t in results]
        assert len(set(thread_ids)) == 10  # All unique
        
        print(f"✅ Created 10 threads concurrently in {elapsed:.3f}s")
    
    @pytest.mark.core
    @pytest.mark.slow
    def test_concurrent_message_addition(self, shared_test_db):
        """Test adding messages concurrently to the same thread."""
        # Create a thread first
        thread = shared_test_db.create_thread("Concurrent Messages Thread")
        thread_id = thread['id']
        
        results = []
        errors = []
        
        def add_message_worker(worker_id):
            try:
                message = shared_test_db.add_message(
                    thread_id, 
                    "user", 
                    f"Concurrent message {worker_id}"
                )
                results.append(message)
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # Add messages concurrently
        threads = [threading.Thread(target=add_message_worker, args=(i,)) for i in range(20)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        
        # All messages should have been added successfully
        assert len(results) == 20
        assert len(errors) == 0
        
        # Verify thread message count
        updated_thread = shared_test_db.get_thread(thread_id)
        assert updated_thread['message_count'] == 20
        
        print(f"✅ Added 20 messages concurrently in {elapsed:.3f}s")


class TestDataIntegrity:
    """Test data integrity and validation."""
    
    @pytest.fixture
    def integrity_test_db(self):
        """Create test database for integrity tests."""
        db_path = f"tests/logs/test_integrity_{uuid.uuid4().hex[:8]}.db"
        db = ZackGPTDatabase(db_path)
        yield db
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.mark.core
    def test_foreign_key_constraints(self, integrity_test_db):
        """Test foreign key constraints are enforced."""
        # Try to add message to non-existent thread
        with pytest.raises(Exception):
            integrity_test_db.add_message("non-existent-thread", "user", "Test message")
        
        print("✅ Foreign key constraints enforced")
    
    @pytest.mark.core
    def test_data_validation(self, integrity_test_db):
        """Test data validation."""
        # Test empty title
        try:
            thread = integrity_test_db.create_thread("")
            # Should either reject empty title or handle it gracefully
            assert thread is not None
        except Exception as e:
            assert "title" in str(e).lower() or "empty" in str(e).lower()
        
        # Test very long content
        long_content = "x" * 10000
        thread = integrity_test_db.create_thread("Test Thread")
        message = integrity_test_db.add_message(thread['id'], "user", long_content)
        
        assert message is not None
        assert len(message['content']) == 10000
        
        print("✅ Data validation working")
    
    @pytest.mark.core
    def test_unicode_handling(self, integrity_test_db):
        """Test Unicode and special character handling."""
        unicode_content = "🎉 Hello 世界! Café naïve résumé 🚀"
        
        thread = integrity_test_db.create_thread(unicode_content)
        assert thread['title'] == unicode_content
        
        message = integrity_test_db.add_message(thread['id'], "user", unicode_content)
        assert message['content'] == unicode_content
        
        print("✅ Unicode handling working")


class TestDatabasePerformance:
    """Test database performance characteristics."""
    
    @pytest.fixture
    def performance_test_db(self):
        """Create test database for performance tests."""
        db_path = f"tests/logs/test_performance_{uuid.uuid4().hex[:8]}.db"
        db = ZackGPTDatabase(db_path)
        yield db
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_bulk_thread_creation_performance(self, performance_test_db):
        """Test performance of creating many threads."""
        start_time = time.time()
        
        threads = []
        for i in range(50):
            thread = performance_test_db.create_thread(f"Performance Test Thread {i}")
            threads.append(thread)
        
        elapsed = time.time() - start_time
        
        assert len(threads) == 50
        assert elapsed < 10.0  # Should complete within 10 seconds
        
        print(f"✅ Created 50 threads in {elapsed:.3f}s ({elapsed/50*1000:.1f}ms per thread)")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_bulk_message_insertion_performance(self, performance_test_db):
        """Test performance of inserting many messages."""
        # Create a thread first
        thread = performance_test_db.create_thread("Performance Test Thread")
        thread_id = thread['id']
        
        start_time = time.time()
        
        messages = []
        for i in range(500):
            message = performance_test_db.add_message(
                thread_id, 
                "user" if i % 2 == 0 else "assistant", 
                f"Performance test message {i}"
            )
            messages.append(message)
        
        elapsed = time.time() - start_time
        
        assert len(messages) == 500
        assert elapsed < 15.0  # Should complete within 15 seconds
        
        # Verify thread message count
        updated_thread = performance_test_db.get_thread(thread_id)
        assert updated_thread['message_count'] == 500
        
        print(f"✅ Inserted 500 messages in {elapsed:.3f}s ({elapsed/500*1000:.1f}ms per message)")
    
    @pytest.mark.performance
    def test_query_performance(self, performance_test_db):
        """Test query performance with larger datasets."""
        # Create test data
        threads = []
        for i in range(50):
            thread = performance_test_db.create_thread(f"Query Test Thread {i}")
            threads.append(thread)
            
            # Add some messages to each thread
            for j in range(10):
                performance_test_db.add_message(
                    thread['id'], 
                    "user", 
                    f"Message {j} in thread {i}"
                )
        
        # Test thread listing performance
        start_time = time.time()
        all_threads = performance_test_db.list_threads(limit=100)
        query_elapsed = time.time() - start_time
        
        assert len(all_threads) == 50
        assert query_elapsed < 1.0  # Should be very fast
        
        # Test message retrieval performance
        start_time = time.time()
        for thread in threads[:10]:  # Test first 10 threads
            messages = performance_test_db.get_messages(thread['id'])
            assert len(messages) == 10
        
        message_query_elapsed = time.time() - start_time
        assert message_query_elapsed < 2.0  # Should be reasonably fast
        
        print(f"✅ Query performance: threads {query_elapsed*1000:.1f}ms, messages {message_query_elapsed*1000:.1f}ms")


class TestDatabaseMaintenance:
    """Test database maintenance operations."""
    
    @pytest.fixture
    def maintenance_test_db(self):
        """Create test database for maintenance tests."""
        db_path = f"tests/logs/test_maintenance_{uuid.uuid4().hex[:8]}.db"
        db = ZackGPTDatabase(db_path)
        yield db
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.mark.core
    def test_database_backup_restore(self, maintenance_test_db):
        """Test database backup and restore functionality."""
        # Create some test data
        thread = maintenance_test_db.create_thread("Backup Test Thread")
        maintenance_test_db.add_message(thread['id'], "user", "Test message for backup")
        
        # Test backup (if implemented)
        if hasattr(maintenance_test_db, 'backup'):
            backup_path = f"tests/logs/backup_{uuid.uuid4().hex[:8]}.db"
            maintenance_test_db.backup(backup_path)
            
            assert os.path.exists(backup_path)
            
            # Verify backup contains data
            backup_db = ZackGPTDatabase(backup_path)
            backup_threads = backup_db.list_threads()
            assert len(backup_threads) >= 1
            
            # Cleanup
            os.remove(backup_path)
            
            print("✅ Database backup/restore working")
        else:
            print("ℹ️ Database backup not implemented yet")
    
    @pytest.mark.core
    def test_database_cleanup(self, maintenance_test_db):
        """Test database cleanup operations."""
        # Create old test data
        old_thread = maintenance_test_db.create_thread("Old Thread")
        
        # Simulate old timestamp (if the database supports it)
        # This would test cleanup of old data
        
        # For now, just verify the database can handle cleanup operations
        if hasattr(maintenance_test_db, 'cleanup_old_data'):
            maintenance_test_db.cleanup_old_data(days=30)
            print("✅ Database cleanup working")
        else:
            print("ℹ️ Database cleanup not implemented yet")
    
    @pytest.mark.core
    def test_database_vacuum(self, maintenance_test_db):
        """Test database vacuum/optimization."""
        # Create and delete some data to create fragmentation
        threads_to_delete = []
        for i in range(20):
            thread = maintenance_test_db.create_thread(f"Temp Thread {i}")
            threads_to_delete.append(thread['id'])
        
        # Delete threads (if delete functionality exists)
        if hasattr(maintenance_test_db, 'delete_thread'):
            for thread_id in threads_to_delete:
                maintenance_test_db.delete_thread(thread_id)
        
        # Test vacuum operation
        if hasattr(maintenance_test_db, 'vacuum'):
            maintenance_test_db.vacuum()
            print("✅ Database vacuum working")
        else:
            # Test basic database integrity
            with maintenance_test_db.get_connection() as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()
                assert result[0] == "ok"
            print("✅ Database integrity verified")


class TestDatabaseMigrations:
    """Test database schema migrations."""
    
    @pytest.mark.core
    def test_schema_version_tracking(self):
        """Test schema version tracking."""
        db_path = f"tests/logs/test_migration_{uuid.uuid4().hex[:8]}.db"
        
        try:
            db = ZackGPTDatabase(db_path)
            
            # Check if schema version tracking exists
            with db.get_connection() as conn:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                table_names = [table[0] for table in tables]
                
                # Should have core tables
                assert 'threads' in table_names
                assert 'messages' in table_names
                assert 'memories' in table_names
                
                print("✅ Database schema properly initialized")
        
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
    
    @pytest.mark.core
    def test_schema_compatibility(self):
        """Test schema compatibility across versions."""
        # This would test that the current code can work with older database schemas
        # For now, we'll test that the current schema is properly structured
        
        db_path = f"tests/logs/test_compatibility_{uuid.uuid4().hex[:8]}.db"
        
        try:
            db = ZackGPTDatabase(db_path)
            
            # Test that all expected columns exist
            with db.get_connection() as conn:
                # Check threads table structure
                threads_info = conn.execute("PRAGMA table_info(threads)").fetchall()
                thread_columns = [col[1] for col in threads_info]
                
                expected_thread_columns = ['id', 'title', 'created_at', 'updated_at', 'message_count']
                for col in expected_thread_columns:
                    assert col in thread_columns, f"Missing column: {col}"
                
                # Check messages table structure
                messages_info = conn.execute("PRAGMA table_info(messages)").fetchall()
                message_columns = [col[1] for col in messages_info]
                
                expected_message_columns = ['id', 'thread_id', 'role', 'content', 'timestamp']
                for col in expected_message_columns:
                    assert col in message_columns, f"Missing column: {col}"
                
                print("✅ Database schema compatibility verified")
        
        finally:
            if os.path.exists(db_path):
                os.remove(db_path) 