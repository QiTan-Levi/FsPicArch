from flask import Flask, send_from_directory, request, jsonify
import os
 
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 
@app.route('/pic/<filename>')
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
 
if __name__ == '__main__':
    app.run(debug=True)