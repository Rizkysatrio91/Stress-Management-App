from flask import Flask, render_template, request, send_file, flash, redirect, url_for # Mengimpor pustaka Flask untuk membuat aplikasi web
import joblib   # Mengimpor pustaka joblib untuk memuat atau menyimpan model machine learning
import logging  # Mengimpor pustaka logging untuk mencatat log atau debug informasi
import numpy as np  # Mengimpor pustaka NumPy untuk melakukan operasi matematika atau array
import sqlite3  # Mengimpor pustaka sqlite3 untuk berinteraksi dengan database SQLite
import csv  # Mengimpor pustaka csv untuk membaca atau menulis file CSV

# Konfigurasi logging untuk mencatat informasi debugging
logging.basicConfig(level=logging.DEBUG)

# Inisialisasi Flask app
app = Flask(__name__)
app.secret_key = 'a_very_secret_key_12345'  
# app.secret_key digunakan untuk mengamankan data sesi, perlindungan CSRF, 
# dan integritas pesan flash. Kunci ini harus rahasia, panjang, dan acak.

# Path ke model yang sudah dilatih dan database
MODEL_PATH = 'stress_level_model.pkl'  # Path model
DATABASE = 'stress_results.db'  # Path database

# Fungsi untuk memuat model dari file
def load_model(model_path):
    try:
        model = joblib.load(model_path)  # Muat model menggunakan joblib
        logging.info("Model loaded successfully.")  # Log jika berhasil
        return model
    except FileNotFoundError:
        logging.error("Model file not found. Ensure the path is correct.")  # Log jika file tidak ditemukan
        return None
    except Exception as e:
        logging.error(f"Error loading model: {e}")  # Log jika terjadi error lain
        return None

# Fungsi untuk inisialisasi database SQLite
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Buat tabel jika belum ada untuk menyimpan hasil cek stres
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stress_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                anxiety_level INTEGER NOT NULL,
                depression INTEGER NOT NULL,
                sleep_quality INTEGER NOT NULL,
                study_load INTEGER NOT NULL,
                future_career_concerns INTEGER NOT NULL,
                peer_pressure INTEGER NOT NULL,
                bullying INTEGER NOT NULL,
                stress_level TEXT NOT NULL
            )
        ''')
        conn.commit()  # Simpan perubahan

# Fungsi untuk menyimpan hasil ke database
def save_to_db(name, input_data, stress_level):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Masukkan data ke tabel stress_results
        cursor.execute('''
            INSERT INTO stress_results (
                name, anxiety_level, depression, sleep_quality, study_load,
                future_career_concerns, peer_pressure, bullying, stress_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, *input_data, stress_level))
        conn.commit()  # Simpan perubahan

# Fungsi untuk mengambil semua data dari database
def fetch_all_results():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Ambil semua data dari tabel stress_results
        cursor.execute('''
            SELECT id, name, anxiety_level, depression, sleep_quality, study_load,
                   future_career_concerns, peer_pressure, bullying, stress_level
            FROM stress_results
        ''')
        return cursor.fetchall()  # Kembalikan data dalam bentuk list

# Fungsi untuk menghapus data berdasarkan ID
def delete_result(result_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Hapus data dengan ID tertentu
        cursor.execute('DELETE FROM stress_results WHERE id = ?', (result_id,))
        conn.commit()  # Simpan perubahan

# Fungsi untuk mengekspor data hasil cek ke file CSV
def export_to_csv():
    results = fetch_all_results()  # Ambil semua data dari database
    csv_file = 'stress_results.csv'  # Nama file CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Tulis header kolom
        writer.writerow([
            'ID', 'Name', 'Anxiety Level', 'Depression', 'Sleep Quality', 'Study Load',
            'Future Career Concerns', 'Peer Pressure', 'Bullying', 'Stress Level'
        ])
        # Tulis data
        writer.writerows(results)
    return csv_file  # Kembalikan nama file

# Muat model saat aplikasi dimulai
model = load_model(MODEL_PATH)

# Daftar fitur yang digunakan dalam model
FEATURE_NAMES = [
    'anxiety_level', 'depression', 'sleep_quality', 'study_load',
    'future_career_concerns', 'peer_pressure', 'bullying'
]

# Fungsi untuk menghitung tingkat stres menggunakan model
def calculate_stress_level_with_model(form_data, model):
    input_data = []

    # Ambil dan validasi setiap fitur input
    for feature in FEATURE_NAMES:
        value = form_data.get(feature)
        if value not in {'0', '1', '2'}:  # Validasi kategori (0, 1, atau 2)
            raise ValueError(f"Invalid input for {feature}. Must be 0, 1, or 2.")
        input_data.append(int(value))  # Konversi ke integer

    # Log input data untuk debugging
    logging.debug(f"Input data for prediction: {input_data}")

    # Pastikan model sudah dimuat
    if model is None:
        raise ValueError("Model is not loaded or unavailable.")

    # Hitung prediksi tingkat stres menggunakan logika rata-rata
    manual_logic_prediction = np.mean(input_data)  # Hitung rata-rata
    if manual_logic_prediction <= 0.5:
        stress_level = 0  # Rendah
    elif manual_logic_prediction <= 1.5:
        stress_level = 1  # Sedang
    else:
        stress_level = 2  # Tinggi

    # Log hasil prediksi
    logging.debug(f"Manual logic prediction result: {stress_level}")

    # Map hasil prediksi ke label tingkat stres
    stress_mapping = {
        0: "rendah",
        1: "sedang",
        2: "tinggi"
    }

    # Kembalikan hasil dengan label
    result = stress_mapping.get(stress_level, "tidak diketahui")
    logging.debug(f"Mapped prediction result: {result}")
    return result, stress_level  # Kembalikan hasil prediksi dan tingkat stres



# Routes


@app.route('/stress-check', methods=['GET', 'POST'])
def stress_check():
    # Inisialisasi variabel untuk hasil, nama mahasiswa, pesan error, rotasi jarum, dan kelas jarum
    result = None
    student_name = None
    error_message = None
    indicator_rotation = -90  # Posisi awal jarum untuk tingkat stres "rendah"
    needle_class = ""  # Default kelas CSS untuk jarum

    # Cek apakah metode POST digunakan
    if request.method == 'POST':
        try:
            # Ambil nama mahasiswa dan input fitur dari form
            student_name = request.form.get('name', "Anonymous").strip()
            input_data = [int(request.form.get(feature, 0)) for feature in FEATURE_NAMES]

            # Validasi input: pastikan semua nilai berada di rentang 0-2
            if any(value not in {0, 1, 2} for value in input_data):
                raise ValueError("Semua input harus memiliki nilai 0, 1, atau 2.")

            # Hitung tingkat stres menggunakan model
            result, stress_indicator = calculate_stress_level_with_model(request.form, model)

            # Hitung sudut rotasi jarum berdasarkan tingkat stres
            indicator_rotation = -90 + (stress_indicator * 90)  # -90 untuk rendah, 0 untuk sedang, +90 untuk tinggi

            # Tentukan kelas CSS jarum berdasarkan hasil tingkat stres
            if stress_indicator == 0:
                needle_class = "low-stress"  # Kelas untuk tingkat stres "rendah"
            elif stress_indicator == 1:
                needle_class = "medium-stress"  # Kelas untuk tingkat stres "sedang"
            elif stress_indicator == 2:
                needle_class = "high-stress"  # Kelas untuk tingkat stres "tinggi"

            # Simpan hasil ke database
            save_to_db(student_name, input_data, result)

            # Log hasil untuk debugging
            logging.debug(f"Nama mahasiswa: {student_name}")
            logging.debug(f"Input data: {input_data}")
            logging.debug(f"Hasil tingkat stres: {result}")
            logging.debug(f"Stress Indicator: {stress_indicator}")
            logging.debug(f"Sudut rotasi jarum: {indicator_rotation}")
            logging.debug(f"Kelas CSS yang diterapkan: {needle_class}")

        except ValueError as ve:
            # Tangani kesalahan validasi input
            logging.error(f"Input validation error: {ve}")
            error_message = f"Kesalahan Input: {ve}"
        except Exception as e:
            # Tangani kesalahan lain
            logging.error(f"Unexpected error: {e}")
            error_message = f"Terjadi kesalahan: {e}"

    # Render template HTML dengan hasil dan informasi terkait
    return render_template(
        'stress_check.html',
        result=result,  # Hasil tingkat stres
        student_name=student_name,  # Nama mahasiswa
        error_message=error_message,  # Pesan error jika ada
        indicator_rotation=indicator_rotation,  # Sudut jarum
        needle_class=needle_class  # Kelas CSS jarum
    )




@app.route('/')
def halaman_utama():
    return render_template('halaman_utama.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/data-hasil-cek')
def data_hasil_cek():
    # Ambil data dari database
    hasil_cek = fetch_all_results()
    return render_template('data_hasil_cek.html', hasil_cek=hasil_cek)

@app.route('/delete-result/<int:result_id>', methods=['POST'])
def delete_result_route(result_id):
    try:
        delete_result(result_id)
        logging.info(f"Deleted result with ID: {result_id}")
        flash("Data berhasil dihapus.", "success")  # Pesan sukses
        return redirect(url_for('data_hasil_cek'))  # Redirect ke halaman data hasil cek
    except Exception as e:
        logging.error(f"Error deleting result with ID {result_id}: {e}")
        flash("Terjadi kesalahan saat menghapus data.", "danger")  # Pesan error
        return redirect(url_for('data_hasil_cek'))

@app.route('/export-csv')
def export_csv():
    # Ekspor data ke CSV
    csv_file = export_to_csv()
    return send_file(csv_file, as_attachment=True)


@app.route('/stress-tips')
def stress_tips():
    return render_template('stress_tips.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Tambahan route untuk halaman olahraga
@app.route('/olahraga')
def olahraga():
    return render_template('olahraga.html')

# Tambahan route untuk halaman meditasi
@app.route('/meditasi')
def meditasi():
    return render_template('meditasi.html')

# Tambahan route untuk halaman jaga pola tidur
@app.route('/jaga_pola_tidur')
def jaga_pola_tidur():
    return render_template('jaga_pola_tidur.html')

@app.route('/berkumpul_dengan_teman_dan_keluarga')
def berkumpul_dengan_teman_dan_keluarga():
    return render_template('berkumpul_dengan_teman_dan_keluarga.html')

@app.route('/multitasking')
def multitasking():
    return render_template('multitasking.html')





# Main program
if __name__ == '__main__':
    init_db()  # Inisialisasi database dan buat tabel jika belum ada
    app.run(debug=True)

