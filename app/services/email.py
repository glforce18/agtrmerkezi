"""
AGTR Merkezi v5.0 - Email Service
Profesyonel email sablonlari ve gonderim
"""

import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Template dizini
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailService:
    """Email gonderim servisi"""
    
    def __init__(self):
        self.smtp_host = "localhost"
        self.smtp_port = 587
        self.smtp_user = ""
        self.smtp_pass = ""
        self.from_email = "noreply@agtrmerkezi.com"
        self.from_name = "AGTR Merkezi"
        
        # Jinja2 template engine
        if TEMPLATE_DIR.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(TEMPLATE_DIR)),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            self.env = None
    
    def configure(self, host: str, port: int, user: str, password: str, 
                  from_email: str = None, from_name: str = None):
        """SMTP ayarlarini yapilandir"""
        self.smtp_host = host
        self.smtp_port = port
        self.smtp_user = user
        self.smtp_pass = password
        if from_email:
            self.from_email = from_email
        if from_name:
            self.from_name = from_name
    
    def render_template(self, template_name: str, **context) -> str:
        """Email sablonunu render et"""
        if self.env is None:
            # Fallback to inline template
            return self._inline_template(template_name, **context)
        
        try:
            template = self.env.get_template(f"{template_name}.html")
            return template.render(
                year=datetime.utcnow().year,
                site_name="AGTR Merkezi",
                site_url="https://agtrmerkezi.com",
                **context
            )
        except Exception as e:
            logger.error(f"Template render error: {e}")
            return self._inline_template(template_name, **context)
    
    def _inline_template(self, template_name: str, **context) -> str:
        """Inline template (fallback)"""
        base_style = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #16213e; 
                         border-radius: 12px; overflow: hidden; }
            .header { background: linear-gradient(135deg, #ff6b00, #ff8c00); 
                      padding: 30px; text-align: center; }
            .header h1 { margin: 0; color: white; font-size: 28px; }
            .content { padding: 30px; }
            .btn { display: inline-block; background: #ff6b00; color: white; 
                   padding: 12px 30px; text-decoration: none; border-radius: 6px; 
                   font-weight: bold; margin: 20px 0; }
            .footer { text-align: center; padding: 20px; color: #888; font-size: 12px; 
                      border-top: 1px solid #333; }
            .highlight { color: #ff6b00; font-weight: bold; }
        </style>
        """
        
        templates = {
            "welcome": f"""
            <!DOCTYPE html>
            <html>
            <head>{base_style}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎮 AGTR Merkezi'ne Hosgeldiniz!</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba <span class="highlight">{context.get('username', 'Oyuncu')}</span>,</p>
                        <p>AGTR Merkezi ailesine katildiginiz icin tesekkur ederiz!</p>
                        <p>Artik Half-Life ve CS 1.6 sunuculari kiralayabilir, 
                           forumda diger oyuncularla iletisim kurabilirsiniz.</p>
                        <a href="{context.get('panel_url', '#')}" class="btn">Panele Git</a>
                    </div>
                    <div class="footer">
                        <p>&copy; {datetime.utcnow().year} AGTR Merkezi. Tum haklar saklidir.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            "password_reset": f"""
            <!DOCTYPE html>
            <html>
            <head>{base_style}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Sifre Sifirlama</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba <span class="highlight">{context.get('username', 'Kullanici')}</span>,</p>
                        <p>Sifrenizi sifirlamak icin asagidaki butona tiklayin:</p>
                        <a href="{context.get('reset_url', '#')}" class="btn">Sifremi Sifirla</a>
                        <p style="color: #888; font-size: 14px;">
                            Bu link 1 saat icerisinde gecersiz olacaktir.<br>
                            Eger bu istegi siz yapmadiysan, bu emaili gormezden gelebilirsiniz.
                        </p>
                    </div>
                    <div class="footer">
                        <p>&copy; {datetime.utcnow().year} AGTR Merkezi</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            "payment_success": f"""
            <!DOCTYPE html>
            <html>
            <head>{base_style}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💰 Odeme Onaylandi!</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba <span class="highlight">{context.get('username', 'Kullanici')}</span>,</p>
                        <p>Odemeniz basariyla tamamlandi!</p>
                        <table style="width: 100%; margin: 20px 0;">
                            <tr><td>Paket:</td><td class="highlight">{context.get('package_name', '-')}</td></tr>
                            <tr><td>Tutar:</td><td class="highlight">{context.get('amount', '0')} TL</td></tr>
                            <tr><td>Islem No:</td><td>{context.get('transaction_id', '-')}</td></tr>
                        </table>
                        <a href="{context.get('panel_url', '#')}" class="btn">Sunucunu Gor</a>
                    </div>
                    <div class="footer">
                        <p>&copy; {datetime.utcnow().year} AGTR Merkezi</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            "server_expiring": f"""
            <!DOCTYPE html>
            <html>
            <head>{base_style}</head>
            <body>
                <div class="container">
                    <div class="header" style="background: linear-gradient(135deg, #ff6600, #cc5200);">
                        <h1>⏰ Sunucu Suresi Doluyor!</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba <span class="highlight">{context.get('username', 'Kullanici')}</span>,</p>
                        <p><strong>{context.get('server_name', 'Sunucunuz')}</strong> sunucunuzun suresi 
                           <span class="highlight">{context.get('expires_at', 'yakinda')}</span> tarihinde dolacak.</p>
                        <p>Sunucunuzun kapanmamasi icin lutfen sure uzatimi yapin.</p>
                        <a href="{context.get('renew_url', '#')}" class="btn">Simdi Yenile</a>
                    </div>
                    <div class="footer">
                        <p>&copy; {datetime.utcnow().year} AGTR Merkezi</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            "notification": f"""
            <!DOCTYPE html>
            <html>
            <head>{base_style}</head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📢 {context.get('title', 'Bildirim')}</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba <span class="highlight">{context.get('username', 'Kullanici')}</span>,</p>
                        <p>{context.get('message', '')}</p>
                        {f'<a href="{context.get("action_url")}" class="btn">{context.get("action_text", "Detaylar")}</a>' if context.get('action_url') else ''}
                    </div>
                    <div class="footer">
                        <p>&copy; {datetime.utcnow().year} AGTR Merkezi</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        return templates.get(template_name, templates["notification"])
    
    async def send_email(self, to: str, subject: str, html_content: str, 
                         text_content: str = None) -> dict:
        """Email gonder"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to
            
            # Plain text version
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            
            # HTML version
            msg.attach(MIMEText(html_content, "html"))
            
            # Send
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_pass,
                use_tls=True
            )
            
            logger.info(f"Email sent to {to}: {subject}")
            return {"success": True, "to": to}
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_welcome(self, to: str, username: str, panel_url: str = None):
        """Hosgeldin emaili"""
        html = self.render_template("welcome", username=username, 
                                    panel_url=panel_url or "https://agtrmerkezi.com/panel")
        return await self.send_email(to, "AGTR Merkezi'ne Hosgeldiniz! 🎮", html)
    
    async def send_password_reset(self, to: str, username: str, reset_url: str):
        """Sifre sifirlama emaili"""
        html = self.render_template("password_reset", username=username, reset_url=reset_url)
        return await self.send_email(to, "Sifre Sifirlama Talebi 🔐", html)
    
    async def send_payment_success(self, to: str, username: str, package_name: str,
                                   amount: float, transaction_id: str, panel_url: str = None):
        """Odeme onay emaili"""
        html = self.render_template("payment_success", 
                                    username=username,
                                    package_name=package_name,
                                    amount=amount,
                                    transaction_id=transaction_id,
                                    panel_url=panel_url or "https://agtrmerkezi.com/panel")
        return await self.send_email(to, "Odemeniz Onaylandi! 💰", html)
    
    async def send_server_expiring(self, to: str, username: str, server_name: str,
                                   expires_at: str, renew_url: str = None):
        """Sunucu sure uyari emaili"""
        html = self.render_template("server_expiring",
                                    username=username,
                                    server_name=server_name,
                                    expires_at=expires_at,
                                    renew_url=renew_url or "https://agtrmerkezi.com/panel")
        return await self.send_email(to, "Sunucu Sureniz Doluyor! ⏰", html)
    
    async def send_notification(self, to: str, username: str, title: str, 
                                message: str, action_url: str = None, action_text: str = None):
        """Genel bildirim emaili"""
        html = self.render_template("notification",
                                    username=username,
                                    title=title,
                                    message=message,
                                    action_url=action_url,
                                    action_text=action_text)
        return await self.send_email(to, f"{title} - AGTR Merkezi", html)


# Global instance
email_service = EmailService()
