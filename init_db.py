# init_db.py

from app import create_app, db
from app.models import UploadedFile

# Inicializamos la app
app = create_app()

# Activamos el contexto de aplicación (para que db funcione)
with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")
