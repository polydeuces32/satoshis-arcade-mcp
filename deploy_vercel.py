#!/usr/bin/env python3
"""
Deploy Satoshi's Arcade MCP to Vercel
"""
import subprocess
import os

def deploy_to_vercel():
    print("🚀 Deploying Satoshi's Arcade MCP to Vercel...")
    print("=" * 50)
    
    # Check if Vercel CLI is installed
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Vercel CLI not found. Installing...")
            subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first.")
        return False
    
    # Deploy to Vercel
    try:
        print("📦 Deploying to Vercel...")
        result = subprocess.run(['vercel', '--prod'], check=True, capture_output=True, text=True)
        
        print("✅ Deployment successful!")
        print(result.stdout)
        
        # Extract URL from output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                print(f"\n🎮 Your arcade is live at: {line.strip()}")
                break
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    deploy_to_vercel()
