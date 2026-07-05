from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/check_key.')
def clave_de_verificacion():
    llave = request.args.get('llave', '')
    telegram_id = request.args.get('id', '')
    
    if not llave or not telegram_id:
        return jsonify({"estado":"error","mensaje":"Falta llave o id"})
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, estado, fecha_vencimiento, telegram_id FROM keys WHERE key = %s", (llave,))
    key_data = cur.fetchone()
    
    if not key_data:
        cur.close(); conn.close()
        return jsonify({"estado":"error","mensaje":"KEY invalida"})
    
    key_id, estado, fecha_vence, id_guardado = key_data
    hoy = datetime.now().date()
    
    if estado == 'used':
        if str(id_guardado) == telegram_id:
            if hoy > fecha_vence:
                cur.close(); conn.close()
                return jsonify({"estado":"error","mensaje":"KEY vencida el " + str(fecha_vence)})
            return jsonify({"estado":"OK","mensaje":"Licencia válida. Vence: " + str(fecha_vence)})
        else:
            cur.close(); conn.close()
            return jsonify({"estado":"error","mensaje":"Esta key ya está en uso en otra cuenta"})
    
    if estado == 'active':
        fecha_vence_nueva = hoy + timedelta(days=15)
        cur.execute("UPDATE keys SET estado = 'used', telegram_id = %s, fecha_activacion = %s, fecha_vencimiento = %s WHERE id = %s", (telegram_id, hoy, fecha_vence_nueva, key_id))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"estado":"OK","mensaje":"Activada. Vence: " + str(fecha_vence_nueva)})
    
    cur.close(); conn.close()
    return jsonify({"estado":"error","mensaje":"KEY invalida"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
