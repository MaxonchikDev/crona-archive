import os
import tarfile
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PasswordDialog(ctk.CTkToplevel):
    """Модальное окно для ввода пароля архива."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Требуется пароль")
        self.geometry("350x180")
        self.resizable(False, False)
        
        # Делаем окно модальным
        self.lift()
        self.focus_force()
        self.grab_set()
        
        self.result = None

        self.label = ctk.CTkLabel(
            self, 
            text="Этот архив защищен паролем.\nПожалуйста, введите его:", 
            font=("Arial", 13)
        )
        self.label.pack(pady=(20, 10), padx=20)

        self.entry = ctk.CTkEntry(self, width=250, show="*")
        self.entry.pack(pady=10, padx=20)
        self.entry.focus()
        
        # Кнопки
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10, fill="x", padx=20)
        
        self.btn_ok = ctk.CTkButton(self.btn_frame, text="ОК", width=100, command=self.on_ok)
        self.btn_ok.pack(side="right", padx=5)
        
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Отмена", width=100, fg_color="gray", hover_color="darkgray", command=self.on_cancel)
        self.btn_cancel.pack(side="right", padx=5)
        
        # Перехват нажатия Enter
        self.entry.bind("<Return>", lambda event: self.on_ok())

    def on_ok(self):
        self.result = self.entry.get()
        self.grab_release()
        self.destroy()

    def on_cancel(self):
        self.grab_release()
        self.destroy()


class ArchiverApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("CronaArchive — Распаковка файлов")
        self.geometry("700x550")
        self.resizable(False, False)

        self.archive_path = None

        # --- ВЕРХНЯЯ ПАНЕЛЬ (ВЫБОР АРХИВА) ---
        self.frame_top = ctk.CTkFrame(self, corner_radius=10)
        self.frame_top.pack(pady=20, padx=20, fill="x", ipady=10)

        self.btn_select = ctk.CTkButton(
            self.frame_top,
            text="Открыть архив",
            font=("Arial", 14, "bold"),
            command=self.select_archive,
        )
        self.btn_select.pack(side="left", padx=20)

        self.lbl_path = ctk.CTkLabel(
            self.frame_top,
            text="Файл не выбран",
            font=("Arial", 12),
            text_color=("gray30", "gray70"),
        )
        self.lbl_path.pack(side="left", fill="x", expand=True, padx=10)

        # --- ЦЕНТРАЛЬНАЯ ПАНЕЛЬ (СОДЕРЖИМОЕ) ---
        self.frame_center = ctk.CTkFrame(self, corner_radius=10)
        self.frame_center.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        self.lbl_content = ctk.CTkLabel(
            self.frame_center,
            text="Содержимое архива",
            font=("Arial", 14, "bold"),
        )
        self.lbl_content.pack(pady=10, anchor="w", padx=15)

        # Список для отображения файлов
        self.listbox_scroll = tk.Scrollbar(self.frame_center)
        self.listbox_scroll.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            self.frame_center,
            font=("Arial", 12),
            bg="#2a2a2a" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            selectbackground="#1f538d",
            relief="flat",
            yscrollcommand=self.listbox_scroll.set,
            highlightthickness=0,
        )
        self.listbox.pack(
            side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15)
        )
        self.listbox_scroll.config(command=self.listbox.y)

        # --- НИЖНЯЯ ПАНЕЛЬ (КНОПКИ РАСПАКОВКИ) ---
        self.frame_bottom = ctk.CTkFrame(self, corner_radius=10)
        self.frame_bottom.pack(pady=(0, 20), padx=20, fill="x", ipady=10)

        self.btn_extract_selected = ctk.CTkButton(
            self.frame_bottom,
            text="Извлечь выбранное",
            font=("Arial", 13),
            fg_color="#2b9348",
            hover_color="#28733b",
            command=self.extract_selected,
        )
        self.btn_extract_selected.pack(side="left", padx=20)

        self.btn_extract_all = ctk.CTkButton(
            self.frame_bottom,
            text="Извлечь все",
            font=("Arial", 13),
            command=self.extract_all,
        )
        self.btn_extract_all.pack(side="right", padx=20)

    def ask_for_password(self):
        """Вызывает модальное окно ввода пароля и возвращает строку или None."""
        dialog = PasswordDialog(self)
        self.wait_window(dialog)
        return dialog.result

    def select_archive(self):
        """Диалоговое окно для выбора архива."""
        file_path = filedialog.askopenfilename(
            title="Выберите архив",
            filetypes=[
                ("All Archives", "*.zip *.tar *.gz"),
                ("Zip files", "*.zip"),
                ("Tar files", "*.tar"),
                ("Gzip files", "*.gz"),
            ],
        )

        if file_path:
            self.archive_path = file_path
            short_name = os.path.basename(file_path)
            self.lbl_path.configure(text=short_name)
            self.load_archive_content()

    def load_archive_content(self):
        """Чтение содержимого архива и вывод его в список."""
        self.listbox.delete(0, tk.END)

        try:
            if self.archive_path.endswith(".zip"):
                with zipfile.ZipFile(self.archive_path, "r") as zip_ref:
                    file_list = zip_ref.namelist()
            elif self.archive_path.endswith((".tar", ".tar.gz", ".gz")):
                with tarfile.open(self.archive_path, "r:*") as tar_ref:
                    file_list = tar_ref.getnames()
            else:
                return

            for file in file_list:
                self.listbox.insert(tk.END, file)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать архив:\n{e}")

    def extract_all(self):
        """Распаковка всех файлов из архива с поддержкой ввода пароля."""
        if not self.archive_path:
            messagebox.showwarning("Внимание", "Пожалуйста, сначала выберите архив.")
            return

        dest_dir = filedialog.askdirectory(title="Выберите папку для распаковки")
        if not dest_dir:
            return

        try:
            if self.archive_path.endswith(".zip"):
                with zipfile.ZipFile(self.archive_path, "r") as zip_ref:
                    try:
                        # Пробуем извлечь без пароля
                        zip_ref.extractall(dest_dir)
                    except RuntimeError as e:
                        # Если выскочила ошибка шифрования ("encrypted"), просим пароль
                        if "encrypted" in str(e) or "password" in str(e):
                            password = self.ask_for_password()
                            if password is None:  # Пользователь нажал Отмена
                                return
                            # Пробуем снова с паролем в байтах
                            zip_ref.extractall(dest_dir, pwd=bytes(password, 'utf-8'))
                        else:
                            raise e
            else:
                # В стандартных tar/gz пароли из коробки не поддерживаются
                with tarfile.open(self.archive_path, "r:*") as tar_ref:
                    tar_ref.extractall(dest_dir)

            messagebox.showinfo("Успех", f"Архив успешно распакован в папку:\n{dest_dir}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось распаковать архив. Возможно, неверный пароль.\nКод ошибки: {e}")

    def extract_selected(self):
        """Распаковка только выделенного в списке файла с поддержкой ввода пароля."""
        selected_index = self.listbox.curselection()

        if not selected_index:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите файл из списка.")
            return

        file_to_extract = self.listbox.get(selected_index)
        dest_dir = filedialog.askdirectory(title="Выберите папку для извлечения")

        if not dest_dir:
            return

        try:
            if self.archive_path.endswith(".zip"):
                with zipfile.ZipFile(self.archive_path, "r") as zip_ref:
                    try:
                        zip_ref.extract(file_to_extract, dest_dir)
                    except RuntimeError as e:
                        if "encrypted" in str(e) or "password" in str(e):
                            password = self.ask_for_password()
                            if password is None:
                                return
                            zip_ref.extract(file_to_extract, dest_dir, pwd=bytes(password, 'utf-8'))
                        else:
                            raise e
            else:
                with tarfile.open(self.archive_path, "r:*") as tar_ref:
                    member = tar_ref.getmember(file_to_extract)
                    tar_ref.extract(member, dest_dir)

            messagebox.showinfo("Успех", f"Файл '{file_to_extract}' успешно извлечен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось извлечь файл. Возможно, неверный пароль.\nКод ошибки: {e}")


if __name__ == "__main__":
    app = ArchiverApp()
    app.mainloop()
