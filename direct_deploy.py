#!/usr/bin/env python3
"""
Direct deployment to Render.com using your API key
"""
import requests
import json
import time

# Your Render API key
API_KEY = "rnd_IfLkNEeR0FHx4nzccAfwPd51axvY"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def deploy_now():
    """Deploy the arcade to Render"""
    print("🚀 Starting direct deployment to Render...")
    
    # First, get owner ID
    print("Getting owner information...")
    try:
        owners_response = requests.get(f"{BASE_URL}/owners", headers=headers)
        if owners_response.status_code == 200:
            owners = owners_response.json()
            if owners and len(owners) > 0:
                owner_id = owners[0]['id']
                print(f"✅ Found owner ID: {owner_id}")
            else:
                print("❌ No owners found")
                return False
        else:
            print(f"❌ Failed to get owners: {owners_response.status_code}")
            print(f"Response: {owners_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting owners: {e}")
        return False
    
    # Create the web service
    print("Creating web service...")
    service_data = {
        "type": "web_service",
        "name": "satoshis-arcade-mcp",
        "repo": "https://github.com/polydeuces32/satoshis-arcade-mcp",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "ownerId": owner_id,
        "healthCheckPath": "/health",
        "autoDeploy": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/services", headers=headers, json=service_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            service = response.json()
            print(f"🎉 SUCCESS! Service created!")
            print(f"Service ID: {service['id']}")
            print(f"🔗 Your arcade will be live at:")
            print(f"https://satoshis-arcade-mcp.onrender.com")
            print(f"\n⏱️  Deployment will take 5-10 minutes")
            print(f"📊 Monitor at: https://dashboard.render.com")
            return True
        else:
            print(f"❌ Failed to create service")
            return False
            
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        return False

if __name__ == "__main__":
    success = deploy_now()
    if success:
        print("\n🎮 Your arcade is being deployed!")
        print("Check https://dashboard.render.com for progress")
    else:
        print("\n❌ Deployment failed")
        print("Try the manual method at https://dashboard.render.com")
