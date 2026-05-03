
class EmailTemplateManager:
 
    @staticmethod
    def otp_template(otp: str, title: str, user_name: str) -> tuple[str, str]:
 
        subject = f"{title} - Tasdiqlash kodi: {otp}"
 
        html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .otp-box {{ background: #f5f5f5; border: 2px solid #667eea; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                    .otp-code {{ font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 5px; font-family: 'Courier New', monospace; }}
                    .warning {{ color: #666; font-size: 14px; margin-top: 20px; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Tasdiqlash Kodi</h1>
                    </div>
                    <div class="content">
                        <p>Salom, <strong>{user_name}</strong>!</p>
                        <p>{title} uchun quyidagi tasdiqlash kodini ishlating:</p>
                        
                        <div class="otp-box">
                            <div class="otp-code">{otp}</div>
                        </div>
                        
                        <p class="warning">
                            ⚠️ <strong>Oqibat:</strong> Bu kod 5 daqiqa ichida amal qiladi.
                            <br>
                            Agar siz bu so'rovni yubormagan bo'lsangiz, bu xabarni e'tibor bermang.
                        </p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Your App. Barcha huquqlar himoyalangan.</p>
                    </div>
                </div>
            </body>
        </html>
        """
 
        return subject, html
 
    @staticmethod
    def password_reset_template(reset_link: str, user_name: str) -> tuple[str, str]:
        """Parol tiklash email template"""
 
        subject = "Parolni tiklash - Action kerak"
 
        html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ff6b6b; color: white; padding: 30px; border-radius: 8px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; margin: 20px 0; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Parolni Tiklash</h1>
                    </div>
                    <div class="content">
                        <p>Salom, <strong>{user_name}</strong>!</p>
                        <p>Parolni tiklash so'rovi olingan. Quyidagi tugmani bosing:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="button">Parolni Tiklash</a>
                        </div>
                        
                        <p>Yoki quyidagi havolani nusxalang:</p>
                        <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                        
                        <div class="warning">
                            <strong>Diqqat!</strong> Bu havola 1 soat ichida amal qiladi.
                            <br>
                            Agar siz bu so'rovni yubormagan bo'lsangiz, bu xabarni e'tibor bermang va parolni ozingizga ma'lum bo'lgan holatda saqlang.
                        </div>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Your App</p>
                    </div>
                </div>
            </body>
        </html>
        """