from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app as app

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se encontró el archivo.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Ningún archivo seleccionado.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Procesar CSV o JSON con pandas
                if filename.endswith('.csv') or filename.endswith('.txt'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_json(filepath)

                summary = {
                    "columnas": list(df.columns),
                    "shape": df.shape,
                    "tipos": df.dtypes.astype(str).to_dict()
                }

            except Exception as e:
                flash(f"Error procesando archivo: {str(e)}")
                return redirect(url_for('main.upload_file'))

            return render_template('summary.html', filename=filename, summary=summary)

        flash('Formato de archivo no permitido.')
        return redirect(request.url)

    return render_template('upload.html')
