from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import firebase_admin
from firebase_admin import credentials, auth

# Ganti dengan path JSON key yang diunduh
cred = credentials.Certificate('D:\Kuliah\Matkul\Semester 5\IAK\M7\config\iakretail7-firebase-adminsdk-fiaat-9ceeeef7f0.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',  # Ganti dengan username MySQL
        password='',  # Ganti dengan password MySQL
        database='retail7'  # Nama database yang ingin disambungkan
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Membuat tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        )
    ''')

    # Membuat tabel gudang
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gudang (
            id_barang INT AUTO_INCREMENT PRIMARY KEY,
            nama_barang VARCHAR(100) NOT NULL,
            jumlah_barang INT NOT NULL
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

# Firebase login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Autentikasi pengguna dengan Firebase
            user = auth.get_user_by_email(email)
            token = auth.create_custom_token(user.uid)

            # Simpan token di session
            session['firebase_token'] = token.decode('utf-8')  # simpan token ke session
            session['username'] = email  # simpan email user ke session

            flash(f"Login sukses! Selamat datang, {email}", 'success')
            return redirect(url_for('transaksi'))  # redirect ke transaksi setelah login berhasil

        except Exception as e:
            flash("Login gagal: " + str(e), 'danger')

    return render_template('login.html')

# Verifikasi token Firebase
def verify_firebase_token(token):
    try:
        # Verifikasi token ID Firebase
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except:
        return None

@app.route('/transaksi')
def transaksi():
    # Verifikasi apakah token ada di session
    token = session.get('firebase_token')

    # Verifikasi token Firebase
    if not token or not verify_firebase_token(token):
        flash("Token tidak valid. Silakan login kembali.", 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    username = session.get('username', 'User')  # Ambil username dari session
    return render_template('transaksi.html', users=users, username=username)

@app.route('/logout')
def logout():
    # Hapus session
    session.pop('firebase_token', None)
    session.pop('username', None)
    flash("Anda telah keluar.", 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
