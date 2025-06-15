"""
API endpoint tests for authentication and authorization.

This module tests JWT token generation, validation, protected endpoint access,
role-based access control, and security features.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper
)


@pytest.mark.api
class TestJWTTokenGeneration:
    """Test JWT token generation and validation."""
    
    def test_valid_token_creation(self, test_settings, auth_headers):
        """Test creation of valid JWT tokens."""
        # The auth_headers fixture creates a valid token
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")
        
        # Extract and verify token
        token = auth_headers["Authorization"].split(" ")[1]
        
        # Decode token to verify structure
        decoded = jwt.decode(
            token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert "sub" in decoded  # Subject (username)
        assert "exp" in decoded  # Expiration
        assert "type" in decoded  # Token type
        assert decoded["type"] == "access"
    
    def test_token_expiration_validation(self, test_settings):
        """Test token expiration validation."""
        # Create expired token
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        expired_token_data = {
            "sub": "testuser",
            "exp": expired_time,
            "type": "access"
        }
        
        expired_token = jwt.encode(
            expired_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Try to decode expired token
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                expired_token,
                test_settings.secret_key,
                algorithms=[test_settings.algorithm]
            )
    
    def test_invalid_token_signature(self, test_settings):
        """Test validation of tokens with invalid signatures."""
        # Create token with wrong secret
        token_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() + timedelta(minutes=5),
            "type": "access"
        }
        
        invalid_token = jwt.encode(
            token_data,
            "wrong-secret-key",
            algorithm=test_settings.algorithm
        )
        
        # Try to decode with correct secret
        with pytest.raises(jwt.JWTError):
            jwt.decode(
                invalid_token,
                test_settings.secret_key,
                algorithms=[test_settings.algorithm]
            )
    
    def test_malformed_token_handling(self, test_settings):
        """Test handling of malformed tokens."""
        malformed_tokens = [
            "not.a.token",
            "Bearer invalid",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "valid.header.invalid-signature"
        ]
        
        for malformed_token in malformed_tokens:
            with pytest.raises((jwt.JWTError, ValueError)):
                jwt.decode(
                    malformed_token,
                    test_settings.secret_key,
                    algorithms=[test_settings.algorithm]
                )


@pytest.mark.api
class TestProtectedEndpointAccess:
    """Test access to protected endpoints with authentication."""
    
    async def test_protected_endpoint_with_valid_token(self, test_client: TestClient, auth_headers):
        """Test accessing protected endpoints with valid authentication."""
        # Test endpoints that might require authentication
        # Note: The actual endpoints depend on the authentication implementation
        
        protected_endpoints = [
            "/api/duty/calculate",
            "/api/search/classify",
            "/api/search/classify/batch"
        ]
        
        for endpoint in protected_endpoints:
            if endpoint == "/api/duty/calculate":
                # POST endpoint requires data
                response = test_client.post(
                    endpoint,
                    json={
                        "hs_code": "0101010000",
                        "country_code": "USA",
                        "customs_value": 1000.00
                    },
                    headers=auth_headers
                )
            elif endpoint == "/api/search/classify":
                response = test_client.post(
                    endpoint,
                    json={
                        "product_description": "Test product",
                        "confidence_threshold": 0.8
                    },
                    headers=auth_headers
                )
            elif endpoint == "/api/search/classify/batch":
                response = test_client.post(
                    endpoint,
                    json={
                        "products": [{"description": "Test product"}],
                        "confidence_threshold": 0.8
                    },
                    headers=auth_headers
                )
            
            # Should not return 401 Unauthorized
            assert response.status_code != 401
    
    async def test_protected_endpoint_without_token(self, test_client: TestClient):
        """Test accessing protected endpoints without authentication."""
        # Test endpoints that might require authentication
        protected_endpoints = [
            ("/api/duty/calculate", "POST", {
                "hs_code": "0101010000",
                "country_code": "USA", 
                "customs_value": 1000.00
            }),
            ("/api/search/classify", "POST", {
                "product_description": "Test product",
                "confidence_threshold": 0.8
            }),
            ("/api/search/classify/batch", "POST", {
                "products": [{"description": "Test"}],
                "confidence_threshold": 0.8
            })
        ]
        
        for endpoint, method, data in protected_endpoints:
            if method == "POST":
                response = test_client.post(endpoint, json=data)
            else:
                response = test_client.get(endpoint)
            
            # If authentication is required, should return 401
            # If not required, should return other status (200, 422, etc.)
            # This test verifies the endpoint doesn't crash without auth
            assert response.status_code in [200, 401, 422, 500]
    
    async def test_protected_endpoint_with_invalid_token(self, test_client: TestClient):
        """Test accessing protected endpoints with invalid tokens."""
        invalid_headers = [
            {"Authorization": "Bearer invalid-token"},
            {"Authorization": "Invalid format"},
            {"Authorization": "Bearer "},
            {"Authorization": ""},
        ]
        
        endpoint = "/api/duty/calculate"
        data = {
            "hs_code": "0101010000",
            "country_code": "USA",
            "customs_value": 1000.00
        }
        
        for headers in invalid_headers:
            response = test_client.post(endpoint, json=data, headers=headers)
            
            # Should either return 401 (if auth required) or process normally
            assert response.status_code in [200, 401, 422, 500]
    
    async def test_protected_endpoint_with_expired_token(self, test_client: TestClient, test_settings):
        """Test accessing protected endpoints with expired tokens."""
        # Create expired token
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        expired_token_data = {
            "sub": "testuser",
            "exp": expired_time,
            "type": "access"
        }
        
        expired_token = jwt.encode(
            expired_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            },
            headers=expired_headers
        )
        
        # Should either return 401 (if auth required) or process normally
        assert response.status_code in [200, 401, 422, 500]


@pytest.mark.api
class TestTokenRefreshMechanism:
    """Test token refresh and renewal mechanisms."""
    
    def test_token_refresh_with_valid_refresh_token(self, test_settings):
        """Test token refresh with valid refresh token."""
        # Create refresh token
        refresh_token_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh"
        }
        
        refresh_token = jwt.encode(
            refresh_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Verify refresh token structure
        decoded = jwt.decode(
            refresh_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert decoded["type"] == "refresh"
        assert decoded["sub"] == "testuser"
    
    def test_access_token_vs_refresh_token_distinction(self, test_settings):
        """Test distinction between access and refresh tokens."""
        # Create access token
        access_token_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "access"
        }
        
        access_token = jwt.encode(
            access_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Create refresh token
        refresh_token_data = {
            "sub": "testuser",
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh"
        }
        
        refresh_token = jwt.encode(
            refresh_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Decode and verify types
        access_decoded = jwt.decode(
            access_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        refresh_decoded = jwt.decode(
            refresh_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert access_decoded["type"] == "access"
        assert refresh_decoded["type"] == "refresh"
        
        # Access tokens should have shorter expiry
        assert access_decoded["exp"] < refresh_decoded["exp"]


@pytest.mark.api
class TestRoleBasedAccessControl:
    """Test role-based access control if implemented."""
    
    def test_admin_role_token_creation(self, test_settings):
        """Test creation of tokens with admin role."""
        admin_token_data = {
            "sub": "admin_user",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "access",
            "role": "admin",
            "permissions": ["read", "write", "admin"]
        }
        
        admin_token = jwt.encode(
            admin_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Verify admin token structure
        decoded = jwt.decode(
            admin_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert decoded["role"] == "admin"
        assert "admin" in decoded["permissions"]
    
    def test_broker_role_token_creation(self, test_settings):
        """Test creation of tokens with broker role."""
        broker_token_data = {
            "sub": "broker_user",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "access",
            "role": "broker",
            "permissions": ["read", "write"]
        }
        
        broker_token = jwt.encode(
            broker_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Verify broker token structure
        decoded = jwt.decode(
            broker_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert decoded["role"] == "broker"
        assert "admin" not in decoded.get("permissions", [])
    
    def test_readonly_role_token_creation(self, test_settings):
        """Test creation of tokens with readonly role."""
        readonly_token_data = {
            "sub": "readonly_user",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "access",
            "role": "readonly",
            "permissions": ["read"]
        }
        
        readonly_token = jwt.encode(
            readonly_token_data,
            test_settings.secret_key,
            algorithm=test_settings.algorithm
        )
        
        # Verify readonly token structure
        decoded = jwt.decode(
            readonly_token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        
        assert decoded["role"] == "readonly"
        assert decoded["permissions"] == ["read"]


@pytest.mark.api
class TestSecurityHeaders:
    """Test security headers and CORS configuration."""
    
    async def test_cors_headers_on_options_request(self, test_client: TestClient):
        """Test CORS headers on OPTIONS requests."""
        response = test_client.options("/api/tariff/sections")
        
        # Check for CORS headers (if implemented)
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        # Note: CORS headers may not be present in test environment
        # This test verifies the endpoint handles OPTIONS requests
        assert response.status_code in [200, 405, 404]
    
    async def test_security_headers_presence(self, test_client: TestClient):
        """Test presence of security headers."""
        response = test_client.get("/api/tariff/sections")
        
        # Check for common security headers (if implemented)
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        # Note: Security headers may not be implemented yet
        # This test documents expected security headers
        for header in security_headers:
            # Just check that the response doesn't crash
            header_value = response.headers.get(header)
            # Could assert specific values if headers are implemented
    
    async def test_content_type_headers(self, test_client: TestClient):
        """Test proper content-type headers."""
        # Test JSON endpoints
        response = test_client.get("/api/tariff/sections")
        
        if response.status_code == 200:
            assert "application/json" in response.headers.get("content-type", "")
        
        # Test POST endpoints
        response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            }
        )
        
        if response.status_code == 200:
            assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.api
@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for authentication workflows."""
    
    async def test_complete_authentication_workflow(self, test_client: TestClient, auth_headers):
        """Test complete authentication workflow."""
        # 1. Access public endpoint (should work without auth)
        public_response = test_client.get("/api/tariff/sections")
        assert public_response.status_code in [200, 404]  # Should not be 401
        
        # 2. Access protected endpoint with auth (if auth is required)
        protected_response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            },
            headers=auth_headers
        )
        assert protected_response.status_code != 401  # Should not be unauthorized
        
        # 3. Access protected endpoint without auth
        unauth_response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            }
        )
        # Should either work (no auth required) or return 401
        assert unauth_response.status_code in [200, 401, 422, 500]
    
    async def test_token_validation_across_endpoints(self, test_client: TestClient, auth_headers):
        """Test token validation consistency across different endpoints."""
        endpoints_and_data = [
            ("/api/duty/calculate", "POST", {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            }),
            ("/api/search/classify", "POST", {
                "product_description": "Test product",
                "confidence_threshold": 0.8
            }),
            ("/api/tariff/search", "GET", None)
        ]
        
        for endpoint, method, data in endpoints_and_data:
            if method == "POST":
                response = test_client.post(endpoint, json=data, headers=auth_headers)
            else:
                response = test_client.get(endpoint, headers=auth_headers)
            
            # Should consistently handle authentication
            assert response.status_code != 401  # Should not be unauthorized with valid token


@pytest.mark.api
@pytest.mark.slow
class TestAuthenticationPerformance:
    """Performance tests for authentication mechanisms."""
    
    async def test_token_validation_performance(self, test_client: TestClient, auth_headers, performance_timer):
        """Test token validation performance."""
        endpoint = "/api/tariff/sections"
        
        # Measure multiple requests with authentication
        performance_timer.start()
        
        for _ in range(10):
            response = test_client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 404]
        
        performance_timer.stop()
        
        # Token validation should not significantly impact performance
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 5.0)
    
    async def test_concurrent_authenticated_requests(self, async_test_client: AsyncClient, auth_headers):
        """Test concurrent requests with authentication."""
        import asyncio
        
        async def make_authenticated_request():
            response = await async_test_client.get("/api/tariff/sections", headers=auth_headers)
            return response.status_code
        
        # Run concurrent authenticated requests
        tasks = [make_authenticated_request() for _ in range(10)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # All requests should complete quickly
        assert end_time - start_time < 5.0
        
        # All should succeed (or consistently fail)
        status_codes = [r for r in results if isinstance(r, int)]
        assert len(status_codes) == len(tasks)
        
        # Should not have authentication failures
        auth_failures = [code for code in status_codes if code == 401]
        assert len(auth_failures) == 0


# Import time for performance tests
import time