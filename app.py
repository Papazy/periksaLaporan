from flask import Flask, render_template, request, send_from_directory
import subprocess # Untuk menjalankan skrip eksternal
import os

app = Flask(__name__)

# Direktori untuk menyimpan file yang diunggah dan hasil
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Pastikan folder ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/periksa', methods=['POST'])
def periksa():
    # Ambil input dari form (misalnya, teks)
    teks_laporan = request.form['laporan']

    # Simpan teks ke file sementara
    input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'laporan.txt')
    with open(input_file_path, 'w', encoding='utf-8') as f:
        f.write(teks_laporan)

    # Jalankan skrip periksaLaporan.py
    # (Asumsikan skrip Anda bisa menerima path file sebagai argumen)
    # Anda mungkin perlu memodifikasi periksaLaporan.py untuk ini
    hasil_pdf_path = os.path.join(app.config['RESULT_FOLDER'], 'hasil_pemeriksaan.pdf')
    subprocess.run(['python', 'periksaLaporan.py', input_file_path, hasil_pdf_path])

    # Arahkan ke halaman hasil
    return render_template('hasil.html', filename='hasil_pemeriksaan.pdf')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)