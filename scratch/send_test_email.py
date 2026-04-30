import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Read .env
env = {}
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

host = env.get('EMAIL_HOST', 'mail.abumonyaagency.com')
user = env.get('EMAIL_HOST_USER', '')
pwd  = env.get('EMAIL_HOST_PASSWORD', '')
TO   = 'baitul.technology@gmail.com'

print(f"Host : {host}")
print(f"User : {user}")
print(f"To   : {TO}")

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Test Email - Abu Monya Agency (وكالة أبو منية)'
msg['From']    = f'Abu Monya Agency <{user}>'
msg['To']      = TO

html_body = """
<div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:32px;
            border-radius:14px;background:#f9f9f9;border:1px solid #e0e0e0;">
  <div style="text-align:center;margin-bottom:24px;">
    <h2 style="color:#1a6f4f;margin:0;">&#x2708;&#xFE0F; Abu Monya Agency</h2>
    <p style="color:#888;font-size:13px;margin:4px 0 0;">abumonyaagency.com</p>
  </div>
  <p style="font-size:16px;color:#333;line-height:1.6;">Hello,</p>
  <p style="font-size:16px;color:#333;line-height:1.6;">
    This is a <strong style="color:#1a6f4f;">test email</strong> confirming that SMTP
    is correctly configured for <strong>abumonyaagency.com</strong>.
  </p>
  <p style="font-size:16px;color:#333;line-height:1.6;">
    Registration OTP emails will be delivered from this address going forward.
  </p>
  <div style="margin:28px 0;text-align:center;">
    <span style="display:inline-block;padding:14px 36px;border-radius:8px;
                 background:#1a6f4f;color:#fff;font-size:18px;font-weight:700;
                 letter-spacing:3px;">SMTP OK &#x2705;</span>
  </div>
  <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">
  <p style="font-size:12px;color:#aaa;text-align:center;margin:0;">
    Sent from noreply@abumonyaagency.com
  </p>
</div>
"""

msg.attach(MIMEText(html_body, 'html', 'utf-8'))

try:
    with smtplib.SMTP(host, 587, timeout=15) as s:
        s.ehlo()
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, [TO], msg.as_string())
    print(f"\nSUCCESS: Test email sent to {TO}")
except Exception as e:
    print(f"\nFAILED: {type(e).__name__}: {e}")
