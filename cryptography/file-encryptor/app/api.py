# app/api.py
from flask import Flask, request, send_file
import os
from app.crypto import encrypt_file, decrypt_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'

@app.route('/encrypt', methods=['POST'])
def api_encrypt():
    if 'file' not in request.files:
        return {"error": "Файл не передан"}, 400
    file = request.files['file']
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_' + file.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted_' + file.filename)
    file.save(input_path)

    try:
        encrypt_file(input_path, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/decrypt', methods=['POST'])
def api_decrypt():
    if 'file' not in request.files:
        return {"error": "Файл не передан"}, 400
    file = request.files['file']
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'enc_' + file.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dec_' + file.filename)
    file.save(input_path)

    try:
        decrypt_file(input_path, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    os.makedirs("keys", exist_ok=True)
    if not os.path.exists("keys/private_key.pem"):
        from app.crypto import generate_rsa_keys
        generate_rsa_keys()
    app.run(host="0.0.0.0", port=5000)