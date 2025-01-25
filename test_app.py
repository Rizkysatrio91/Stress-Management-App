import pytest
from app import app, init_db, calculate_stress_level_with_model, model

# Fixture untuk membuat test client Flask
# Test client memungkinkan pengujian rute dan respons tanpa memulai server Flask sebenarnya
@pytest.fixture
def client():
    """Fixture untuk membuat test client Flask."""
    app.config['TESTING'] = True  # Aktifkan mode testing Flask
    app.config['WTF_CSRF_ENABLED'] = False  # Matikan CSRF untuk kemudahan pengujian
    init_db()  # Pastikan database telah diinisialisasi sebelum pengujian
    with app.test_client() as client:
        yield client  # Kembalikan test client untuk digunakan dalam tes

# Pengujian rute utama ("/")
def test_home_route(client):
    """Tes apakah rute / berfungsi dengan benar."""
    response = client.get('/')  # Kirim permintaan GET ke rute "/"
    assert response.status_code == 200  # Pastikan respons berhasil (kode status 200)
    assert b"Masuk" in response.data  # Periksa apakah teks "Masuk" ada di data respons (untuk memverifikasi tampilan halaman)

# Pengujian akses GET ke rute "/stress-check"
def test_stress_check_get(client):
    """Tes akses GET ke rute /stress-check."""
    response = client.get('/stress-check')  # Kirim permintaan GET ke rute "/stress-check"
    assert response.status_code == 200  # Pastikan respons berhasil (kode status 200)
    assert b"Cek Tingkat Stress" in response.data  # Periksa apakah teks "Cek Tingkat Stress" dirender dengan benar

# Pengujian akses POST ke rute "/stress-check" dengan data valid
def test_stress_check_post(client):
    """Tes akses POST ke rute /stress-check dengan data yang valid."""
    # Data input untuk simulasi form
    data = {
        'name': 'Test User',  # Nama mahasiswa
        'anxiety_level': '1',
        'depression': '1',
        'sleep_quality': '1',
        'study_load': '1',
        'future_career_concerns': '1',
        'peer_pressure': '1',
        'bullying': '1'
    }
    response = client.post('/stress-check', data=data, follow_redirects=True)  # Kirim permintaan POST dengan data
    assert response.status_code == 200  # Pastikan respons berhasil
    assert b"Test User" in response.data  # Verifikasi nama yang diinput muncul dalam respons
    assert b"sedang" in response.data  # Pastikan prediksi tingkat stres adalah "sedang"

# Pengujian akses POST ke rute "/stress-check" dengan data tidak valid
def test_stress_check_post_invalid(client):
    """Tes akses POST ke rute /stress-check dengan data tidak valid."""
    # Data input tidak valid (anxiety_level = 3, di luar rentang yang diperbolehkan)
    data = {
        'name': 'Test User',
        'anxiety_level': '3',  # Nilai tidak valid
        'depression': '1',
        'sleep_quality': '1',
        'study_load': '1',
        'future_career_concerns': '1',
        'peer_pressure': '1',
        'bullying': '1'
    }
    response = client.post('/stress-check', data=data, follow_redirects=True)  # Kirim permintaan POST dengan data tidak valid
    assert response.status_code == 200  # Pastikan respons berhasil
    assert b"Kesalahan Input" in response.data  # Periksa apakah pesan error validasi ditampilkan

# Pengujian fungsi ekspor data ke file CSV
def test_export_csv(client):
    """Tes apakah fungsi ekspor CSV berfungsi dengan benar."""
    response = client.get('/export-csv')  # Kirim permintaan GET ke rute "/export-csv"
    assert response.status_code == 200  # Pastikan respons berhasil
    assert response.headers['Content-Disposition'].startswith('attachment;')  # Periksa apakah file diunduh sebagai lampiran
    assert response.headers['Content-Type'] in ['text/csv', 'application/vnd.ms-excel']  # Periksa tipe konten file adalah CSV

# Pengujian fungsi `calculate_stress_level_with_model`
def test_calculate_stress_level_with_model():
    """Tes fungsi calculate_stress_level_with_model dengan input valid."""
    # Data input yang valid
    form_data = {
        'anxiety_level': '1',
        'depression': '1',
        'sleep_quality': '1',
        'study_load': '1',
        'future_career_concerns': '1',
        'peer_pressure': '1',
        'bullying': '1'
    }
    # Panggil fungsi dengan data input dan model
    result, stress_indicator = calculate_stress_level_with_model(form_data, model)
    assert result in ["rendah", "sedang", "tinggi"]  # Pastikan hasil prediksi valid
    assert stress_indicator in [0, 1, 2]  # Pastikan indikator stres valid (0, 1, atau 2)
