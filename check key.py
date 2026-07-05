from flask import Flask, request, jsonify

app = Flask(__name__)

# AQUI METES TODAS LAS KEYS QUE VENDAS
KEYS_VALIDAS = [
    "BC61DF6E-56F5-47FF-AAAA-BBBB", # KEY de prueba 1
    "12345678-90AB-CDEF-1234-567890" # KEY de prueba 2
]

@app.route('/check_key.php')  # <- lo dejamos igual para que tu bot no cambie
def check_key():
    key = request.args.get('key', '')
    
    if key in KEYS_VALIDAS:
        return jsonify({"status": "ok", "msg": "Licencia valida"})
    else:
        return jsonify({"status": "error", "msg": "KEY invalida"})

if __name__ == '__main__':
    app.run()