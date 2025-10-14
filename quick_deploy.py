#!/usr/bin/env python3
"""
Quick deployment script for Satoshi's Arcade MCP to Render.com
"""
import requests
import json
import time

# Your Render API key
RENDER_API_KEY = "rnd_IfLkNEeR0FHx4nzccAfwPd51axvY"
RENDER_API_BASE = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

def get_owner_id():
    """Get the owner ID for the API key"""
    try:
        response = requests.get(f"{RENDER_API_BASE}/owners", headers=headers)
        if response.status_code == 200:
            owners = response.json()
            if owners:
                return owners[0]['id']
        print(f"Failed to get owner ID: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error getting owner ID: {e}")
        return None

def create_service(owner_id):
    """Create the web service"""
    service_data = {
        "type": "web_service",
        "name": "satoshis-arcade-mcp",
        "repo": "https://github.com/polydeuces32/satoshis-arcade-mcp",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "ownerId": owner_id,
        "healthCheckPath": "/health"
    }
    
    print("Creating web service...")
    response = requests.post(f"{RENDER_API_BASE}/services", headers=headers, json=service_data)
    
    if response.status_code == 201:
        service = response.json()
        print(f"✅ Service created successfully!")
        print(f"Service ID: {service['id']}")
        return service
    else:
        print(f"❌ Failed to create service: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    print("🚀 Deploying Satoshi's Arcade MCP to Render.com")
    print("=" * 50)
    
    # Get owner ID
    print("Getting owner ID...")
    owner_id = get_owner_id()
    if not owner_id:
        print("❌ Could not get owner ID")
        return
    
    # Create service
    service = create_service(owner_id)
    if service:
        print(f"\n🎉 Deployment initiated!")
        print(f"🔗 Your arcade will be available at:")
        print(f"https://satoshis-arcade-mcp.onrender.com")
        print(f"\n📊 Monitor deployment at:")
        print(f"https://dashboard.render.com")
        print(f"\n⏱️  Deployment typically takes 5-10 minutes")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
