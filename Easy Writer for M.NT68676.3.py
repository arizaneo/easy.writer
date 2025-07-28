import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import configparser
import os

INI_PATH = "ezwriter.ini"
selected_bin_path = None

# JIG tipi açıklamaları
JIG_OPTIONS = {
    "NVT EasyUSB": "0",
    "FTDI (UART)": "1",
    "AMD (DP)": "2",
    "NVIDIA (DP)": "3",
    "INTEL (DP only)": "4",
    "UART (Doğrudan Seri)": "5"
}
REVERSE_JIG_OPTIONS = {v: k for k, v in JIG_OPTIONS.items()}

def read_ini_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    info = config["INFORMATION"] if "INFORMATION" in config else {}
    com_port = f"COM{info.get('UART_COMPORT', '1')}"
    ftd_speed = int(info.get('FTD_SPEED', '57600'))
    baud = "57600"
    if ftd_speed <= 300000:
        baud = "57600"
    elif ftd_speed <= 500000:
        baud = "115200"
    else:
        baud = "38400"
    jig_type = info.get('JIG_TYPE', '1')
    auto_wp = info.get('AUTO_WP', '0')

    return com_port, baud, ftd_speed, jig_type, auto_wp

def list_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def select_bin_file():
    global selected_bin_path
    file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if file_path:
        selected_bin_path = file_path
        label_bin_path.config(text=os.path.basename(file_path))
        output_text.insert(tk.END, f"📦 Seçilen .bin dosyası: {file_path}\n")

def test_connection():
    port = combo_port.get()
    baudrate = int(combo_baud.get())
    timeout = 2

    if not port:
        messagebox.showwarning("Uyarı", "Lütfen bir COM portu seçin.")
        return

    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        output_text.insert(tk.END, f"🧪 {port} portuna bağlanıldı. Veri bekleniyor...\n")
        root.update()

        ser.write(b'\x00')  # ping
        data = ser.read(128)

        if data:
            output_text.insert(tk.END, f"📨 Veri alındı:\n{data.decode(errors='ignore')}\n")
        else:
            output_text.insert(tk.END, "⚠️ Veri alınamadı. Kart ISP modunda olmayabilir.\n")

        ser.close()
    except serial.SerialException as e:
        output_text.insert(tk.END, f"❌ Seri port hatası: {e}\n")
    except Exception as e:
        output_text.insert(tk.END, f"⚠️ Hata: {e}\n")

def trigger_isp():
    port = combo_port.get()
    baudrate = int(combo_baud.get())

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        output_text.insert(tk.END, f"🛁 ISP sinyali gönderiliyor ({port}, {baudrate} baud)...\n")
        root.update()
        ser.write(b'\xA5\x5A')  # ISP tetikleme sinyali (temsilî)
        ser.close()
        output_text.insert(tk.END, "✅ ISP komutu gönderildi. Kart tepki veriyorsa bağlantı kurulmalı.\n")
    except Exception as e:
        output_text.insert(tk.END, f"❌ ISP komutu gönderilemedi: {e}\n")

# --- GUI ---
root = tk.Tk()
root.title("MN168676 ISP UART Test (INI + ISP Tuşlu + BIN Dosyası)")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0)

# INI'den oku
if os.path.exists(INI_PATH):
    com_default, baud_default, ftd_speed_default, jig_type_default, auto_wp_default = read_ini_config(INI_PATH)
else:
    com_default, baud_default, ftd_speed_default, jig_type_default, auto_wp_default = "COM1", "57600", 57600, "1", "0"

jig_type_text = REVERSE_JIG_OPTIONS.get(jig_type_default, "FTDI (UART)")

# --- Seri Ayarlar ---
ttk.Label(frame, text="COM Port:").grid(column=0, row=0, sticky="W")
combo_port = ttk.Combobox(frame, values=list_serial_ports(), width=15)
combo_port.grid(column=1, row=0)
combo_port.set(com_default)

ttk.Label(frame, text="Baudrate:").grid(column=0, row=1, sticky="W")
combo_baud = ttk.Combobox(frame, values=["9600", "19200", "38400", "57600", "115200"], width=15)
combo_baud.grid(column=1, row=1)
combo_baud.set(baud_default)

# --- INI Ayarları ---
ttk.Label(frame, text="FTDI Speed (Hz):").grid(column=0, row=2, sticky="W")
entry_ftd = ttk.Entry(frame, width=15)
entry_ftd.insert(0, str(ftd_speed_default))
entry_ftd.grid(column=1, row=2)

ttk.Label(frame, text="JIG Tipi:").grid(column=0, row=3, sticky="W")
combo_jig = ttk.Combobox(frame, values=list(JIG_OPTIONS.keys()), width=25)
combo_jig.grid(column=1, row=3)
combo_jig.set(jig_type_text)

ttk.Label(frame, text="Auto WP:").grid(column=0, row=4, sticky="W")
combo_wp = ttk.Combobox(frame, values=["0", "1"], width=15)
combo_wp.grid(column=1, row=4)
combo_wp.set(auto_wp_default)

# --- BIN dosyası seçimi ---
btn_select_file = ttk.Button(frame, text="BIN Dosyası Seç", command=select_bin_file)
btn_select_file.grid(column=0, row=5, pady=5, sticky="W")

label_bin_path = ttk.Label(frame, text="Henüz dosya seçilmedi.")
label_bin_path.grid(column=1, row=5, sticky="W")

# --- ISP tuşu ---
btn_isp = ttk.Button(frame, text="ISP Modunu Aktif Et", command=trigger_isp)
btn_isp.grid(column=0, row=6, columnspan=2, pady=5)

# --- Bağlantı test ---
btn_test = ttk.Button(frame, text="Bağlantıyı Test Et", command=test_connection)
btn_test.grid(column=0, row=7, columnspan=2, pady=5)

# --- Çıktı alanı ---
output_text = scrolledtext.ScrolledText(root, width=70, height=14)
output_text.grid(row=1, column=0, padx=10, pady=10)

root.mainloop()
