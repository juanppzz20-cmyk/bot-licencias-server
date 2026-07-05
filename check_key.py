from flask import Flask, request, jsonify

app = Flask(__name__)

# AQUI METES TODAS LAS KEYS QUE VENDAS
KEYS_VALIDAS = [
   "BT-VIP-001-2026",
    "BT-VIP-002-2026",
    "BT-VIP-003-2026",
    "BT-VIP-004-2026",
    "BT-VIP-005-2026",
    "BT-VIP-006-2026",
    "BT-VIP-007-2026",
    "BT-VIP-008-2026",
    "BT-VIP-009-2026",
    "BT-VIP-010-2026",
    "BT-PRO-011-2026",
    "BT-PRO-012-2026",
    "BT-PRO-013-2026",
    "BT-PRO-014-2026",
    "BT-PRO-015-2026",
    "BT-PRO-016-2026",
    "BT-PRO-017-2026",
    "BT-PRO-018-2026",
    "BT-PRO-019-2026",
    "BT-PRO-020-2026"
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
