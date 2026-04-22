import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY", "re_TsunmTHM_KRwX41wT26Cd713DS2LoogVD")

FROM_EMAIL = "MotoApp <onboarding@resend.dev>"

def enviar_reset_password(email: str, nombre: str, token: str) -> bool:
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": email,
            "subject": "Recuperar contraseña - MotoApp",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #4A90D9;">MotoApp 🏍️</h2>
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>Recibimos una solicitud para recuperar tu contraseña.</p>
                <p>Tu código de verificación es:</p>
                <div style="background: #f4f4f4; padding: 20px; text-align: center; 
                            font-size: 32px; font-weight: bold; letter-spacing: 8px;
                            border-radius: 8px; color: #4A90D9;">
                    {token}
                </div>
                <p style="color: #666;">Este código expira en <strong>15 minutos</strong>.</p>
                <p style="color: #666;">Si no solicitaste esto, ignora este correo.</p>
                <hr style="border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">MotoApp — Gestión de mantenimiento</p>
            </div>
            """,
        })
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def enviar_bienvenida(email: str, nombre: str) -> bool:
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": email,
            "subject": "Bienvenido a MotoApp 🏍️",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #4A90D9;">¡Bienvenido a MotoApp! 🏍️</h2>
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>Tu cuenta ha sido creada exitosamente.</p>
                <p>Ya puedes gestionar el mantenimiento de tu moto desde la app.</p>
                <hr style="border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">MotoApp — Gestión de mantenimiento</p>
            </div>
            """,
        })
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
