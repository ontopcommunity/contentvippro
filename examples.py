#!/usr/bin/env python3
"""
Example: Integrating ContentVIP Pro with Render proxy API.

This script demonstrates how to use the integration module to:
1. Fetch proxies from the Render API
2. Create campaigns
3. Monitor campaign status
"""

import json
from integration import ContentVIPProIntegration


def example_basic_usage():
    """
    Basic example: Create a campaign and fetch proxies.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Campaign Creation")
    print("="*60)
    
    integrator = ContentVIPProIntegration(
        render_url="https://contentvippro.onrender.com",
        render_key="rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa"
    )
    
    # Check service health
    if not integrator.health_check():
        print("❌ Render service is not available. Please deploy first.")
        return
    
    target_url = "https://www.tiktok.com/@example/video/123456789"
    view_count = 2500
    
    # Create campaign
    print(f"\n📝 Creating campaign for: {target_url}")
    print(f"📊 Target views: {view_count}")
    
    campaign = integrator.create_campaign(
        target_url=target_url,
        view_count=view_count,
        campaign_name="Example Campaign 1",
    )
    
    if campaign:
        print("\n✅ Campaign created successfully!")
        print(json.dumps(campaign, indent=2))
        campaign_id = campaign.get("job_id")
        print(f"\n🆔 Campaign ID: {campaign_id}")
    else:
        print("\n❌ Failed to create campaign")
    
    integrator.close()


def example_with_proxies():
    """
    Example: Fetch proxies and create campaign.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Campaign with Proxy Fetching")
    print("="*60)
    
    integrator = ContentVIPProIntegration()
    
    if not integrator.health_check():
        print("❌ Service unavailable")
        return
    
    target_url = "https://www.tiktok.com/@creator/video/987654321"
    view_count = 5000
    
    print(f"\n🔄 Step 1: Fetch proxies for {target_url}")
    proxies = integrator.fetch_proxies(
        target_url=target_url,
        view_count=view_count
    )
    
    print(f"✅ Fetched {len(proxies)} proxies:")
    for i, proxy in enumerate(proxies[:3], 1):
        print(f"   {i}. {proxy}")
    if len(proxies) > 3:
        print(f"   ... and {len(proxies) - 3} more")
    
    print(f"\n🔄 Step 2: Create campaign with fetched proxies")
    campaign = integrator.create_campaign(
        target_url=target_url,
        view_count=view_count,
        campaign_name="Example Campaign 2",
        metadata={"proxy_count": len(proxies), "source": "render_api"}
    )
    
    if campaign:
        print("\n✅ Campaign created with proxies!")
        print(json.dumps(campaign, indent=2))
    
    integrator.close()


def example_batch_campaigns():
    """
    Example: Create multiple campaigns in batch.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Campaign Creation")
    print("="*60)
    
    integrator = ContentVIPProIntegration()
    
    if not integrator.health_check():
        print("❌ Service unavailable")
        return
    
    # Sample TikTok URLs and view targets
    campaigns_config = [
        {
            "url": "https://www.tiktok.com/@user1/video/111111",
            "views": 1000,
            "name": "Campaign A"
        },
        {
            "url": "https://www.tiktok.com/@user2/video/222222",
            "views": 2500,
            "name": "Campaign B"
        },
        {
            "url": "https://www.tiktok.com/@user3/video/333333",
            "views": 5000,
            "name": "Campaign C"
        },
    ]
    
    print(f"\n📊 Creating {len(campaigns_config)} campaigns...\n")
    
    campaign_ids = []
    for config in campaigns_config:
        print(f"  ➤ {config['name']}: {config['url'][:50]}... ({config['views']} views)")
        
        campaign = integrator.create_campaign(
            target_url=config["url"],
            view_count=config["views"],
            campaign_name=config["name"],
        )
        
        if campaign:
            campaign_ids.append(campaign.get("job_id"))
            print(f"    ✅ Created: {campaign.get('job_id')}")
        else:
            print(f"    ❌ Failed")
    
    print(f"\n✅ Batch complete! Created {len(campaign_ids)} campaigns")
    print(f"📋 Campaign IDs: {campaign_ids}")
    
    integrator.close()


def example_status_check():
    """
    Example: Check campaign status.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Campaign Status Monitoring")
    print("="*60)
    
    integrator = ContentVIPProIntegration()
    
    if not integrator.health_check():
        print("❌ Service unavailable")
        return
    
    # First create a campaign
    print("\n📝 Creating a test campaign...")
    campaign = integrator.create_campaign(
        target_url="https://www.tiktok.com/@test/video/999999",
        view_count=3000,
        campaign_name="Status Check Test",
    )
    
    if not campaign:
        print("❌ Failed to create campaign")
        integrator.close()
        return
    
    campaign_id = campaign.get("job_id")
    print(f"✅ Campaign created: {campaign_id}")
    
    # Check status
    print(f"\n🔍 Checking campaign status...")
    status = integrator.get_campaign_status(campaign_id)
    
    if status:
        print("✅ Status retrieved:")
        print(json.dumps(status, indent=2))
    else:
        print("⚠️  Could not retrieve status (endpoint may not be implemented yet)")
    
    integrator.close()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# ContentVIP Pro - Render Integration Examples")
    print("#"*60)
    
    try:
        # Run examples
        example_basic_usage()
        example_with_proxies()
        example_batch_campaigns()
        example_status_check()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    
    print("\n" + "#"*60)
    print("# Examples Complete")
    print("#"*60 + "\n")
