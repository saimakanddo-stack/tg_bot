# webhook_rotator.py
import requests
import schedule
import time
from datetime import datetime
from config import BOT_TOKEN

# Webhook URLs for different services
SERVICES = {
    'cyclic': 'https://telegram-bot-cyclic.cyclic.app',
    'koyeb': 'https://telegram-bot-koyeb.app',
    'railway': 'https://tgbot-production-b230.up.railway.app',
    'render': 'https://telegram-bot-render.onrender.com'
}

def set_webhook(service_name):
    """Webhook সেট করুন"""
    service_url = SERVICES.get(service_name)
    if not service_url:
        print(f"Service {service_name} not found!")
        return False
        
    webhook_url = f"{service_url}/{BOT_TOKEN}"
    
    try:
        # আগের webhook ডিলিট
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        
        # নতুন webhook সেট
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            json={'url': webhook_url}
        )
        
        if response.status_code == 200:
            print(f"[{datetime.now()}] ✓ Switched to {service_name}")
            return True
        else:
            print(f"[{datetime.now()}] ✗ Failed: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Error: {e}")
    
    return False

# শিডিউল সেটআপ (রোটেশন)
schedule.every().day.at("00:00").do(set_webhook, 'cyclic')
schedule.every().day.at("03:00").do(set_webhook, 'koyeb')
schedule.every().day.at("06:00").do(set_webhook, 'railway')
schedule.every().day.at("18:00").do(set_webhook, 'render')

print("Webhook rotation system started!")

# Main loop
while True:
    schedule.run_pending()
    time.sleep(60)

