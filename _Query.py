import pyodbc, pandas as pd

def query_db(config, query,limit):
    db = pyodbc.connect(f"Driver={config['driver']};"
                        f"UID={config['uid']};"
                        f"PASSWORD={config['password']};"
                        f"DatabaseName={config['database']};"
                        f"ServerName={config['server']};"
                        f"Integrated={config['integrated']};"
                        f"Encryption={config['encryption']};"
                        f"Host={config['host']}")
    df = pd.read_sql_query(query, db)
    return df.head(limit)