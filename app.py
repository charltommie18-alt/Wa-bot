
from flask import Flask, send_from_directory, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

@app.route('/api/lead', methods=['POST'])
def lead():
    try:
        data = request.get_json()
        print("NEW LEAD:", data)
        # TODO: Save to Supabase here
        return jsonify({"status":"ok","saved":True})
    except Exception as e:
        return jsonify({"status":"error","msg":str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
