from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Base de datos
DB_FILE = 'clientes.db'

def crear_tabla():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT,
                telefono TEXT,
                direccion TEXT,
                deuda_total REAL DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                fecha TEXT,
                monto REAL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')

crear_tabla()

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
        cedula = request.form['cedula']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        deuda = float(request.form['deuda'])

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nombre, cedula, telefono, direccion, deuda_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, cedula, telefono, direccion, deuda))
            conn.commit()
        return redirect(url_for('clientes'))
    return render_template('registrar_cliente.html')

@app.route('/registrar_pago/<int:cliente_id>', methods=['GET', 'POST'])
def registrar_pago(cliente_id):
    if request.method == 'POST':
        fecha = request.form['fecha']
        monto = float(request.form['monto'])

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pagos (cliente_id, fecha, monto) VALUES (?, ?, ?)", (cliente_id, fecha, monto))
            cursor.execute("UPDATE clientes SET deuda_total = deuda_total - ? WHERE id = ?", (monto, cliente_id))
            conn.commit()
        return redirect(url_for('clientes'))

    return render_template('registrar_pago.html', cliente_id=cliente_id)

@app.route('/informe_pagos/<int:cliente_id>')
def informe_pagos(cliente_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()

        cursor.execute("SELECT fecha, monto FROM pagos WHERE cliente_id = ?", (cliente_id,))
        pagos = cursor.fetchall()
    return render_template('informe_pagos.html', cliente=cliente, pagos=pagos)

# 👇 Esto es lo que Render necesita para detectar el puerto dinámicamente
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
