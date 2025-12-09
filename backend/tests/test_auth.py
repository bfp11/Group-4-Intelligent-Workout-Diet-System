# backend/tests/test_auth.py
"""
Unit tests for authentication system (bcrypt + sessions)
Testing critical security components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import bcrypt
from main import (
    hash_password,
    verify_password,
    create_session,
    get_session,
    delete_session
)

class TestAuthentication:
    """Test suite for authentication and session management"""
    
    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing produces valid bcrypt hash"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed.startswith("$2b$")  # Bcrypt identifier
        assert len(hashed) == 60  # Standard bcrypt hash length
        assert hashed != password  # Not plain text
    
    def test_hash_password_different_hashes_same_password(self):
        """Test that same password produces different hashes (salt randomness)"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to random salt
    
    def test_verify_password_correct_password(self):
        """Test password verification succeeds with correct password"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_verify_password_incorrect_password(self):
        """Test password verification fails with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        assert result is False
    
    def test_verify_password_case_sensitive(self):
        """Test password verification is case-sensitive"""
        password = "TestPassword123"
        wrong_case = "testpassword123"
        hashed = hash_password(password)
        
        result = verify_password(wrong_case, hashed)
        assert result is False
    
    @patch('main.get_supabase_client')
    def test_create_session_generates_valid_token(self, mock_supabase):
        """Test session creation generates cryptographically secure token"""
        # Mock database
        mock_db = MagicMock()
        mock_db.table().insert().execute.return_value = MagicMock(data=[{"session_id": "test"}])
        mock_supabase.return_value = mock_db
        
        # Execute
        session_id = create_session("user-123", "testuser")
        
        # Verify
        assert session_id is not None
        assert len(session_id) >= 32  # Sufficient entropy
        assert isinstance(session_id, str)
        
        # Verify database call
        mock_db.table.assert_called_with('sessions')
        mock_db.table().insert.assert_called_once()
    
    @patch('main.get_supabase_client')
    def test_create_session_sets_correct_expiration(self, mock_supabase):
        """Test session expiration is set to 7 days from now"""
        # Mock database
        mock_db = MagicMock()
        captured_data = {}
        
        def capture_insert(data):
            captured_data.update(data)
            return mock_db
        
        mock_db.table().insert.side_effect = capture_insert
        mock_db.table().insert().execute.return_value = MagicMock(data=[{}])
        mock_supabase.return_value = mock_db
        
        # Execute
        before_time = datetime.now()
        session_id = create_session("user-123", "testuser")
        after_time = datetime.now()
        
        # Verify expiration is ~7 days from now
        expires_at = datetime.fromisoformat(captured_data["expires_at"])
        expected_expiration = datetime.now() + timedelta(days=7)
        
        # Allow 1 minute margin for test execution time
        assert abs((expires_at - expected_expiration).total_seconds()) < 60
    
    @patch('main.get_supabase_client')
    def test_get_session_valid_session(self, mock_supabase):
        """Test retrieving valid non-expired session"""
        # Mock database response with valid session
        future_time = datetime.now() + timedelta(days=5)
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(
            data=[{
                "session_id": "test-session-123",
                "user_id": "user-456",
                "expires_at": future_time.isoformat() + "Z",
                "users": {
                    "id": "user-456",
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }]
        )
        mock_supabase.return_value = mock_db
        
        # Execute
        result = get_session("test-session-123")
        
        # Verify
        assert result is not None
        assert result["user_id"] == "user-456"
        assert result["username"] == "Test User"
    
    @patch('main.get_supabase_client')
    def test_get_session_expired_session(self, mock_supabase):
        """Test expired session returns None and gets deleted"""
        # Mock database response with expired session
        past_time = datetime.now() - timedelta(days=1)
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(
            data=[{
                "session_id": "expired-session",
                "user_id": "user-456",
                "expires_at": past_time.isoformat() + "Z",
                "users": {"id": "user-456", "name": "Test User", "email": "test@example.com"}
            }]
        )
        mock_supabase.return_value = mock_db
        
        # Execute
        result = get_session("expired-session")
        
        # Verify
        assert result is None
        
        # Verify session was deleted
        mock_db.table().delete().eq.assert_called()
    
    @patch('main.get_supabase_client')
    def test_get_session_nonexistent_session(self, mock_supabase):
        """Test nonexistent session returns None"""
        # Mock empty database response
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Execute
        result = get_session("nonexistent-session")
        
        # Verify
        assert result is None
    
    def test_get_session_none_input(self):
        """Test None session ID returns None without database call"""
        result = get_session(None)
        assert result is None
    
    @patch('main.get_supabase_client')
    def test_delete_session_success(self, mock_supabase):
        """Test session deletion calls database correctly"""
        # Mock database
        mock_db = MagicMock()
        mock_supabase.return_value = mock_db
        
        # Execute
        delete_session("test-session-123")
        
        # Verify database call
        mock_db.table.assert_called_with('sessions')
        mock_db.table().delete().eq.assert_called()
    
    def test_delete_session_none_input(self):
        """Test deleting None session ID doesn't crash"""
        # Should not raise exception
        delete_session(None)
    
    @patch('main.get_supabase_client')
    def test_delete_session_handles_database_error(self, mock_supabase):
        """Test session deletion handles database errors gracefully"""
        # Mock database error
        mock_db = MagicMock()
        mock_db.table().delete().eq.side_effect = Exception("Database error")
        mock_supabase.return_value = mock_db
        
        # Execute - should not raise exception
        delete_session("test-session-123")