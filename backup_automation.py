"""
AUTOMATED FOLDER BACKUP SCRIPT
Mata Kuliah: Programming Fundamentals & Automation
Minggu 13-14: Integrasi Python untuk Automasi
Dosen: Budi Sunaryo, S.T., M.T. dan Fitri Saftnita, S.T., M.Kom.
"""

import os
import shutil
import datetime
import zipfile
import sys

# ====================
# KONFIGURASI
# ====================
SOURCE_FOLDER = "data_mentah"          # Folder yang akan dibackup
BACKUP_FOLDER = "backup_results"       # Tempat penyimpanan backup
RETENTION_DAYS = 7                     # Hapus backup lebih lama dari X hari

# ====================
# FUNGSI UTAMA
# ====================

def buat_folder_demo():
    """Membuat folder dan file demo jika belum ada"""
    if not os.path.exists(SOURCE_FOLDER):
        os.makedirs(SOURCE_FOLDER)
        print(f" Folder '{SOURCE_FOLDER}' dibuat")
        
        # Buat beberapa file contoh
        file_contoh = [
            ("data_mahasiswa.csv", "NIM,Nama,Nilai\n001,Budi,85\n002,Ani,90\n003,Cici,78"),
            ("log_system.txt", "2024-01-15 10:30:00 - System started\n2024-01-15 11:00:00 - Backup completed"),
            ("config.json", '{"server": "localhost", "port": 8080, "autobackup": true}'),
            ("readme.md", "# Data Sumber\n\nFolder ini berisi data untuk praktikum automasi backup.")
        ]
        
        for nama_file, isi in file_contoh:
            with open(os.path.join(SOURCE_FOLDER, nama_file), 'w', encoding='utf-8') as f:
                f.write(isi)
            print(f"  File '{nama_file}' dibuat")
        
        return True
    return False

def create_backup():
    """
    Membuat backup folder SOURCE_FOLDER ke BACKUP_FOLDER
    dalam format ZIP dengan timestamp.
    """
    try:
        print("\n" + "="*50)
        print("MEMBUAT BACKUP...")
        print("="*50)
        
        # 1. Cek dan buat folder sumber jika belum ada
        dibuat = buat_folder_demo()
        if dibuat:
            print("(Folder demo dibuat otomatis)")
        
        # 2. Buat folder backup jika belum ada
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
            print(f" Folder backup '{BACKUP_FOLDER}' dibuat")
        
        # 3. Generate nama file backup dengan timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_FOLDER, backup_name)
        
        # 4. Hitung jumlah file yang akan dibackup
        file_count = 0
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            file_count += len(files)
        
        print(f" Menemukan {file_count} file di '{SOURCE_FOLDER}'")
        print(f" Membuat: {backup_name}")
        
        # 5. Buat ZIP backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(SOURCE_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Buat path relatif di dalam ZIP
                    arcname = os.path.relpath(file_path, SOURCE_FOLDER)
                    zipf.write(file_path, arcname)
        
        # 6. Hitung ukuran backup
        backup_size = os.path.getsize(backup_path)
        if backup_size < 1024:
            size_str = f"{backup_size} bytes"
        elif backup_size < 1024*1024:
            size_str = f"{backup_size/1024:.2f} KB"
        else:
            size_str = f"{backup_size/(1024*1024):.2f} MB"
        
        print(f" BACKUP BERHASIL!")
        print(f" Ukuran: {size_str}")
        print(f" Lokasi: {backup_path}")
        
        # 7. Bersihkan backup lama (opsional)
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        return False

def cleanup_old_backups():
    """
    Menghapus backup yang lebih lama dari RETENTION_DAYS
    """
    try:
        if not os.path.exists(BACKUP_FOLDER):
            return
        
        now = datetime.datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(BACKUP_FOLDER):
            if filename.startswith("backup_") and filename.endswith(".zip"):
                file_path = os.path.join(BACKUP_FOLDER, filename)
                
                # Ekstrak tanggal dari nama file
                try:
                    # Format: backup_YYYYMMDD_HHMMSS.zip
                    date_str = filename[7:-4]  # Hapus 'backup_' dan '.zip'
                    file_date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    
                    # Hitung selisih hari
                    days_diff = (now - file_date).days
                    
                    if days_diff > RETENTION_DAYS:
                        os.remove(file_path)
                        print(f"   Hapus backup lama: {filename} ({days_diff} hari)")
                        deleted_count += 1
                        
                except ValueError:
                    continue
        
        if deleted_count > 0:
            print(f"   {deleted_count} backup lama dihapus")
            
    except Exception as e:
        print(f"   Gagal hapus backup lama: {e}")

def list_backups():
    """
    Menampilkan daftar backup yang tersedia
    """
    print("\n" + "="*50)
    print("DAFTAR BACKUP TERSEDIA")
    print("="*50)
    
    if not os.path.exists(BACKUP_FOLDER):
        print("Belum ada backup")
        return
    
    backups = []
    for filename in os.listdir(BACKUP_FOLDER):
        if filename.endswith(".zip"):
            file_path = os.path.join(BACKUP_FOLDER, filename)
            size_bytes = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)
            modified_str = datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M")
            
            # Format ukuran file
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024*1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.2f} MB"
            
            backups.append((filename, size_str, modified_str))
    
    if not backups:
        print("Tidak ada file backup")
        return
    
    for i, (name, size, mod_time) in enumerate(backups, 1):
        print(f"{i:2}. {name}")
        print(f"     Ukuran: {size}, Modifikasi: {mod_time}")
    
    print(f"\n Total: {len(backups)} backup")

def view_source_folder():
    """
    Menampilkan isi folder sumber
    """
    print("\n" + "="*50)
    print(f"ISI FOLDER: {SOURCE_FOLDER}")
    print("="*50)
    
    if not os.path.exists(SOURCE_FOLDER):
        print("Folder belum ada")
        return
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        level = root.replace(SOURCE_FOLDER, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent} {os.path.basename(root) or SOURCE_FOLDER}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            file_count += 1
            
            if file_size < 1024:
                size_str = f"{file_size} B"
            else:
                size_str = f"{file_size/1024:.1f} KB"
            
            print(f"{subindent} {file} ({size_str})")
    
    print("-"*50)
    print(f" Total: {file_count} file, {total_size/1024:.1f} KB")

def restore_backup():
    """
    Merestore backup ke folder tertentu
    """
    if not os.path.exists(BACKUP_FOLDER):
        print("Tidak ada backup untuk direstore")
        return
    
    backups = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.zip')]
    
    if not backups:
        print("Tidak ada file backup")
        return
    
    print("\nPILIH BACKUP UNTUK DIRESTORE:")
    for i, filename in enumerate(backups, 1):
        print(f"{i}. {filename}")
    
    try:
        choice = int(input(f"\nPilih (1-{len(backups)}): "))
        if 1 <= choice <= len(backups):
            selected = backups[choice-1]
            zip_path = os.path.join(BACKUP_FOLDER, selected)
            
            # Tentukan folder restore
            restore_to = input("Restore ke folder (kosongkan untuk 'restored_data'): ").strip()
            if not restore_to:
                restore_to = "restored_data"
            
            # Ekstrak ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(restore_to)
            
            print(f"Backup '{selected}' berhasil direstore ke '{restore_to}'")
        else:
            print("Pilihan tidak valid")
    except (ValueError, IndexError):
        print("Input tidak valid")

# ====================
# MENU UTAMA
# ====================
def main():
    """
    Menu interaktif untuk mahasiswa
    """
    print("\n" + "="*60)
    print("PRAKTIKUM INTEGRASI PYTHON UNTUK AUTOMASI")
    print("Mata Kuliah: Programming Fundamentals & Automation")
    print("Dosen: Budi Sunaryo, S.T., M.T.")
    print("="*60)
    
    print(f"\n Sumber data: ./{SOURCE_FOLDER}/")
    print(f" Lokasi backup: ./{BACKUP_FOLDER}/")
    print(f" Retention policy: {RETENTION_DAYS} hari")
    
    while True:
        print("\n" + "-"*50)
        print("MENU UTAMA:")
        print("1. Buat Backup Sekarang")
        print("2. Lihat Daftar Backup")
        print("3. Lihat Isi Folder Sumber")
        print("4. Restore Backup")
        print("5. Hapus Semua Backup")
        print("6. Keluar")
        print("-"*50)
        
        choice = input("Pilih opsi (1-6): ").strip()
        
        if choice == "1":
            create_backup()
        elif choice == "2":
            list_backups()
        elif choice == "3":
            view_source_folder()
        elif choice == "4":
            restore_backup()
        elif choice == "5":
            confirm = input("Yakin hapus SEMUA backup? (y/n): ").lower()
            if confirm == 'y':
                if os.path.exists(BACKUP_FOLDER):
                    shutil.rmtree(BACKUP_FOLDER)
                    print("Semua backup dihapus")
                else:
                    print("Folder backup tidak ada")
        elif choice == "6":
            print("\n" + "="*50)
            print("TERIMA KASIH TELAH MENGGUNAKAN PROGRAM INI!")
            print("="*50)
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# ====================
# JALANKAN PROGRAM
# ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Program dihentikan oleh user")
    except Exception as e:
        print(f"\n  Error tidak terduga: {e}")