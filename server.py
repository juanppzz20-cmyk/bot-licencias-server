from flask import Flask, request, jsonify
import sqlite3
import datetime
import uuid

app = Flask(__name__)
conn = sqlite3.connect('keys.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS keys 
             (key TEXT, status TEXT, pc_id TEXT, expiry DATE)''')
conn.commit()

@app.route('/validar', methods=['POST'])
def validar():
    data = request.json
    key = data['key']
    pc_id = data['pc_id']
    c.execute("SELECT * FROM keys WHERE key=?", (key,))
    result = c.fetchone()
    if not result: return jsonify({"status": "error", "msg": "KEY no existe"})
    status, db_pc_id, expiry = result[1], result[2], result[3]
    if status == "banned": return jsonify({"status": "error", "msg": "KEY baneada"})
    if datetime.datetime.now().date() > datetime.datetime.strptime(expiry, '%Y-%m-%d').date():
        return jsonify({"status": "error", "msg": "KEY expirada. Renueva por $30"})
    if db_pc_id == "":
        c.execute("UPDATE keys SET pc_id=? WHERE key=?", (pc_id, key))
        conn.commit()
        return jsonify({"status": "ok", "msg": f"Activada. Vence: {expiry}"})
    if db_pc_id!= pc_id: return jsonify({"status": "error", "msg": "KEY ya en otra PC"})
    return jsonify({"status": "ok", "msg": f"Válida. Vence: {expiry}"})

@app.route('/generar_key')
def generar():
    new_key = str(uuid.uuid4()).upper()[:19]
    expiry = (datetime.datetime.now() + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
    c.execute("INSERT INTO keys VALUES (?, 'active', '',?)", (new_key, expiry))
    conn.commit()
    return f"KEY: {new_key} | $30 | Vence: {expiry}"

app.run(host='0.0.0.0', port=10000)