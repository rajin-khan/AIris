"""
Email Service - Handles email notifications for AIris
Uses Gmail SMTP for sending alerts and daily/weekly summaries
"""

import os
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json


# AIris Brand Colors
COLORS = {
    "gold": "#C9AC78",
    "gold_light": "#D4BC8E",
    "gold_dark": "#A89058",
    "charcoal": "#1D1D1D",
    "bg": "#161616",
    "surface": "#212121",
    "surface_light": "#2A2A2A",
    "border": "#333333",
    "text_primary": "#EAEAEA",
    "text_secondary": "#A0A0A0",
    "text_muted": "#6B6B6B",
    "danger": "#C75050",
    "danger_light": "#D46A6A",
    "success": "#5A9E6F",
    "success_light": "#6FB583",
}


@dataclass
class EmailConfig:
    """Email configuration"""
    sender_email: str
    sender_password: str
    recipient_email: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587


@dataclass
class ActivityEvent:
    """Represents a single activity event"""
    timestamp: datetime
    event_type: str  # "SAFETY_ALERT", "SESSION", "OBSERVATION"
    summary: str
    location: Optional[str] = None
    descriptions: List[str] = field(default_factory=list)


class EmailService:
    def __init__(self):
        self.config: Optional[EmailConfig] = None
        self.last_alert_time: Optional[datetime] = None
        self.alert_cooldown_minutes: int = 5
        
        # Risk threshold (0.1 - 0.5, default 0.3)
        self.risk_threshold: float = 0.3
        self.MIN_RISK_THRESHOLD: float = 0.1
        self.MAX_RISK_THRESHOLD: float = 0.5
        
        self.daily_events: List[ActivityEvent] = []
        self.weekly_events: List[ActivityEvent] = []
        self.location_history: List[Dict[str, Any]] = []
        self.hourly_activity: Dict[int, int] = defaultdict(int)
        
        self._load_config()
    
    def set_risk_threshold(self, threshold: float) -> bool:
        """Set the risk threshold for alerts (0.4 - 0.8)"""
        if threshold < self.MIN_RISK_THRESHOLD:
            threshold = self.MIN_RISK_THRESHOLD
        elif threshold > self.MAX_RISK_THRESHOLD:
            threshold = self.MAX_RISK_THRESHOLD
        
        self.risk_threshold = threshold
        print(f"✓ Risk threshold set to: {threshold}")
        return True
    
    def get_risk_threshold(self) -> float:
        """Get the current risk threshold"""
        return self.risk_threshold
    
    def _load_config(self):
        """Load email configuration from environment variables"""
        sender = os.environ.get("EMAIL_SENDER", "")
        password = os.environ.get("EMAIL_PASSWORD", "")
        recipient = os.environ.get("EMAIL_RECIPIENT", "")
        
        if sender and password and recipient:
            self.config = EmailConfig(
                sender_email=sender,
                sender_password=password,
                recipient_email=recipient
            )
            print(f"✓ Email service configured: {sender} → {recipient}")
        else:
            missing = []
            if not sender: missing.append("EMAIL_SENDER")
            if not password: missing.append("EMAIL_PASSWORD")
            if not recipient: missing.append("EMAIL_RECIPIENT")
            print(f"⚠️  Email service not configured. Missing: {', '.join(missing)}")
            self.config = None
    
    def is_configured(self) -> bool:
        return self.config is not None
    
    def _can_send_alert(self) -> bool:
        if self.last_alert_time is None:
            return True
        time_since_last = datetime.now() - self.last_alert_time
        return time_since_last.total_seconds() >= (self.alert_cooldown_minutes * 60)
    
    def _extract_location(self, descriptions: List[str], summary: str) -> str:
        """Extract location from descriptions using keyword matching"""
        location_keywords = {
            "kitchen": ["kitchen", "stove", "refrigerator", "fridge", "cooking", "counter", "sink", "microwave", "oven"],
            "living room": ["living room", "couch", "sofa", "television", "tv", "remote", "living"],
            "bedroom": ["bedroom", "bed", "pillow", "sleeping", "blanket", "mattress"],
            "bathroom": ["bathroom", "toilet", "shower", "bath", "sink", "mirror", "restroom"],
            "hallway": ["hallway", "corridor", "hall"],
            "dining room": ["dining", "table", "chairs", "eating", "meal"],
            "office": ["office", "desk", "computer", "monitor", "keyboard", "work"],
            "garage": ["garage", "car", "vehicle", "parking"],
            "outdoors": ["outside", "outdoor", "garden", "yard", "street", "sidewalk", "porch"],
            "stairs": ["stairs", "staircase", "steps"],
            "entrance": ["door", "entrance", "doorway", "front door", "entryway"]
        }
        
        all_text = " ".join(descriptions + [summary]).lower()
        
        for location, keywords in location_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                return location
        
        return "unknown location"
    
    def _get_time_patterns(self) -> Dict[str, Any]:
        """Analyze time-based activity patterns"""
        if not self.hourly_activity:
            return {"most_active": None, "least_active": None, "pattern": "No activity data"}
        
        sorted_hours = sorted(self.hourly_activity.items(), key=lambda x: x[1], reverse=True)
        most_active_hour = sorted_hours[0][0] if sorted_hours else None
        
        morning = sum(self.hourly_activity.get(h, 0) for h in range(6, 12))
        afternoon = sum(self.hourly_activity.get(h, 0) for h in range(12, 18))
        evening = sum(self.hourly_activity.get(h, 0) for h in range(18, 24))
        night = sum(self.hourly_activity.get(h, 0) for h in range(0, 6))
        
        periods = {"Morning": morning, "Afternoon": afternoon, "Evening": evening, "Night": night}
        most_active_period = max(periods.items(), key=lambda x: x[1])[0] if any(periods.values()) else "Unknown"
        
        return {
            "most_active_hour": most_active_hour,
            "most_active_period": most_active_period,
            "hourly_breakdown": dict(self.hourly_activity)
        }
    
    def _format_hour(self, hour: int) -> str:
        if hour is None:
            return "—"
        if hour == 0:
            return "12:00 AM"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour - 12}:00 PM"
    
    def _get_base_styles(self) -> str:
        """Get base CSS styles for emails"""
        return f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: {COLORS['bg']};
            color: {COLORS['text_primary']};
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 560px;
            margin: 0 auto;
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            overflow: hidden;
        }}
        .header {{
            padding: 32px 32px 24px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        .logo {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 28px;
            font-weight: normal;
            color: {COLORS['text_primary']};
            letter-spacing: 0.04em;
            margin: 0 0 4px 0;
        }}
        .logo span {{
            font-size: 22px;
            opacity: 0.8;
        }}
        .header-subtitle {{
            font-size: 13px;
            color: {COLORS['text_secondary']};
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        .content {{
            padding: 24px 32px;
        }}
        .section {{
            margin-bottom: 24px;
        }}
        .section:last-child {{
            margin-bottom: 0;
        }}
        .section-title {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 11px;
            font-weight: normal;
            color: {COLORS['gold']};
            text-transform: uppercase;
            letter-spacing: 0.15em;
            margin: 0 0 12px 0;
        }}
        .card {{
            background-color: {COLORS['surface_light']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        .footer {{
            padding: 20px 32px;
            border-top: 1px solid {COLORS['border']};
            text-align: center;
        }}
        .footer p {{
            font-size: 11px;
            color: {COLORS['text_muted']};
            margin: 0;
        }}
        """
    
    async def _send_email(self, subject: str, html_content: str, plain_content: str = "") -> bool:
        """Send an email using Gmail SMTP"""
        if not self.config:
            print("⚠️  Email not configured - skipping send")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"AIris <{self.config.sender_email}>"
            message["To"] = self.config.recipient_email
            
            if plain_content:
                message.attach(MIMEText(plain_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.config.smtp_server,
                port=self.config.smtp_port,
                start_tls=True,
                username=self.config.sender_email,
                password=self.config.sender_password,
            )
            
            print(f"✓ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    async def send_safety_alert(
        self,
        summary: str,
        raw_descriptions: List[str],
        timestamp: Optional[datetime] = None,
        risk_score: float = 0.7,
        risk_factors: List[str] = None,
        is_fall: bool = False
    ) -> bool:
        """Send an immediate safety alert email with risk score"""
        if risk_factors is None:
            risk_factors = []
        
        # For falls, bypass cooldown
        if not is_fall and not self._can_send_alert():
            remaining = self.alert_cooldown_minutes - (
                (datetime.now() - self.last_alert_time).total_seconds() / 60
            )
            print(f"⚠️  Alert cooldown active. {remaining:.1f} minutes remaining.")
            return False
        
        if timestamp is None:
            timestamp = datetime.now()
        
        location = self._extract_location(raw_descriptions, summary)
        self.hourly_activity[timestamp.hour] += 1
        
        event = ActivityEvent(
            timestamp=timestamp,
            event_type="SAFETY_ALERT",
            summary=summary,
            location=location,
            descriptions=raw_descriptions
        )
        self.daily_events.append(event)
        self.weekly_events.append(event)
        
        # Determine severity level
        if risk_score >= 0.8 or is_fall:
            severity = "CRITICAL"
            severity_color = COLORS['danger']
        elif risk_score >= 0.6:
            severity = "HIGH"
            severity_color = COLORS['danger_light']
        else:
            severity = "MODERATE"
            severity_color = COLORS['gold']
        
        subject = f"AIris {severity} Alert — {location.title()}"
        if is_fall:
            subject = f"AIris FALL Alert — {location.title()}"
        
        # Risk factors HTML
        risk_factors_html = ""
        if risk_factors:
            factors_list = "".join(
                f'<li style="color: {COLORS["text_secondary"]}; margin-bottom: 4px; font-size: 12px;">{factor}</li>'
                for factor in risk_factors[:5]
            )
            risk_factors_html = f"""
            <div class="section">
                <h3 class="section-title">Risk Factors</h3>
                <ul style="margin: 0; padding-left: 18px;">
                    {factors_list}
                </ul>
            </div>
            """
        
        observations_html = "".join(
            f'<li style="color: {COLORS["text_secondary"]}; margin-bottom: 6px; font-size: 13px;">{desc}</li>'
            for desc in raw_descriptions[:5]
        )
        
        # Risk score visual
        risk_pct = int(risk_score * 100)
        risk_bar_color = COLORS['danger'] if risk_score >= 0.7 else (COLORS['gold'] if risk_score >= 0.5 else COLORS['success'])
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">{"Fall Alert" if is_fall else "Safety Alert"}</p>
        </div>
        
        <div class="content">
            <!-- Alert Banner -->
            <div style="background: {severity_color}15; border: 1px solid {severity_color}40; border-left: 3px solid {severity_color}; border-radius: 6px; padding: 16px; margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; color: {severity_color}; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">{severity} {"— FALL DETECTED" if is_fall else ""}</span>
                    <span style="font-size: 11px; color: {COLORS['text_muted']};">Risk Score: {risk_pct}%</span>
                </div>
                <div style="font-size: 14px; color: {COLORS['text_primary']}; line-height: 1.5;">{summary}</div>
            </div>
            
            <!-- Risk Score Bar -->
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em;">Risk Level</span>
                    <span style="font-size: 12px; color: {COLORS['text_primary']}; font-weight: 500;">{risk_pct}%</span>
                </div>
                <div style="background: {COLORS['border']}; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: {risk_bar_color}; height: 100%; width: {risk_pct}%; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <!-- Details -->
            <div class="section">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                            <span style="font-size: 12px; color: {COLORS['text_muted']};">Location</span>
                        </td>
                        <td style="padding: 8px 0; border-bottom: 1px solid {COLORS['border']}; text-align: right;">
                            <span style="font-size: 13px; color: {COLORS['text_primary']};">{location.title()}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                            <span style="font-size: 12px; color: {COLORS['text_muted']};">Time</span>
                        </td>
                        <td style="padding: 8px 0; border-bottom: 1px solid {COLORS['border']}; text-align: right;">
                            <span style="font-size: 13px; color: {COLORS['text_primary']};">{timestamp.strftime('%I:%M %p')}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;">
                            <span style="font-size: 12px; color: {COLORS['text_muted']};">Date</span>
                        </td>
                        <td style="padding: 8px 0; text-align: right;">
                            <span style="font-size: 13px; color: {COLORS['text_primary']};">{timestamp.strftime('%B %d, %Y')}</span>
                        </td>
                    </tr>
                </table>
            </div>
            
            {risk_factors_html}
            
            <!-- Observations -->
            <div class="section">
                <h3 class="section-title">Scene Observations</h3>
                <ul style="margin: 0; padding-left: 18px;">
                    {observations_html}
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Please check on your loved one when possible.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — {severity} Alert {"(FALL DETECTED)" if is_fall else ""}

Risk Score: {risk_pct}%

{summary}

Location: {location.title()}
Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%B %d, %Y')}

Risk Factors:
{chr(10).join(f'• {factor}' for factor in risk_factors[:5]) if risk_factors else '• None identified'}

Scene Observations:
{chr(10).join(f'• {desc}' for desc in raw_descriptions[:5])}

—
Please check on your loved one when possible.
"""
        
        success = await self._send_email(subject, html_content, plain_content)
        if success:
            self.last_alert_time = datetime.now()
        return success
    
    async def send_fall_alert(self, timestamp: Optional[datetime] = None) -> bool:
        """Send a simple fall alert email - no extra details, just the alert"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.hourly_activity[timestamp.hour] += 1
        
        # Simple event for tracking
        event = ActivityEvent(
            timestamp=timestamp,
            event_type="FALL_ALERT",
            summary="Possible fall or collision detected",
            location="unknown",
            descriptions=[]
        )
        self.daily_events.append(event)
        self.weekly_events.append(event)
        
        subject = "AIris FALL Alert"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Fall Alert</p>
        </div>
        
        <div class="content">
            <!-- Alert Banner -->
            <div style="background: {COLORS['danger']}20; border: 2px solid {COLORS['danger']}; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 14px; color: {COLORS['danger']}; text-transform: uppercase; letter-spacing: 0.15em; font-weight: 600; margin-bottom: 8px;">⚠️ URGENT</div>
                <div style="font-family: Georgia, serif; font-size: 22px; color: {COLORS['text_primary']}; margin-bottom: 8px;">Possible Fall or Collision Detected</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']};">Please check on your loved one immediately.</div>
            </div>
            
            <!-- Time -->
            <div style="text-align: center; padding: 16px; background: {COLORS['surface_light']}; border-radius: 8px;">
                <div style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px;">Detected At</div>
                <div style="font-size: 18px; color: {COLORS['text_primary']}; font-family: Georgia, serif;">{timestamp.strftime('%I:%M %p')}</div>
                <div style="font-size: 12px; color: {COLORS['text_secondary']}; margin-top: 2px;">{timestamp.strftime('%B %d, %Y')}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Please check on your loved one as soon as possible.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — FALL ALERT

⚠️ URGENT: Possible Fall or Collision Detected

Please check on your loved one immediately.

Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%B %d, %Y')}

—
Please check on your loved one as soon as possible.
"""
        
        success = await self._send_email(subject, html_content, plain_content)
        if success:
            self.last_alert_time = datetime.now()
        return success
    
    def add_fall_event(self, timestamp: Optional[datetime] = None):
        """Add a simple fall event to tracking for daily/weekly summaries"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.hourly_activity[timestamp.hour] += 1
        
        event = ActivityEvent(
            timestamp=timestamp,
            event_type="FALL_ALERT",
            summary="Possible fall or collision detected",
            location="unknown",
            descriptions=[]
        )
        self.daily_events.append(event)
        self.weekly_events.append(event)
    
    def add_observation(self, summary: str, descriptions: List[str], timestamp: Optional[datetime] = None, 
                        risk_score: float = 0.0):
        """Add a regular observation to tracking"""
        if timestamp is None:
            timestamp = datetime.now()
        
        location = self._extract_location(descriptions, summary)
        self.hourly_activity[timestamp.hour] += 1
        
        event = ActivityEvent(
            timestamp=timestamp,
            event_type="OBSERVATION",
            summary=summary,
            location=location,
            descriptions=descriptions
        )
        self.daily_events.append(event)
        self.weekly_events.append(event)
        
        self.location_history.append({
            "time": timestamp, 
            "location": location,
            "risk_score": risk_score
        })
    
    def add_fall_event(self, timestamp: Optional[datetime] = None):
        """Add a fall event to tracking for daily/weekly summaries"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.hourly_activity[timestamp.hour] += 1
        
        event = ActivityEvent(
            timestamp=timestamp,
            event_type="FALL_ALERT",
            summary="Possible fall or collision detected",
            location="unknown",
            descriptions=[]
        )
        self.daily_events.append(event)
        self.weekly_events.append(event)
    
    async def send_fall_alert(self, timestamp: Optional[datetime] = None) -> bool:
        """Send a simple fall alert email - no extra details"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Track the event
        self.add_fall_event(timestamp)
        
        subject = "AIris FALL Alert"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Fall Alert</p>
        </div>
        
        <div class="content">
            <!-- Alert Banner -->
            <div style="background: {COLORS['danger']}20; border: 2px solid {COLORS['danger']}; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['danger']}; margin-bottom: 8px;">
                    Possible Fall or Collision
                </div>
                <div style="font-size: 14px; color: {COLORS['text_secondary']};">
                    The camera detected a sudden change that may indicate a fall.
                </div>
            </div>
            
            <!-- Time Info -->
            <div class="section">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid {COLORS['border']};">
                            <span style="font-size: 13px; color: {COLORS['text_muted']};">Time Detected</span>
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid {COLORS['border']}; text-align: right;">
                            <span style="font-size: 14px; color: {COLORS['text_primary']}; font-weight: 500;">{timestamp.strftime('%I:%M %p')}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0;">
                            <span style="font-size: 13px; color: {COLORS['text_muted']};">Date</span>
                        </td>
                        <td style="padding: 12px 0; text-align: right;">
                            <span style="font-size: 14px; color: {COLORS['text_primary']};">{timestamp.strftime('%B %d, %Y')}</span>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>Please check on your loved one immediately.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — FALL ALERT

Possible Fall or Collision Detected

The camera detected a sudden change that may indicate a fall.

Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%B %d, %Y')}

Please check on your loved one immediately.
"""
        
        success = await self._send_email(subject, html_content, plain_content)
        if success:
            self.last_alert_time = datetime.now()
        return success
    
    async def send_daily_summary(self, force: bool = False) -> bool:
        """Send daily summary email"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        alert_count = sum(1 for e in self.daily_events if e.event_type in ["SAFETY_ALERT", "FALL_ALERT"])
        fall_count = sum(1 for e in self.daily_events if e.event_type == "FALL_ALERT")
        observation_count = sum(1 for e in self.daily_events if e.event_type == "OBSERVATION")
        total_events = len(self.daily_events)
        
        patterns = self._get_time_patterns()
        
        location_counts = defaultdict(int)
        for event in self.daily_events:
            if event.location:
                location_counts[event.location] += 1
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        is_all_clear = alert_count == 0
        
        subject = f"AIris Daily Summary — {yesterday.strftime('%B %d')}"
        if not is_all_clear:
            subject = f"AIris Daily Summary — {alert_count} Alert{'s' if alert_count != 1 else ''}"
        
        # Build status section
        if is_all_clear:
            status_html = f"""
            <div style="background: {COLORS['success']}15; border: 1px solid {COLORS['success']}30; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 18px; color: {COLORS['success_light']}; margin-bottom: 4px;">All Clear</div>
                <div style="font-size: 12px; color: {COLORS['text_secondary']};">No safety concerns detected</div>
            </div>
            """
        else:
            status_html = f"""
            <div style="background: {COLORS['danger']}15; border: 1px solid {COLORS['danger']}30; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 18px; color: {COLORS['danger_light']}; margin-bottom: 4px;">{alert_count} Alert{'s' if alert_count != 1 else ''} Detected</div>
                <div style="font-size: 12px; color: {COLORS['text_secondary']};">Review details below</div>
            </div>
            """
        
        # Build stats
        stats_html = f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
            <div style="text-align: center; flex: 1;">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['text_primary']};">{total_events}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Events</div>
            </div>
            <div style="text-align: center; flex: 1; border-left: 1px solid {COLORS['border']}; border-right: 1px solid {COLORS['border']};">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['text_primary']};">{observation_count}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Observations</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['danger'] if alert_count > 0 else COLORS['text_primary']};">{alert_count}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Alerts</div>
            </div>
        </div>
        """
        
        # Build locations
        locations_html = ""
        if top_locations:
            for loc, count in top_locations:
                locations_html += f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                    <span style="font-size: 13px; color: {COLORS['text_primary']};">{loc.title()}</span>
                    <span style="font-size: 13px; color: {COLORS['text_muted']};">{count}</span>
                </div>
                """
        else:
            locations_html = f'<div style="font-size: 13px; color: {COLORS["text_muted"]}; text-align: center; padding: 16px;">No location data</div>'
        
        # Build events timeline
        events_html = ""
        if self.daily_events:
            for event in sorted(self.daily_events, key=lambda x: x.timestamp, reverse=True)[:8]:
                event_time = event.timestamp.strftime('%I:%M %p')
                
                if event.event_type == "FALL_ALERT":
                    events_html += f"""
                    <div style="background: {COLORS['danger']}15; border-left: 3px solid {COLORS['danger']}; padding: 12px 14px; margin-bottom: 8px; border-radius: 0 6px 6px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 10px; color: {COLORS['danger']}; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Fall Alert</span>
                            <span style="font-size: 11px; color: {COLORS['text_muted']};">{event_time}</span>
                        </div>
                        <div style="font-size: 13px; color: {COLORS['text_primary']};">Possible fall or collision detected</div>
                    </div>
                    """
                elif event.event_type == "SAFETY_ALERT":
                    events_html += f"""
                    <div style="background: {COLORS['danger']}10; border-left: 2px solid {COLORS['danger']}; padding: 12px 14px; margin-bottom: 8px; border-radius: 0 6px 6px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 10px; color: {COLORS['danger_light']}; text-transform: uppercase; letter-spacing: 0.05em;">Alert</span>
                            <span style="font-size: 11px; color: {COLORS['text_muted']};">{event_time}</span>
                        </div>
                        <div style="font-size: 13px; color: {COLORS['text_primary']};">{event.summary[:100]}{'...' if len(event.summary) > 100 else ''}</div>
                    </div>
                    """
                else:
                    events_html += f"""
                    <div style="border-left: 2px solid {COLORS['border']}; padding: 12px 14px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 10px; color: {COLORS['gold']}; text-transform: uppercase; letter-spacing: 0.05em;">{event.location.title() if event.location else 'Observation'}</span>
                            <span style="font-size: 11px; color: {COLORS['text_muted']};">{event_time}</span>
                        </div>
                        <div style="font-size: 13px; color: {COLORS['text_secondary']};">{event.summary[:100]}{'...' if len(event.summary) > 100 else ''}</div>
                    </div>
                    """
        else:
            events_html = f"""
            <div style="text-align: center; padding: 32px; color: {COLORS['text_muted']};">
                <div style="font-family: Georgia, serif; font-size: 16px; margin-bottom: 8px;">No Activity Recorded</div>
                <div style="font-size: 12px;">The device may have been inactive today.</div>
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Daily Summary · {yesterday.strftime('%B %d, %Y')}</p>
        </div>
        
        <div class="content">
            {status_html}
            {stats_html}
            
            <div class="section">
                <h3 class="section-title">Locations</h3>
                <div class="card">
                    {locations_html}
                </div>
            </div>
            
            <div class="section">
                <h3 class="section-title">Activity Patterns</h3>
                <div class="card">
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                        <span style="font-size: 12px; color: {COLORS['text_muted']};">Most Active Period</span>
                        <span style="font-size: 13px; color: {COLORS['text_primary']};">{patterns.get('most_active_period', '—')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                        <span style="font-size: 12px; color: {COLORS['text_muted']};">Peak Hour</span>
                        <span style="font-size: 13px; color: {COLORS['text_primary']};">{self._format_hour(patterns.get('most_active_hour'))}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3 class="section-title">Timeline</h3>
                {events_html}
            </div>
        </div>
        
        <div class="footer">
            <p>AIris Vision Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — Daily Summary
{yesterday.strftime('%B %d, %Y')}

Status: {'All Clear' if is_all_clear else f'{alert_count} Alert(s)'}

Events: {total_events}
Observations: {observation_count}
Alerts: {alert_count}

Top Locations:
{chr(10).join(f'• {loc.title()}: {count}' for loc, count in top_locations) if top_locations else '• No data'}

Most Active Period: {patterns.get('most_active_period', '—')}
Peak Hour: {self._format_hour(patterns.get('most_active_hour'))}

—
AIris Vision Assistant
"""
        
        success = await self._send_email(subject, html_content, plain_content)
        if success:
            self.daily_events = []
            self.hourly_activity.clear()
            self.location_history = []
        return success
    
    async def send_weekly_report(self) -> bool:
        """Send weekly report email"""
        today = datetime.now()
        week_start = today - timedelta(days=7)
        
        alert_count = sum(1 for e in self.weekly_events if e.event_type in ["SAFETY_ALERT", "FALL_ALERT"])
        fall_count = sum(1 for e in self.weekly_events if e.event_type == "FALL_ALERT")
        observation_count = sum(1 for e in self.weekly_events if e.event_type == "OBSERVATION")
        total_events = len(self.weekly_events)
        daily_avg = total_events / 7 if total_events > 0 else 0
        
        location_counts = defaultdict(int)
        for event in self.weekly_events:
            if event.location:
                location_counts[event.location] += 1
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Alerts by day (including falls)
        alerts_by_day = defaultdict(list)
        for event in self.weekly_events:
            if event.event_type in ["SAFETY_ALERT", "FALL_ALERT"]:
                day_name = event.timestamp.strftime('%A')
                alerts_by_day[day_name].append(event)
        
        is_all_clear = alert_count == 0
        
        subject = f"AIris Weekly Report — {week_start.strftime('%b %d')} to {today.strftime('%b %d')}"
        
        # Status section
        if is_all_clear:
            status_html = f"""
            <div style="background: {COLORS['success']}15; border: 1px solid {COLORS['success']}30; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 20px; color: {COLORS['success_light']}; margin-bottom: 6px;">All Clear This Week</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']};">No safety concerns were detected during this period.</div>
            </div>
            """
        else:
            status_html = f"""
            <div style="background: {COLORS['gold']}10; border: 1px solid {COLORS['gold']}30; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 20px; color: {COLORS['gold']}; margin-bottom: 6px;">{alert_count} Alert{'s' if alert_count != 1 else ''} This Week</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']};">Please review the details in this report.</div>
            </div>
            """
        
        # Stats
        stats_html = f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 24px; padding: 20px; background: {COLORS['surface_light']}; border-radius: 8px;">
            <div style="text-align: center; flex: 1;">
                <div style="font-family: Georgia, serif; font-size: 28px; color: {COLORS['text_primary']};">{total_events}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Total Events</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-family: Georgia, serif; font-size: 28px; color: {COLORS['danger'] if alert_count > 0 else COLORS['success']};">{alert_count}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Alerts</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-family: Georgia, serif; font-size: 28px; color: {COLORS['text_primary']};">{daily_avg:.1f}</div>
                <div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Daily Avg</div>
            </div>
        </div>
        """
        
        # Location breakdown
        locations_html = ""
        if top_locations:
            max_count = top_locations[0][1]
            for loc, count in top_locations:
                pct = (count / max_count) * 100
                locations_html += f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 13px; color: {COLORS['text_primary']};">{loc.title()}</span>
                        <span style="font-size: 12px; color: {COLORS['text_muted']};">{count}</span>
                    </div>
                    <div style="background: {COLORS['border']}; border-radius: 3px; height: 4px; overflow: hidden;">
                        <div style="background: {COLORS['gold']}; height: 100%; width: {pct}%;"></div>
                    </div>
                </div>
                """
        else:
            locations_html = f'<div style="font-size: 13px; color: {COLORS["text_muted"]}; text-align: center; padding: 20px;">No location data available</div>'
        
        # Alerts summary
        alerts_html = ""
        if alerts_by_day:
            for day, events in sorted(alerts_by_day.items()):
                alerts_html += f"""
                <div style="border-left: 2px solid {COLORS['danger']}; padding: 12px 14px; margin-bottom: 8px; background: {COLORS['danger']}08;">
                    <div style="font-size: 12px; color: {COLORS['danger_light']}; font-weight: 500; margin-bottom: 6px;">{day}</div>
                    {''.join(f'<div style="font-size: 12px; color: {COLORS["text_secondary"]}; margin-top: 4px;">• {e.summary[:60]}...</div>' for e in events[:2])}
                </div>
                """
        else:
            alerts_html = f"""
            <div style="text-align: center; padding: 24px; background: {COLORS['success']}10; border-radius: 8px;">
                <div style="font-family: Georgia, serif; font-size: 16px; color: {COLORS['success_light']};">No Alerts This Week</div>
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Weekly Report · {week_start.strftime('%B %d')} — {today.strftime('%B %d, %Y')}</p>
        </div>
        
        <div class="content">
            {status_html}
            {stats_html}
            
            <div class="section">
                <h3 class="section-title">Location Breakdown</h3>
                <div class="card">
                    {locations_html}
                </div>
            </div>
            
            <div class="section">
                <h3 class="section-title">Alerts Summary</h3>
                {alerts_html}
            </div>
            
            <div class="section">
                <h3 class="section-title">Insights</h3>
                <div class="card">
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid {COLORS['border']};">
                        <span style="font-size: 12px; color: {COLORS['text_muted']};">Most Frequented Area</span>
                        <span style="font-size: 13px; color: {COLORS['text_primary']};">{top_locations[0][0].title() if top_locations else '—'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                        <span style="font-size: 12px; color: {COLORS['text_muted']};">Total Observations</span>
                        <span style="font-size: 13px; color: {COLORS['text_primary']};">{observation_count}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>AIris Vision Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — Weekly Report
{week_start.strftime('%B %d')} — {today.strftime('%B %d, %Y')}

Status: {'All Clear' if is_all_clear else f'{alert_count} Alert(s)'}

Total Events: {total_events}
Alerts: {alert_count}
Daily Average: {daily_avg:.1f}

Top Locations:
{chr(10).join(f'• {loc.title()}: {count}' for loc, count in top_locations) if top_locations else '• No data'}

—
AIris Vision Assistant
"""
        
        success = await self._send_email(subject, html_content, plain_content)
        if success:
            self.weekly_events = []
        return success
    
    def set_recipient(self, recipient_email: str):
        """Update the recipient email address"""
        if self.config:
            self.config.recipient_email = recipient_email
            print(f"✓ Email recipient updated: {recipient_email}")
        else:
            # Create config with just recipient (sender info from env)
            sender = os.environ.get("EMAIL_SENDER", "")
            password = os.environ.get("EMAIL_PASSWORD", "")
            if sender and password:
                self.config = EmailConfig(
                    sender_email=sender,
                    sender_password=password,
                    recipient_email=recipient_email
                )
                print(f"✓ Email service configured with recipient: {recipient_email}")
    
    async def send_welcome_email(self, guardian_name: str = "Guardian") -> bool:
        """Send a welcome email when a guardian is first set up"""
        subject = "Welcome to AIris"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Vision Assistant</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; padding: 32px 0 24px;">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['text_primary']}; margin-bottom: 12px;">Welcome, {guardian_name}</div>
                <div style="font-size: 14px; color: {COLORS['text_secondary']}; line-height: 1.6; max-width: 400px; margin: 0 auto;">
                    You've been registered as a guardian on AIris. You'll now receive notifications about your loved one's safety and daily activities.
                </div>
            </div>
            
            <div style="background: {COLORS['gold']}10; border: 1px solid {COLORS['gold']}25; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 14px; color: {COLORS['gold']}; margin-bottom: 12px;">What to Expect</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']}; line-height: 1.7;">
                    AIris monitors the environment and will keep you informed through regular updates and immediate alerts when needed.
                </div>
            </div>
            
            <div class="section">
                <h3 class="section-title">You'll Receive</h3>
                <div class="card">
                    <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Safety Alerts</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">When potential concerns are detected</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['danger']}; text-transform: uppercase; letter-spacing: 0.05em;">Immediate</div>
                        </div>
                    </div>
                    <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Daily Summaries</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">Overview of the day's activities</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em;">3:00 AM</div>
                        </div>
                    </div>
                    <div style="padding: 14px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Weekly Reports</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">Comprehensive weekly overview</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em;">Fridays</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; padding-top: 8px;">
                <div style="font-size: 12px; color: {COLORS['text_muted']};">
                    Thank you for trusting AIris to help keep your loved one safe.
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>AIris Vision Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
Welcome to AIris, {guardian_name}

You've been registered as a guardian on AIris. You'll now receive notifications about your loved one's safety and daily activities.

What You'll Receive:

• Safety Alerts — Immediate notification when potential concerns are detected
• Daily Summaries — Every morning at 3:00 AM
• Weekly Reports — Every Friday at midnight

Thank you for trusting AIris to help keep your loved one safe.

—
AIris Vision Assistant
"""
        
        return await self._send_email(subject, html_content, plain_content)
    
    def set_recipient(self, recipient_email: str):
        """Set/update the recipient email address"""
        if self.config:
            self.config.recipient_email = recipient_email
            print(f"✓ Email recipient updated to: {recipient_email}")
        else:
            # Create config with just recipient for now
            sender = os.environ.get("EMAIL_SENDER", "")
            password = os.environ.get("EMAIL_PASSWORD", "")
            if sender and password:
                self.config = EmailConfig(
                    sender_email=sender,
                    sender_password=password,
                    recipient_email=recipient_email
                )
                print(f"✓ Email service configured with recipient: {recipient_email}")
    
    # Alias for backwards compatibility
    update_recipient = set_recipient
    
    async def send_welcome_email(self, guardian_name: str = "Guardian") -> bool:
        """Send a welcome email to a newly configured guardian"""
        subject = "Welcome to AIris"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Vision Assistant</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; padding: 32px 0 24px;">
                <div style="font-family: Georgia, serif; font-size: 24px; color: {COLORS['text_primary']}; margin-bottom: 12px;">Welcome, {guardian_name}</div>
                <div style="font-size: 14px; color: {COLORS['text_secondary']}; line-height: 1.6;">
                    You've been added as a guardian for an AIris user.<br>
                    You'll now receive important notifications about their safety.
                </div>
            </div>
            
            <div style="background: {COLORS['gold']}10; border: 1px solid {COLORS['gold']}25; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <div style="font-family: Georgia, serif; font-size: 13px; color: {COLORS['gold']}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px;">What is AIris?</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']}; line-height: 1.7;">
                    AIris is an AI-powered vision assistant designed to help visually impaired individuals 
                    navigate their daily lives safely. The system monitors their environment and can alert 
                    you if it detects any safety concerns.
                </div>
            </div>
            
            <div class="section">
                <h3 class="section-title">What You'll Receive</h3>
                <div class="card">
                    <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Safety Alerts</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">Immediate notification if danger is detected</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['danger']}; text-transform: uppercase;">Instant</div>
                        </div>
                    </div>
                    <div style="padding: 14px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Daily Summary</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">Overview of the day's activity and any concerns</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase;">3:00 AM</div>
                        </div>
                    </div>
                    <div style="padding: 14px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 14px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Weekly Report</div>
                                <div style="font-size: 11px; color: {COLORS['text_muted']};">Comprehensive weekly health and activity insights</div>
                            </div>
                            <div style="font-size: 11px; color: {COLORS['text_muted']}; text-transform: uppercase;">Fridays</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; padding: 24px 0 8px;">
                <div style="font-size: 13px; color: {COLORS['text_secondary']};">
                    Thank you for being there for your loved one.
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>AIris Vision Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
AIRIS — Welcome, {guardian_name}

You've been added as a guardian for an AIris user.
You'll now receive important notifications about their safety.

WHAT IS AIRIS?
AIris is an AI-powered vision assistant designed to help visually impaired 
individuals navigate their daily lives safely. The system monitors their 
environment and can alert you if it detects any safety concerns.

WHAT YOU'LL RECEIVE:
• Safety Alerts — Immediate notification if danger is detected
• Daily Summary — Overview of the day's activity (3:00 AM)
• Weekly Report — Comprehensive weekly insights (Fridays)

Thank you for being there for your loved one.

—
AIris Vision Assistant
"""
        
        return await self._send_email(subject, html_content, plain_content)
    
    async def send_test_email(self) -> bool:
        """Send a test email to verify configuration"""
        subject = "AIris — Configuration Successful"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">A<span>IRIS</span></h1>
            <p class="header-subtitle">Email Configuration</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; padding: 24px 0;">
                <div style="font-family: Georgia, serif; font-size: 20px; color: {COLORS['success_light']}; margin-bottom: 8px;">Configuration Successful</div>
                <div style="font-size: 13px; color: {COLORS['text_secondary']};">Your email notifications are now active.</div>
            </div>
            
            <div class="section">
                <h3 class="section-title">What You'll Receive</h3>
                <div class="card">
                    <div style="padding: 10px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="font-size: 13px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Safety Alerts</div>
                        <div style="font-size: 11px; color: {COLORS['text_muted']};">Immediate notification when concerns are detected</div>
                    </div>
                    <div style="padding: 10px 0; border-bottom: 1px solid {COLORS['border']};">
                        <div style="font-size: 13px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Daily Summaries</div>
                        <div style="font-size: 11px; color: {COLORS['text_muted']};">Every morning at 3:00 AM</div>
                    </div>
                    <div style="padding: 10px 0;">
                        <div style="font-size: 13px; color: {COLORS['text_primary']}; margin-bottom: 2px;">Weekly Reports</div>
                        <div style="font-size: 11px; color: {COLORS['text_muted']};">Every Friday at midnight</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>AIris Vision Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = """
AIRIS — Configuration Successful

Your email notifications are now active.

What You'll Receive:
• Safety Alerts — Immediate notification when concerns are detected
• Daily Summaries — Every morning at 3:00 AM
• Weekly Reports — Every Friday at midnight

—
AIris Vision Assistant
"""
        
        return await self._send_email(subject, html_content, plain_content)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
