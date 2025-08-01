from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_FILE = 'clientes.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
    return render_template('clientes.html', clientes=clientes)

@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        deuda = float(request.form['deuda'])
        frecuencia_pago = request.form['frecuencia_pago']
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nombre, deuda, frecuencia_pago)
                VALUES (?, ?, ?)
            ''', (nombre, deuda, frecuencia_pago))
            conn.commit()
        return redirect(url_for('clientes'))
    return render_template('registrar_cliente.html')

@app.route('/registrar_pago', methods=['GET', 'POST'])
def registrar_pago():
    # Aquí puedes implementar la lógica para registrar pagos
    if request.method == 'POST':
        # Procesar pago
        pass
    return render_template('registrar_pago.html')

@app.route('/informe_pagos')
def informe_pagos():
    # Aquí puedes implementar la lógica para mostrar informe de pagos
    return render_template('informe_pagos.html')

if __name__ == '__main__':
    app.run(debug=True)
