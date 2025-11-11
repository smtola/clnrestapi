import smtplib
import ssl
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str) -> bool:
    """
    Send a styled OTP email via Gmail SMTP.

    Args:
        email (str): Recipient email address.
        otp (str): OTP code to send.

    Returns:
        bool: True if email sent successfully, False otherwise.
    """

    # Use environment variables for security
    sender_email = os.getenv("EMAIL_USER","tolasom.titan@gmail.com")
    sender_password = os.getenv("EMAIL_PASSWORD", "bapl rpih plow tzyp")

    subject = "Your Security Code"

    # Styled HTML email body
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px;">
        <table align="center" width="100%" style="max-width: 600px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
          <tr>
            <td align="center" style="padding: 20px 20px 0 20px;">
              <img src="https://cln-tan.vercel.app/assets/logo-CxDBtqyW.png" alt="Company Logo" style="max-width: 180px; height: auto; display: block;" />
            </td>
          </tr>
          <tr>
            <td style="padding: 30px; text-align: center;">
              <h2 style="color: #111827; margin-bottom: 20px;">Your Security Code</h2>
              <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                Use the following code to complete your verification process:
              </p>
              <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb; background: #f0f9ff; padding: 15px 25px; border-radius: 8px; display: inline-block;">
                {otp}
              </div>
              <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                This code will expire in <strong>5 minutes</strong>. If you did not request this, please ignore this email.
              </p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        # Connect to Gmail SMTP securely
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        print(f"✅ OTP sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {email}: {e}")
        return False
