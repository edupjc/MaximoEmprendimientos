from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave-secreta'

DB = 'database.db'

# 🔧 Inicializa las tablas si no existen
def init_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                cedula TEXT PRIMARY KEY,
                nombre TEXT,
                apellido TEXT,
                direccion TEXT,
                telefono TEXT,
                deuda_total REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT,
                fecha TEXT,
                monto REAL,
                tipo TEXT,
                FOREIGN KEY (cedula) REFERENCES clientes(cedula)
            )
        ''')

# 🏠 Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# 📋 Lista de clientes (acepta /clientes y /clientes/)
@app.route('/clientes/')
@app.route('/clientes')
def clientes():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    lista = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=lista)

# ➕ Agregar cliente
@app.route('/agregar/', methods=['GET', 'POST'])
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        data = (
            request.form['cedula'],
            request.form['nombre'].title(),
            request.form['apellido'].title(),
            request.form['direccion'],
            request.form['telefono'],
            float(request.form['deuda']),
        )
        try:
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO clientes (cedula, nombre, apellido, direccion, telefono, deuda_total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', data)
                flash("✅ Cliente agregado correctamente", "success")
        except sqlite3.IntegrityError:
            flash("❌ Ya existe un cliente con esa cédula", "danger")
        return redirect(url_for('clientes'))
    return render_template('agregar_cliente.html')

# 💰 Registrar pago
@app.route('/pago/', methods=['GET', 'POST'])
@app.route('/pago', methods=['GET', 'POST'])
def pago():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT cedula, nombre || ' ' || apellido FROM clientes")
    clientes = cursor.fetchall()
    
    if request.method == 'POST':
        cedula = request.form['cedula']
        monto = float(request.form['monto'])
        tipo = request.form['tipo']
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("SELECT deuda_total FROM clientes WHERE cedula = ?", (cedula,))
        resultado = cursor.fetchone()

        if not resultado:
            flash("❌ Cliente no encontrado", "danger")
            return redirect(url_for('pago'))

        deuda_actual = resultado[0]
        if monto > deuda_actual:
            monto = deuda_actual

        # Insertar el pago
        cursor.execute('''
            INSERT INTO pagos (cedula, fecha, monto, tipo)
            VALUES (?, ?, ?, ?)
        ''', (cedula, fecha, monto, tipo))

        # Actualizar deuda
        cursor.execute("UPDATE clientes SET deuda_total = ? WHERE cedula = ?", (deuda_actual - monto, cedula))
        conn.commit()
        conn.close()

        flash("💰 Pago registrado correctamente", "success")
        return redirect(url_for('clientes'))

    conn.close()
    return render_template('registrar_pago.html', clientes=clientes)

# 📄 Informe de pagos por cliente
@app.route('/informe/', methods=['GET', 'POST'])
@app.route('/informe', methods=['GET', 'POST'])
def informe():
    pagos = []
    cliente = None
    if request.method == 'POST':
        cedula = request.form['cedula']
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, apellido, deuda_total FROM clientes WHERE cedula = ?", (cedula,))
        cliente = cursor.fetchone()

        if not cliente:
            flash("❌ Cliente no encontrado", "danger")
        else:
            cursor.execute("SELECT fecha, monto, tipo FROM pagos WHERE cedula = ? ORDER BY fecha", (cedula,))
            pagos = cursor.fetchall()

        conn.close()
    return render_template('informe_pagos.html', cliente=cliente, pagos=pagos)

# 🚀 Iniciar aplicación
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
