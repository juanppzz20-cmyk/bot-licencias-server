from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db():
    DATABASE_URL = os.environ['DATABASE_URL']
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        # Crea la tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS licencias (
                id SERIAL PRIMARY KEY,
                clave VARCHAR(50) UNIQUE NOT NULL,
                estado VARCHAR(20) DEFAULT 'INACTIVA',
                fecha_vencimiento TIMESTAMP,
                telegram_id BIGINT
            );
        """)
        # Mete key de prueba si no existe
        cur.execute("INSERT INTO licencias (clave, estado) VALUES ('BT-VIP-001-2026', 'INACTIVA') ON CONFLICT (clave) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
        print("DB Inicializada correctamente")
    except Exception as e:
        print(f"Error init_db: {e}")

# INICIALIZAR DB AL ARRANCAR
init_db()

@app.route('/check_key')
def check_key():
    try:
        llave = request.args.get('llave')
        telegram_id = request.args.get('id')
        
        if not llave or not telegram_id:
            return jsonify({"estado": "ERROR", "mensaje": "Faltan parametros"})
            
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT estado, fecha_vencimiento FROM licencias WHERE clave = %s", (llave,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({"estado": "INVALIDA", "mensaje": "La clave no existe"})
            
        estado, fecha_vencimiento = result
        
        if estado == 'INACTIVA':
            nueva_fecha = datetime.now() + timedelta(days=30)
            cur.execute("UPDATE licencias SET estado = 'ACTIVA', fecha_vencimiento = %s, telegram_id = %s WHERE clave = %s",
                        (nueva_fecha, telegram_id, llave))
            conn.commit()
            return jsonify({"estado": "OK", "mensaje": f"Activada. Vence: {nueva_fecha.strftime('%Y-%m-%d')}"})
        
        elif estado == 'ACTIVA':
            if fecha_vencimiento and fecha_vencimiento > datetime.now():
                return jsonify({"estado": "OK", "mensaje": f"Ya esta activa. Vence: {fecha_vencimiento.strftime('%Y-%m-%d')}"})
            else:
                return jsonify({"estado": "EXPIRADA", "mensaje": "La licencia ya expiro"})
                
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)})
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    app.run()
