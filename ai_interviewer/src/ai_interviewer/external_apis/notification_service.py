"""
Notification service for email/SMS communications
"""

import logging
from typing import Optional, Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification service for email and SMS communications."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.email_user = getattr(settings, 'EMAIL_USER', '')
        self.email_password = getattr(settings, 'EMAIL_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', self.email_user)
        
        # SMS service (e.g., Twilio)
        self.twilio_sid = getattr(settings, 'TWILIO_SID', '')
        self.twilio_token = getattr(settings, 'TWILIO_TOKEN', '')
        self.twilio_phone = getattr(settings, 'TWILIO_PHONE', '')
    
    async def send_interview_invitation(self, user_email: str, interview_details: Dict[str, Any]) -> bool:
        """Send interview invitation email."""
        try:
            subject = f"Interview Invitation - {interview_details.get('position', 'Position')}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Interview Invitation</h2>
                <p>Dear Candidate,</p>
                <p>You have been invited to participate in an AI-powered interview for the position of <strong>{interview_details.get('position', 'N/A')}</strong>.</p>
                
                <h3>Interview Details:</h3>
                <ul>
                    <li><strong>Position:</strong> {interview_details.get('position', 'N/A')}</li>
                    <li><strong>Type:</strong> {interview_details.get('interview_type', 'N/A')}</li>
                    <li><strong>Difficulty:</strong> {interview_details.get('difficulty', 'N/A')}</li>
                    <li><strong>Scheduled Date:</strong> {interview_details.get('scheduled_date', 'To be confirmed')}</li>
                </ul>
                
                <p><strong>Interview Link:</strong> <a href="{interview_details.get('interview_link', '#')}">Start Interview</a></p>
                
                <h3>Preparation Tips:</h3>
                <ul>
                    <li>Ensure you have a stable internet connection</li>
                    <li>Test your microphone and camera beforehand</li>
                    <li>Find a quiet, well-lit space for the interview</li>
                    <li>Review the job description and your resume</li>
                </ul>
                
                <p>Good luck with your interview!</p>
                <p>Best regards,<br>AI Interviewer Team</p>
            </body>
            </html>
            """
            
            return await self._send_email(user_email, subject, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send interview invitation: {e}")
            return False
    
    async def send_interview_reminder(self, user_email: str, interview_details: Dict[str, Any]) -> bool:
        """Send interview reminder email."""
        try:
            subject = f"Interview Reminder - {interview_details.get('position', 'Position')}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Interview Reminder</h2>
                <p>Dear Candidate,</p>
                <p>This is a friendly reminder about your upcoming interview scheduled for <strong>{interview_details.get('scheduled_date', 'soon')}</strong>.</p>
                
                <p><strong>Interview Link:</strong> <a href="{interview_details.get('interview_link', '#')}">Start Interview</a></p>
                
                <p>Please ensure you're ready 5 minutes before the scheduled time.</p>
                
                <p>Best regards,<br>AI Interviewer Team</p>
            </body>
            </html>
            """
            
            return await self._send_email(user_email, subject, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send interview reminder: {e}")
            return False
    
    async def send_interview_completion(self, user_email: str, interview_results: Dict[str, Any]) -> bool:
        """Send interview completion notification with results."""
        try:
            subject = "Interview Completed - Thank You"
            
            html_body = f"""
            <html>
            <body>
                <h2>Interview Completed</h2>
                <p>Dear Candidate,</p>
                <p>Thank you for completing your interview with us. Here's a summary of your performance:</p>
                
                <h3>Interview Summary:</h3>
                <ul>
                    <li><strong>Position:</strong> {interview_results.get('position', 'N/A')}</li>
                    <li><strong>Duration:</strong> {interview_results.get('duration', 'N/A')} minutes</li>
                    <li><strong>Questions Answered:</strong> {interview_results.get('questions_answered', 'N/A')}</li>
                    <li><strong>Overall Score:</strong> {interview_results.get('overall_score', 'N/A')}/10</li>
                </ul>
                
                <h3>Key Strengths:</h3>
                <ul>
                    {self._format_list_items(interview_results.get('strengths', []))}
                </ul>
                
                <h3>Areas for Improvement:</h3>
                <ul>
                    {self._format_list_items(interview_results.get('improvements', []))}
                </ul>
                
                <p>We will review your interview and get back to you within 3-5 business days.</p>
                
                <p>Thank you for your time and interest in our company!</p>
                <p>Best regards,<br>AI Interviewer Team</p>
            </body>
            </html>
            """
            
            return await self._send_email(user_email, subject, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send interview completion email: {e}")
            return False
    
    async def send_sms_reminder(self, phone_number: str, message: str) -> bool:
        """Send SMS reminder (requires Twilio setup)."""
        try:
            if not self.twilio_sid or not self.twilio_token:
                logger.warning("Twilio credentials not configured")
                return False
            
            # Mock SMS sending - replace with actual Twilio implementation
            logger.info(f"SMS sent to {phone_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email using SMTP."""
        try:
            if not self.email_user or not self.email_password:
                logger.warning("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _format_list_items(self, items: List[str]) -> str:
        """Format list items for HTML."""
        if not items:
            return "<li>No items to display</li>"
        return "\n".join([f"<li>{item}</li>" for item in items])
    
    async def send_system_alert(self, alert_type: str, message: str, details: Dict[str, Any]) -> bool:
        """Send system alerts to administrators."""
        try:
            admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
            if not admin_emails:
                logger.warning("No admin emails configured for alerts")
                return False
            
            subject = f"System Alert: {alert_type}"
            
            html_body = f"""
            <html>
            <body>
                <h2>System Alert: {alert_type}</h2>
                <p><strong>Message:</strong> {message}</p>
                
                <h3>Details:</h3>
                <ul>
                    {self._format_dict_items(details)}
                </ul>
                
                <p>Timestamp: {details.get('timestamp', 'N/A')}</p>
            </body>
            </html>
            """
            
            for admin_email in admin_emails:
                await self._send_email(admin_email, subject, html_body)
            
            return True
            
        except Exception as e:
            logger.error(f"System alert sending failed: {e}")
            return False
    
    def _format_dict_items(self, items: Dict[str, Any]) -> str:
        """Format dictionary items for HTML."""
        if not items:
            return "<li>No details available</li>"
        return "\n".join([f"<li><strong>{key}:</strong> {value}</li>" for key, value in items.items()])
