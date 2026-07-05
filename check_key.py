from flask import Flask, request, jsonify
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/check_key')
def clave_de_verificacion():
    llave = request.args.get('llave')
    telegram_id = request.args.get('id')

    if not llave or not telegram_id:
        return jsonify({"estado": "ERROR", "mensaje": "Faltan parametros"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        # 1. Buscar la llave
        cur.execute("SELECT * FROM licencias WHERE clave = %s", (llave,))
        licencia = cur.fetchone()

        if not licencia:
            return jsonify({"estado": "ERROR", "mensaje": "KEY invalida"})

        # licencia = (id, clave, estado, fecha_vencimiento, telegram_id)
        estado_db = licencia[2]
        fecha_venc = licencia[3]
        id_asignado = licencia[4]

        # 2. Si esta inactiva
        if estado_db == 'INACTIVA':
            nueva_fecha = datetime.now() + timedelta(days=30)
            cur.execute("UPDATE licencias SET estado = 'ACTIVA', fecha_vencimiento = %s, telegram_id = %s WHERE clave = %s", 
                        (nueva_fecha, telegram_id, llave))
            conn.commit()
            return jsonify({"estado": "OK", "mensaje": f"Activada. Vence: {nueva_fecha.strftime('%Y-%m-%d')}"})

        # 3. Si ya esta activa
        if estado_db == 'ACTIVA':
            # Si es el mismo usuario
            if str(id_asignado) == str(telegram_id):
                if datetime.now() > fecha_venc:
                    return jsonify({"estado": "EXPIRADA", "mensaje": "Tu licencia expiro. Compra otra."})
                else:
                    return jsonify({"estado": "OK", "mensaje": f"Licencia valida. Vence: {fecha_venc.strftime('%Y-%m-%d')}"})
            else:
                return jsonify({"estado": "ERROR", "mensaje": "Esta KEY ya esta en uso por otra cuenta"})
        
        # 4. Si esta baneada
        if estado_db == 'BAN':
            return jsonify({"estado": "BAN", "mensaje": "Esta licencia fue baneada"})

    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": f"Error de servidor: {str(e)}"}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
