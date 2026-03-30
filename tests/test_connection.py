#!/usr/bin/env python3
"""
Test script to verify Gotify MCP server connection using HTTP transport.
"""

import asyncio
import httpx
import json
import sys

async def test_mcp_connection():
    """Test connection to the MCP server using HTTP transport."""
    
    # MCP server URL
    server_url = "http://localhost:9158"
    
    print(f"Testing connection to MCP server at {server_url}")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test 1: Check if server is responding
            print("1. Testing HTTP endpoint...")
            response = await client.post(
                server_url,
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    },
                    "id": 1
                }
            )
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("   ✓ Server is responding on HTTP transport")
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"   ✗ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                
            # Test 2: Check health endpoint
            print("\n2. Testing health endpoint...")
            health_response = await client.get(f"{server_url}/health")
            print(f"   Status: {health_response.status_code}")
            if health_response.status_code == 200:
                print("   ✓ Health endpoint is accessible")
                print(f"   Response: {health_response.json()}")
            else:
                print(f"   ✗ Health endpoint returned: {health_response.status_code}")
                
    except httpx.ConnectError as e:
        print(f"✗ Connection failed: {e}")
        print("  Make sure the MCP server is running on port 9158")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Connection test completed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)