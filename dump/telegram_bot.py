from utils import TelegramConfig
import requests
import random
import time

def main():
    # Example configuration
    telegram_config = TelegramConfig("@Mvcslog", "bot7172672222:AAFqGCbZgQC-ch4KXl7NhfBkTS8OoGq-35E", 150)
    
    while True:
        # Generate a random float value every 10 seconds
        random_value = random.uniform(0, 500)  # Adjust the range as needed
        
        # Check if the random value exceeds the threshold
        if random_value > telegram_config.threshold:
            # Send alert to Telegram every second
            for _ in range(10):
                print("Random value:", random_value)
                print("Above threshold, alert sent.")
                send_telegram_alert(telegram_config, random_value)
                time.sleep(1)  # Wait for 1 second before sending the next alert
        else:
            print("Random value:", random_value)
            print("Below threshold, no alert sent.")
        
        # Wait for 10 seconds before generating the next random value
        time.sleep(10)
def send_telegram_alert(config, value):
    # Telegram API endpoint for sending messages
    url = f"https://api.telegram.org/{config.telegram_bot_id}/sendMessage"
    
    # Message to send
    message = f"Alert! Random value ({value}) exceeded the threshold ({config.threshold})!"
    
    # Parameters for the API request
    params = {
        "chat_id": config.telegram_chat_id,
        "text": message
    }
    
    # Send the alert
    response = requests.post(url, params=params)
    if response.status_code != 200:
        print("Failed to send alert to Telegram:", response.text)

if __name__ == "__main__":
    main()


