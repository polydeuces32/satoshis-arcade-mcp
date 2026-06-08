#!/usr/bin/env python3
"""
Deploy Satoshi's Arcade MCP to Render.com using the API
"""
import requests
import json
import time

# Render API configuration
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
                owner_id = owners[0]['id']
                print(f"Found owner ID: {owner_id}")
                return owner_id
        print(f"Failed to get owner ID: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error getting owner ID: {e}")
        return None

def create_web_service(owner_id):
    """Create a new web service on Render"""
    
    # Service configuration
    service_data = {
        "type": "web_service",
        "name": "satoshis-arcade-mcp",
        "repo": "https://github.com/polydeuces32/satoshis-arcade-mcp",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "ownerId": owner_id
    }
    
    print("Creating web service on Render...")
    print(f"Service name: {service_data['name']}")
    print(f"Repository: {service_data['repo']}")
    
    try:
        response = requests.post(
            f"{RENDER_API_BASE}/services",
            headers=headers,
            json=service_data
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            service = response.json()
            print(f"✅ Service created successfully!")
            print(f"Service ID: {service['id']}")
            return service
        else:
            print(f"❌ Failed to create service: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        return None

def main():
    print("🚀 Deploying Satoshi's Arcade MCP to Render.com")
    print("=" * 50)
    
    # Get owner ID first
    print("Getting owner ID...")
    owner_id = get_owner_id()
    
    if not owner_id:
        print("❌ Could not get owner ID. Please check your API key.")
        return
    
    # Create the web service
    service = create_web_service(owner_id)
    
    if service:
        print(f"\n🔗 Your arcade will be available at:")
        print(f"https://satoshis-arcade-mcp.onrender.com")
        print(f"\n📝 You can monitor the deployment in your Render dashboard:")
        print(f"https://dashboard.render.com")
        
    else:
        print("❌ Deployment failed. Please check your API key and try again.")

if __name__ == "__main__":
    main()
