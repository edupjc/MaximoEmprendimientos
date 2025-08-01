from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('clientes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear tablas si no existen
def crear_tablas():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            deuda_total REAL DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            monto REAL,
            fecha TEXT,
            forma_pago TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    ''')
    conn.commit()
    conn.close()

crear_tablas()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ver clientes
@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

# Registrar cliente nuevo
@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        deuda = float(request.form['deuda'])

        conn = get_db_connection()
        conn.execute('INSERT INTO clientes (nombre, telefono, deuda_total) VALUES (?, ?, ?)',
                     (nombre, telefono, deuda))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    return render_template('registrar_cliente.html')

# Registrar pago
@app.route('/registrar_pago', methods=['GET', 'POST'])
def registrar_pago():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        monto = float(request.form['monto'])
        forma_pago = request.form['forma_pago']
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn.execute('INSERT INTO pagos (cliente_id, monto, fecha, forma_pago) VALUES (?, ?, ?, ?)',
                     (cliente_id, monto, fecha, forma_pago))
        conn.execute('UPDATE clientes SET deuda_total = deuda_total - ? WHERE id = ?',
                     (monto, cliente_id))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    conn.close()
    return render_template('registrar_pago.html', clientes=clientes)

# Informe de pagos
@app.route('/informe_pagos')
def informe_pagos():
    conn = get_db_connection()
    pagos = conn.execute('''
        SELECT p.*, c.nombre 
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.fecha DESC
    ''').fetchall()
    conn.close()
    return render_template('informe_pagos.html', pagos=pagos)

# Iniciar app con configuración para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
