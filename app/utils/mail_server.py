
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

def request_quote(company_name, full_name, client_email, address, tel, job, origin_destination, product_name,
                  weight_dimensions, service, container_size, user_id):
    """Send quote request email to agency and confirmation email to client"""

    # Gmail SMTP credentials (App Password recommended)
    sender_email = os.getenv("EMAIL_USER","tolasom.titan@gmail.com")
    sender_password = os.getenv("EMAIL_PASSWORD", "bapl rpih plow tzyp")


    if not sender_email or not sender_password:
        print("❌ Gmail credentials not set in environment variables")
        return False

    subject_agency = "📦 New Quote Request"
    subject_client = "✅ Your Quote Request Has Been Received"

    # HTML body for agency (full details)
    agency_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px; margin: 0;">
            <table align="center" width="100%" style="max-width: 650px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <tr>
                <td align="center" style="padding: 20px 20px 0 20px;">
                <img src="https://clncambodia.com/logo.png" alt="Company Logo" style="max-width: 180px; height: auto; display: block;" />
                </td>
            </tr>
            <tr>
                <td style="padding: 30px;">
                <h2 style="color: #111827; text-align: center; margin-bottom: 20px;">📦 New Quote Request</h2>
                <p style="font-size: 16px; color: #374151; text-align: center; margin-bottom: 30px;">
                    A client has submitted a request for quotation:
                </p>
                <table width="100%" cellspacing="0" cellpadding="10" style="border-collapse: collapse; font-size: 15px; color: #374151;">
                    <tr style="background-color: #f9fafb;"><td><b>Company Name</b></td><td>{company_name}</td></tr>
                    <tr><td><b>Full Name</b></td><td>{full_name}</td></tr>
                    <tr style="background-color: #f9fafb;"><td><b>Email</b></td><td>{client_email}</td></tr>
                    <tr><td><b>Address</b></td><td>{address}</td></tr>
                    <tr style="background-color: #f9fafb;"><td><b>Tel</b></td><td>{tel}</td></tr>
                    <tr><td><b>Job</b></td><td>{job}</td></tr>
                    <tr style="background-color: #f9fafb;"><td><b>Origin → Destination</b></td><td>{origin_destination}</td></tr>
                    <tr><td><b>Product Name(s)</b></td><td>{product_name}</td></tr>
                    <tr style="background-color: #f9fafb;"><td><b>Weight & Dimensions</b></td><td>{weight_dimensions}</td></tr>
                    <tr><td><b>Service</b></td><td>{service}</td></tr>
                    <tr style="background-color: #f9fafb;"><td><b>Container Size</b></td><td>{container_size}</td></tr>
                </table>
                <p style="margin-top: 30px; font-size: 14px; color: #6b7280; text-align: center;">
                    This request was generated automatically from your website.
                </p>
                </td>
            </tr>
            </table>
        </body>
        </html>
    """

    # HTML body for client (confirmation)
    client_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9fafb; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; padding: 30px; text-align: center;">
                <h2 style="color: #16a34a;">✅ Thank You, {full_name}!</h2>
                <p style="color: #374151; font-size: 16px; margin-top: 10px;">
                    Your quotation request has been successfully received by <b>{company_name}</b>.
                </p>
                <p style="color: #374151; font-size: 15px; margin-top: 15px;">
                    Our team will review your request and get back to you shortly.
                </p>
                <p style="color: #6b7280; font-size: 13px; margin-top: 30px;">
                    This is an automated confirmation. Please do not reply.
                </p>
            </div>
        </body>
    </html>
    """

    try:
        context = ssl.create_default_context()

        # Connect once and send both emails
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)

            # 1. Send to agency
            msg_agency = MIMEMultipart("alternative")
            msg_agency["From"] = formataddr((f"Customer-{client_email}"))
            msg_agency["To"] = sender_email
            msg_agency["Subject"] = subject_agency
            msg_agency.attach(MIMEText(agency_body, "html"))
            server.sendmail(sender_email, sender_email, msg_agency.as_string())

            # 2. Send confirmation to client
            msg_client = MIMEMultipart("alternative")
            msg_client["From"] = formataddr(("CLN CAMBODIA No-Reply", "noreply@clncambodia.com"))
            msg_client["To"] = client_email
            msg_client["Subject"] = subject_client
            msg_client.attach(MIMEText(client_body, "html"))
            server.sendmail(sender_email, client_email, msg_client.as_string())

        return True

    except Exception as e:
        print(f"❌ Failed to send emails: {e}")
        return False

def contact_us(company_name, full_name, client_email, address, tel, job, origin_destination, product_name,
                  weight_dimensions, service, container_size, user_id):
    """Message from Customer to agency and confirmation email to customer"""

    
    sender_email = os.getenv("EMAIL_USER","tolasom.titan@gmail.com")
    sender_password = os.getenv("EMAIL_PASSWORD", "bapl rpih plow tzyp")

    if not sender_email or not sender_password:
        print("❌ Gmail credentials not set in environment variables")
        return False

    subject_agency = "📦 New Message from Customer"
    subject_client = "✅ Your Message from Customer Has Been Received"

    # HTML body for agency (full details)
    agency_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px; margin: 0;">
                <table align="center" width="100%" style="max-width: 650px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <tr>
                    <td align="center" style="padding: 20px 20px 0 20px;">
                    <img src="https://clncambodia.com/logo.png" alt="Company Logo" style="max-width: 180px; height: auto; display: block;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 30px;">
                    <h2 style="color: #111827; text-align: center; margin-bottom: 20px;">📦 New Quote Request</h2>
                    <p style="font-size: 16px; color: #374151; text-align: center; margin-bottom: 30px;">
                        A client has submitted a request for quotation:
                    </p>
                    <table width="100%" cellspacing="0" cellpadding="10" style="border-collapse: collapse; font-size: 15px; color: #374151;">
                        <tr style="background-color: #f9fafb;"><td><b>Company Name</b></td><td>{company_name}</td></tr>
                        <tr><td><b>Full Name</b></td><td>{full_name}</td></tr>
                        <tr style="background-color: #f9fafb;"><td><b>Email</b></td><td>{client_email}</td></tr>
                        <tr><td><b>Address</b></td><td>{address}</td></tr>
                        <tr style="background-color: #f9fafb;"><td><b>Tel</b></td><td>{tel}</td></tr>
                        <tr><td><b>Job</b></td><td>{job}</td></tr>
                        <tr style="background-color: #f9fafb;"><td><b>Origin → Destination</b></td><td>{origin_destination}</td></tr>
                        <tr><td><b>Product Name(s)</b></td><td>{product_name}</td></tr>
                        <tr style="background-color: #f9fafb;"><td><b>Weight & Dimensions</b></td><td>{weight_dimensions}</td></tr>
                        <tr><td><b>Service</b></td><td>{service}</td></tr>
                        <tr style="background-color: #f9fafb;"><td><b>Container Size</b></td><td>{container_size}</td></tr>
                    </table>
                    <p style="margin-top: 30px; font-size: 14px; color: #6b7280; text-align: center;">
                        This request was generated automatically from your website.
                    </p>
                    </td>
                </tr>
                </table>
            </body>
        </html>
    """

    # HTML body for client (confirmation)
    client_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9fafb; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; padding: 30px; text-align: center;">
                <h2 style="color: #16a34a;">✅ Thank You, {full_name}!</h2>
                <p style="color: #374151; font-size: 16px; margin-top: 10px;">
                    Your message has been successfully received by <b>{company_name}</b>.
                </p>
                <p style="color: #374151; font-size: 15px; margin-top: 15px;">
                    Our team will review your message and get back to you shortly.
                </p>
                <p style="color: #6b7280; font-size: 13px; margin-top: 30px;">
                    This is an automated confirmation. Please do not reply.
                </p>
            </div>
        </body>
    </html>
    """

    try:
        context = ssl.create_default_context()

        # Connect once and send both emails
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)

            # 1. Send to agency
            msg_agency = MIMEMultipart("alternative")
            msg_agency["From"] = sender_email
            msg_agency["To"] = sender_email
            msg_agency["Subject"] = subject_agency
            msg_agency.attach(MIMEText(agency_body, "html"))
            server.sendmail(sender_email, sender_email, msg_agency.as_string())

            # 2. Send confirmation to client
            msg_client = MIMEMultipart("alternative")
            msg_client["From"] = sender_email
            msg_client["To"] = client_email
            msg_client["Subject"] = subject_client
            msg_client.attach(MIMEText(client_body, "html"))
            server.sendmail(sender_email, client_email, msg_client.as_string())

        print("✅ Contact Us request sent to agency and confirmation sent to client.")
        return True

    except Exception as e:
        print(f"❌ Failed to send emails: {e}")
        return False
