import os, json

def config_setting():
    
    config_path = "config.json"
    data = {
        "driver": "SQL Anywhere 17",
        "uid": "uid",
        "password": "Password",
        "database": "Schema Database",
        "server": "Server",
        "integrated": "NO",
        "encryption": "NONE",
        "host": "127.0.0.1",
        "lines_limit": "100",
        "autosave_path": "autosave.txt"
    }

    if os.path.exists(config_path): return
    
    try:
        with open(config_path, "w", encoding="utf-8") as arquivo: 
            json.dump(data, arquivo, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao criar o arquivo: {e}")

    config = json.load(open(config_path, 'r', encoding='utf8'))
    return config