from tkinter import ttk, messagebox

def load_query_from_autosave(file_path, query_text):
    try:
        with open(file_path, "r") as f:
            config_query = f.read()
        query_text.insert("1.0", config_query)
    except Exception as e:
        messagebox.showerror("Error trying to read autosave", f"Erro:\n{e}")

