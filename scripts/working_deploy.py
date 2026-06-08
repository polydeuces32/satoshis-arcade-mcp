#!/usr/bin/env python3
"""
Working deployment script for Render.com
"""
import requests
import json

API_KEY = "rnd_IfLkNEeR0FHx4nzccAfwPd51axvY"
BASE_URL = "https://api.render.com/v1"
OWNER_ID = "tea-d3m3ah3ipnbc73af5njg"  # From the curl response

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def deploy_arcade():
    print("🚀 Deploying Satoshi's Arcade MCP to Render...")
    print("=" * 50)
    
    service_data = {
        "type": "web_service",
        "name": "satoshis-arcade-mcp",
        "repo": "https://github.com/polydeuces32/satoshis-arcade-mcp",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "ownerId": OWNER_ID,
        "healthCheckPath": "/health",
        "autoDeploy": True
    }
    
    print("Creating web service...")
    print(f"Repository: {service_data['repo']}")
    print(f"Owner ID: {OWNER_ID}")
    
    try:
        response = requests.post(f"{BASE_URL}/services", headers=headers, json=service_data)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            service = response.json()
            print(f"\n🎉 SUCCESS! Arcade deployed!")
            print(f"Service ID: {service['id']}")
            print(f"\n🔗 Your arcade is live at:")
            print(f"https://satoshis-arcade-mcp.onrender.com")
            print(f"\n📊 Monitor deployment at:")
            print(f"https://dashboard.render.com")
            print(f"\n⏱️  Deployment takes 5-10 minutes")
            return True
        else:
            print(f"\n❌ Deployment failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    deploy_arcade()
