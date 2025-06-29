from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app as app

from .models import UploadedFile
from . import db

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv', 'json', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/historial')
def historial():
    archivos = UploadedFile.query.order_by(UploadedFile.upload_date.desc()).all()
    return render_template('historial.html', archivos=archivos)

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se encontró el archivo.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se seleccionó ningún archivo.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # ✅ Definimos filename antes del bloque try
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # ✅ Procesamos el archivo
                if filename.endswith('.csv') or filename.endswith('.txt'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_json(filepath)

                summary = {
                    "columnas": list(df.columns),
                    "shape": df.shape,
                    "tipos": df.dtypes.astype(str).to_dict()
                }

                # ✅ Guardamos en la base de datos
                uploaded = UploadedFile(
                    filename=filename,
                    num_rows=df.shape[0],
                    num_columns=df.shape[1]
                )
                db.session.add(uploaded)
                db.session.commit()

                return render_template('summary.html', filename=filename, summary=summary)

            except Exception as e:
                flash(f"Error procesando archivo: {str(e)}")
                return redirect(url_for('main.upload_file'))

        else:
            flash('Formato de archivo no permitido.')
            return redirect(request.url)

    return render_template('upload.html')
    
@main.route('/archivo/<int:archivo_id>')
def ver_detalle(archivo_id):
    archivo = UploadedFile.query.get_or_404(archivo_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)

    try:
        # Cargar archivo
        if archivo.filename.endswith('.csv') or archivo.filename.endswith('.txt'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_json(filepath)

        # Obtener primeras filas
        preview = df.head(10).to_html(classes='tabla', index=False)

        # Obtener estadísticas
        stats = df.describe().to_html(classes='tabla', index=True)

        # Generar datos para un gráfico
        # Elegimos la primera columna categórica o numérica
        col = df.select_dtypes(include=['object', 'int', 'float']).columns[0]
        chart_data = df[col].value_counts().head(5)

        labels = [str(label) for label in chart_data.index]
        values = [int(value) for value in chart_data.values]

        return render_template(
            'detalle.html',
            archivo=archivo,
            preview=preview,
            stats=stats,
            chart_labels=labels,
            chart_values=values,
            col=col
        )

    except Exception as e:
        flash(f"Error al procesar el archivo: {e}")
        return redirect(url_for('main.historial'))
