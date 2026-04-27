from string import Template


_OTP_HTML = Template("""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:32px 20px;">
  <h2 style="color:#111;margin-bottom:8px;">$title</h2>
  <p style="color:#444;">Salom, <strong>$username</strong>!</p>
  <p style="color:#444;">$intro_text</p>
 
  <div style="margin:28px 0;text-align:center;">
    <div style="display:inline-block;background:#f3f4f6;border-radius:12px;
                padding:20px 40px;letter-spacing:10px;
                font-size:36px;font-weight:700;color:#111;
                font-family:'Courier New',monospace;border:2px solid #e5e7eb;">
      $otp_code
    </div>
  </div>
 
  <p style="color:#6b7280;font-size:14px;">
    ⏱ Kod <strong>$expires_text</strong> ichida amal qiladi.<br>
    🔒 Kodni hech kimga bermang.<br>
    $note
  </p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
  <p style="color:#9ca3af;font-size:12px;">$app_name &mdash; avtomatik xabar</p>
</body>
</html>
""")
 
_OTP_TEXT = Template(
    "$title\n\n"
    "Salom, $username!\n\n"
    "$intro_text\n\n"
    "Tasdiqlash kodi: $otp_code\n\n"
    "Kod $expires_text ichida amal qiladi.\n"
    "Kodni hech kimga bermang.\n"
    "$note\n"
)
