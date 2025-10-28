# sebelum memakai pergi ke terminal ketik "pip install google-genai"
#                                         "pip install Pillow"

# Gunakan Internet ketika menggunakan

# library install
from google import genai
import os
from google.genai.errors import APIError
import PIL.Image
import json
import subprocess


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# File untuk mengakses riwayat / history chat
CHAT_HISTORY_FILE = "chatbot_history.json"

# mendefinisikan menyimpan history / riwayat chat
def save_chat_history(history_list):
    """Menyimpan list riwayat chat ke file JSON."""
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, indent=4)
    except IOError as e:
        print(
            f"{Colors.RED}Error: Gagal menyimpan riwayat chat ke {CHAT_HISTORY_FILE}. {e}{Colors.END}")

# mendefinisikan memuat history / riwayat chat
def load_chat_history():
    """Memuat list riwayat chat dari file JSON."""
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []

    try:
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history_list = json.load(f)
            if not isinstance(history_list, list):
                print(
                    f"{Colors.YELLOW}Warning: Format riwayat chat tidak valid, memulai sesi baru.{Colors.END}")
                return []
            return history_list
    except (IOError, json.JSONDecodeError) as e:
        print(
            f"{Colors.RED}Error: Gagal memuat riwayat chat. Memulai sesi baru. {e}{Colors.END}")
        return []

# mendefinisikan menu chatbot(text)
def run_chatbot_text(chat_session, history_list):
    """
    Menjalankan mode chatbot berbasis teks, menyimpan riwayat, dan
    mengembalikan status kelanjutan (keep_going) dan riwayat terbaru.
    """
    message = input(f"{Colors.BOLD}pertanyaan{Colors.END} > ")

    if message.lower().strip() == "exit":
        print(f"{Colors.YELLOW}Keluar dari sesi Chatbot Teks.{Colors.END}")
        return False, history_list

    formatting_instruction = " (Jawab dalam format Markdown: gunakan **tebal** untuk subjudul, dan pisahkan paragraf dengan jelas untuk tampilan terminal yang rapi.)"
    prompt_to_send = message + formatting_instruction

    print(f"\n{Colors.YELLOW}sedang berpikir...{Colors.END}")

    try:
        res = chat_session.send_message(prompt_to_send)
        print("\n" + res.text)
        history_list.append({"role": "user", "parts": [message]})
        history_list.append({"role": "model", "parts": [res.text]})
        save_chat_history(history_list)

    except APIError as e:
        print(f"\n{Colors.RED}An API error occurred: {e}{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Terjadi error tak terduga: {e}{Colors.END}")
    return True, history_list

# mendefinisikan fungsi untuk menguji code
def run_python_code(code_string):
    """Menjalankan string kode Python menggunakan subprocess."""
    print(f"\n{Colors.YELLOW}=== HASIL EKSEKUSI KODE ==={Colors.END}")
    try:
        # Menjalankan kode sebagai proses terpisah
        result = subprocess.run(
            ['python', '-c', code_string],
            capture_output=True,
            text=True,
            timeout=10,  
            check=True  
        )

        if result.stdout:
            print(f"{Colors.GREEN}Output:{Colors.END}\n{result.stdout}")

        if result.stderr:
            # stderr akan berisi output meskipun check=True, jika ada warning dll.
            print(
                f"{Colors.YELLOW}Warning/Error pada stderr:{Colors.END}\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Error Eksekusi Ditemukan:{Colors.END}")
        print(f"{e.stderr}")
    except FileNotFoundError:
        print(f"{Colors.RED}Error: Interpreter 'python' tidak ditemukan. Pastikan Python terinstal dan berada di PATH Anda.{Colors.END}")
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}Error: Eksekusi kode melebihi batas waktu (10 detik). Ada kemungkinan infinite loop.{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error tak terduga saat menjalankan kode: {e}{Colors.END}")
    print(f"{Colors.YELLOW}========================={Colors.END}\n")


def main_menu():
    """Fungsi utama untuk menjalankan aplikasi."""
    try:
        client = genai.Client(
            api_key="AIzaSyBQD0brSlNEnQmdAKbzcxo_cxrjc0-Gc4U")

        default_chat = client.chats.create(model="gemini-2.0-flash")
    except Exception as e:
        print(f"{Colors.RED}FATAL ERROR: Gagal menginisialisasi Gemini Client. Cek API Key. {e}{Colors.END}")
        return

    while True:
        print(" ")
        print(f"===={Colors.MAGENTA}{Colors.BOLD}Py Helper{Colors.END}====")
        print(" ")
        print(f"{Colors.CYAN}'chatbot'{Colors.END} = untuk membuka chatbot AI")
        print(f"{Colors.GREEN}'py assist'{Colors.END} = pembantu coding python")
        print(f"{Colors.RED}'exit'{Colors.END} = keluar dari program")
        print(" ")

        interface = input("Pilih fungsi > ").lower().strip()

        if interface == "exit":
            print(
                f"{Colors.MAGENTA}Terima kasih telah menggunakan Py Helper. Sampai jumpa!{Colors.END}")
            break

        elif interface == "chatbot":
            print(" ")
            print(f"--{Colors.CYAN}Wellcome to Chatbot{Colors.END}--")
            print(f"{Colors.YELLOW}Riwayat obrolan ditemukan ('{CHAT_HISTORY_FILE}').{Colors.END}" if os.path.exists(
                CHAT_HISTORY_FILE) else f"{Colors.YELLOW}Tidak ada riwayat obrolan.{Colors.END}")

            choice = input(
                f"Pilih {Colors.BLUE}'load'{Colors.END} atau {Colors.GREEN}'new'{Colors.END} > ").lower().strip()

            current_history = []
            if choice == 'load':
                current_history = load_chat_history()
            else:
                save_chat_history([])

            chat_session = default_chat
            try:
                chat_session = client.chats.create(
                    model="gemini-2.0-flash",
                    history=current_history
                )
                print(f"{Colors.GREEN}Sesi chat berhasil dibuat/dimuat.{Colors.END}")
            except Exception as e:
                print(
                    f"{Colors.RED}Error saat membuat sesi chat: {e}. Menggunakan sesi default kosong.{Colors.END}")
                current_history = []

            while True:
                print("-" * 30)
                print(f"{Colors.BLUE}'text'{Colors.END} = untuk text biasa")
                print(f"{Colors.BLUE}'image'{Colors.END} = untuk gambar/foto")
                print(f"{Colors.RED}'exit'{Colors.END} = untuk kembali ke Main Menu")
                print("-" * 30)

                text_atau_gambar = input(
                    "ketik 'text' / 'image' / 'exit' > ").lower().strip()

                if text_atau_gambar == "exit":
                    break

                elif text_atau_gambar == "text":
                    keep_going, updated_history = run_chatbot_text(
                        chat_session, current_history)
                    current_history = updated_history

                    if not keep_going:
                        break

                elif text_atau_gambar == "image":
                    IMAGE_FILE_PATH = input("masukkan nama file gambar: ")
                    try:
                        img_content = PIL.Image.open(IMAGE_FILE_PATH)
                        print(
                            f"File berhasil di upload! Name: {IMAGE_FILE_PATH}")
                        print("-" * 30)

                        extract = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=["salin / tulis ulang semua teks dari gambar", img_content])
                        teks_soal = extract.text

                        input_user = input("masukkan prompt untuk gambar > ")
                        promt_work = (
                            f"{input_user}:\n\n Teks dari gambar:\n {teks_soal}\n\n"
                            f"Berikan jawaban dalam format Markdown yang rapi; gunakan **tebal** untuk poin penting "
                            f"dan buat paragraf yang terstruktur."
                        )
                        response_work = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=[promt_work])
                        print(response_work.text)

                    except APIError as e:
                        print(f"An API error occurred: {e}")
                    except FileNotFoundError:
                        print(
                            f"Error: The file '{IMAGE_FILE_PATH}' was not found. Please check the file path.")
                    pass

                else:
                    print(f"{Colors.RED}Pilihan tidak valid.{Colors.END}")

        elif interface == "py assist":
            print(
                f"{Colors.GREEN}Masukkan code (ketik 'selesai' di akhir code){Colors.END}")
            error_code = []
            while True:
                codes = input(f"{Colors.GREEN}>{Colors.END} ")
                if codes.strip() == "selesai":
                    break
                error_code.append(codes)

            code_string = "\n".join(error_code)
            # Opsi 1: Uji kode yang dikumpulkan
            if code_string.strip():
                print(
                    f"\n{Colors.CYAN}Apakah Anda ingin menguji kode yang Anda masukkan sebelum meminta perbaikan? (y/n){Colors.END}")
                test_choice = input("Pilih (y/n) > ").lower().strip()
                if test_choice == 'y':
                    run_python_code(code_string)

            # Opsi 2: Minta perbaikan/penjelasan dari AI
            user_prompt = input(
                "masukkan masalah/pertanyaan tentang kode di atas: ")

            fixing_prompt = "Kamu adalah Ahli dalam programming python. Ada error/kesalahan atau pertanyaan. Anda diminta untuk memperbaiki kode dan memberikan penjelasan singkat."

            complete_prompt = fixing_prompt + " " + user_prompt
            fix_error_setup = f"Kode Python:\n\n{code_string}\n\nInstruksi: {complete_prompt}"

            print(f"\n{Colors.YELLOW}sedang menganalisis...{Colors.END}")

            try:
                response_fix = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[fix_error_setup])
                print("\n" + "=" * 20)
                print(f"{Colors.GREEN}RESPON PY ASSIST:{Colors.END}")
                print("=" * 20)
                print(response_fix.text)
                print("=" * 20 + "\n")

            except APIError as e:
                print(
                    f"\n{Colors.RED}An API error occurred during Py Assist: {e}{Colors.END}")
            except Exception as e:
                print(
                    f"\n{Colors.RED}Terjadi error tak terduga di Py Assist: {e}{Colors.END}")

        else:
            print(f"{Colors.RED}Pilihan tidak valid. Silakan coba lagi.{Colors.END}")


if __name__ == "__main__":
    main_menu()
