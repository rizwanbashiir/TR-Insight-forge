import resend
from app.config.settings import settings

resend.api_key = settings.RESEND_API_KEY

def send_verification_email(to_email: str, code: str):
    """
    Sends a verification code email to the newly registered user.
    """
    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "re_123456789_placeholder":
        print(f"RESEND: (Mock) Verification code for {to_email} is {code}")
        return

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ font-family: 'Inter', Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
      .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }}
      .header {{ padding: 30px; text-align: center; border-bottom: 1px solid #f1f5f9; }}
      .logo {{ font-size: 24px; font-weight: 800; color: #0f172a; }}
      .logo span {{ color: #4F46E5; }}
      .content {{ padding: 40px 30px; text-align: center; }}
      .title {{ font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 0; margin-bottom: 16px; line-height: 1.2; letter-spacing: -0.5px; }}
      .text {{ color: #475569; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }}
      .otp-box {{ background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 20px; margin: 0 auto 30px; max-width: 300px; }}
      .otp-code {{ font-size: 36px; font-weight: 800; color: #4F46E5; letter-spacing: 8px; margin-left: 8px; }}
      .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #94a3b8; font-size: 13px; }}
    </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="logo"><span>✦</span> TR-Insight-Forge</div>
        </div>
        <div class="content">
          <h1 class="title">Verify your email</h1>
          <p class="text">Welcome aboard! To start transforming your business data into actionable intelligence, please verify your email address using the code below.</p>
          <div class="otp-box">
            <div class="otp-code">{code}</div>
          </div>
          <p class="text" style="font-size: 14px;">This code will expire in 10 minutes.</p>
        </div>
        <div class="footer">
          If you didn't attempt to sign up, you can safely ignore this email.<br>
          &copy; 2026 TR-Insight-Forge. All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "Verify your TR-InsightForge Account",
            "html": html_content,
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"Failed to send verification email to {to_email}: {e}")


def send_password_reset_email(to_email: str, reset_link: str):
    """
    Sends a password reset link email.
    """
    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "re_123456789_placeholder":
        print(f"RESEND: (Mock) Password reset link for {to_email}: {reset_link}")
        return

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ font-family: 'Inter', Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
      .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }}
      .header {{ padding: 30px; text-align: center; border-bottom: 1px solid #f1f5f9; }}
      .logo {{ font-size: 24px; font-weight: 800; color: #0f172a; }}
      .logo span {{ color: #4F46E5; }}
      .content {{ padding: 40px 30px; text-align: center; }}
      .title {{ font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 0; margin-bottom: 16px; line-height: 1.2; letter-spacing: -0.5px; }}
      .text {{ color: #475569; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }}
      .button-box {{ margin: 0 auto 30px; }}
      .button {{ background-color: #4F46E5; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block; }}
      .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #94a3b8; font-size: 13px; }}
    </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="logo"><span>✦</span> TR-Insight-Forge</div>
        </div>
        <div class="content">
          <h1 class="title">Reset Your Password</h1>
          <p class="text">We received a request to reset your password. Click the button below to choose a new one:</p>
          <div class="button-box">
            <a href="{reset_link}" class="button">Reset Password</a>
          </div>
          <p class="text" style="font-size: 14px;">If the button doesn't work, copy and paste this link into your browser:</p>
          <p class="text" style="font-size: 14px; word-break: break-all;">
            <a href="{reset_link}" style="color: #4F46E5;">{reset_link}</a>
          </p>
          <p class="text" style="font-size: 14px;">This link will expire in 6 hours.</p>
        </div>
        <div class="footer">
          If you didn't request a password reset, you can safely ignore this email.<br>
          &copy; 2026 TR-Insight-Forge. All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "Reset your TR-InsightForge Password",
            "html": html_content,
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"Failed to send password reset email to {to_email}: {e}")
