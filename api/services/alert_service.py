"""
Multi-Channel Alert Service
Ensures subscribers never miss a signal
"""

import os
from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import telegram

class AlertService:
    """
    Handles multi-channel alert delivery:
    - Email (SendGrid)
    - SMS (Twilio)  
    - Telegram
    - Discord webhook
    - Push notifications (future)
    """
    
    def __init__(self):
        # Email setup
        self.sendgrid_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'signals@driftedge.com')
        
        # SMS setup  
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Telegram setup
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Discord webhook
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        
    async def send_new_signal_alert(self, signal: Dict, current_price: float):
        """
        Send new signal alert to all subscribers via all channels.
        """
        # Get active subscribers from database
        subscribers = await self.get_active_subscribers()
        
        # Prepare message content
        message_data = self.prepare_signal_message(signal, current_price)
        
        # Send via all channels in parallel
        tasks = []
        
        for subscriber in subscribers:
            if subscriber.get('email_enabled'):
                tasks.append(self.send_email(subscriber['email'], message_data))
            
            if subscriber.get('sms_enabled'):
                tasks.append(self.send_sms(subscriber['phone'], message_data))
                
            if subscriber.get('telegram_id'):
                tasks.append(self.send_telegram(subscriber['telegram_id'], message_data))
        
        # Send to Discord channel for all subscribers
        if self.discord_webhook:
            tasks.append(self.send_discord(message_data))
        
        # Execute all sends in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Alert delivery failed: {result}")
    
    def prepare_signal_message(self, signal: Dict, current_price: float) -> Dict:
        """
        Prepare message content for all channels.
        """
        direction_emoji = "📈" if signal['signal_direction'] == "LONG" else "📉"
        
        # Calculate stops and targets
        if signal['signal_direction'] == "LONG":
            stop_loss = round(current_price * 0.975, 2)
            take_profit = round(current_price * 1.018, 2)
        else:
            stop_loss = round(current_price * 1.025, 2)
            take_profit = round(current_price * 0.98, 2)
        
        return {
            'subject': f"{direction_emoji} New Signal: {signal['symbol']} {signal['signal_direction']}",
            'symbol': signal['symbol'],
            'direction': signal['signal_direction'],
            'current_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'sue_score': signal['sue_score'],
            'quintile': signal['quintile'],
            'surprise_pct': signal['surprise_pct'],
            'emoji': direction_emoji
        }
    
    async def send_email(self, to_email: str, data: Dict):
        """
        Send email alert via SendGrid.
        """
        try:
            html_content = f"""
            <h2>{data['emoji']} New Post-Earnings Signal</h2>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
                <h3>{data['symbol']} - {data['direction']}</h3>
                
                <p><strong>Entry Price:</strong> ${data['current_price']:.2f}</p>
                <p><strong>Stop Loss:</strong> ${data['stop_loss']:.2f} (-2.5%)</p>
                <p><strong>Take Profit:</strong> ${data['take_profit']:.2f} (+1.8%)</p>
                
                <hr>
                
                <p><strong>Signal Details:</strong></p>
                <ul>
                    <li>SUE Score: {data['sue_score']:.2f}</li>
                    <li>Quintile: Q{data['quintile']}</li>
                    <li>Earnings Surprise: {data['surprise_pct']:.1f}%</li>
                </ul>
                
                <p><strong>Expected Hold:</strong> 3-5 trading days</p>
                
                <hr>
                
                <p><em>This is a paper trading signal based on academic PEAD research. 
                Not financial advice. Historical win rate: 45-55%</em></p>
            </div>
            
            <p>View all signals: <a href="https://driftedge.com/dashboard">Dashboard</a></p>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=data['subject'],
                html_content=html_content
            )
            
            sg = SendGridAPIClient(self.sendgrid_key)
            response = await asyncio.to_thread(sg.send, message)
            print(f"Email sent to {to_email}: {response.status_code}")
            
        except Exception as e:
            print(f"Email send failed to {to_email}: {e}")
            raise
    
    async def send_sms(self, phone: str, data: Dict):
        """
        Send SMS alert via Twilio.
        """
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            
            # Short SMS format
            message_body = (
                f"{data['emoji']} DRIFT Signal\n"
                f"{data['symbol']} {data['direction']}\n"
                f"Entry: ${data['current_price']:.2f}\n"
                f"Stop: ${data['stop_loss']:.2f}\n"
                f"Target: ${data['take_profit']:.2f}\n"
                f"Check email for details"
            )
            
            message = await asyncio.to_thread(
                client.messages.create,
                body=message_body,
                from_=self.twilio_from,
                to=phone
            )
            
            print(f"SMS sent to {phone}: {message.sid}")
            
        except Exception as e:
            print(f"SMS send failed to {phone}: {e}")
            raise
    
    async def send_telegram(self, chat_id: str, data: Dict):
        """
        Send Telegram alert.
        """
        try:
            bot = telegram.Bot(token=self.telegram_token)
            
            message = (
                f"{data['emoji']} <b>New Signal: {data['symbol']}</b>\n\n"
                f"Direction: <b>{data['direction']}</b>\n"
                f"Entry: ${data['current_price']:.2f}\n"
                f"Stop Loss: ${data['stop_loss']:.2f}\n"
                f"Take Profit: ${data['take_profit']:.2f}\n\n"
                f"SUE Score: {data['sue_score']:.2f} (Q{data['quintile']})\n"
                f"Earnings Surprise: {data['surprise_pct']:.1f}%\n\n"
                f"Hold: 3-5 days"
            )
            
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            print(f"Telegram sent to {chat_id}")
            
        except Exception as e:
            print(f"Telegram send failed to {chat_id}: {e}")
            raise
    
    async def send_discord(self, data: Dict):
        """
        Send to Discord channel via webhook.
        """
        try:
            embed = {
                "title": f"{data['emoji']} New Signal: {data['symbol']}",
                "color": 0x00ff00 if data['direction'] == "LONG" else 0xff0000,
                "fields": [
                    {"name": "Direction", "value": data['direction'], "inline": True},
                    {"name": "Entry", "value": f"${data['current_price']:.2f}", "inline": True},
                    {"name": "Stop Loss", "value": f"${data['stop_loss']:.2f}", "inline": True},
                    {"name": "Take Profit", "value": f"${data['take_profit']:.2f}", "inline": True},
                    {"name": "SUE Score", "value": f"{data['sue_score']:.2f}", "inline": True},
                    {"name": "Quintile", "value": f"Q{data['quintile']}", "inline": True},
                ],
                "footer": {"text": "DriftEdge • Post-Earnings Drift Scanner"},
                "timestamp": datetime.now().isoformat()
            }
            
            webhook_data = {"embeds": [embed]}
            
            response = await asyncio.to_thread(
                requests.post,
                self.discord_webhook,
                json=webhook_data
            )
            
            print(f"Discord webhook sent: {response.status_code}")
            
        except Exception as e:
            print(f"Discord send failed: {e}")
            raise
    
    async def get_active_subscribers(self) -> List[Dict]:
        """
        Get list of active subscribers from database.
        TODO: Implement database connection
        """
        # For now, return test subscriber
        return [
            {
                'email': 'test@example.com',
                'phone': '+1234567890',
                'telegram_id': None,
                'email_enabled': True,
                'sms_enabled': True
            }
        ]

# Test the service
if __name__ == "__main__":
    service = AlertService()
    
    test_signal = {
        'symbol': 'AAPL',
        'signal_direction': 'LONG',
        'sue_score': 2.3,
        'quintile': 5,
        'surprise_pct': 8.5
    }
    
    asyncio.run(service.send_new_signal_alert(test_signal, 175.50))