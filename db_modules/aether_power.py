"""Aether Power module"""
import secrets
from db_modules.db import DB

def get_new_apid():
    """Aether Power id generation"""
    new_apid = secrets.token_hex(8)
    while load_aeth_power(new_apid) is not None:
        new_apid = secrets.token_hex(8)
    return new_apid

class Aether_power:
    """Object Aether Power"""

    def __init__(
            self, 
            Power_name: str,
            Power_desc: str):
        self.apid = None
        self.Power_name = Power_name
        self.Power_desc = Power_desc
    
    def store(self):
        """Save aether power into DB"""
        if self.apid is None:
            self.apid = get_new_apid()
            try:
                with DB:
                    DB.execute(
                        "INSERT INTO Aether_power (id, Power_name, Power_description) VALUES (?, ?, ?)",
                        (self.apid, self.Power_name, self.Power_desc)
                    )
            except Exception as e:
                print(f"Error storing aether power: {e}")
    
    def exists(self):
        """Checks if aether power exists in the DB"""
        res = DB.execute('SELECT * FROM Aether_power WHERE id=?', (self.apid,)).fetchone()
        return res is not None

def load_aeth_power(apid: str):
    res = None
    if apid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Aether_power WHERE id=?", (apid,)).fetchone()
        except Exception as e:
            print(f"Error loading aether power: {e}")

    if res is None:
        return None

    apid, Power_name, Power_desc = res
    aeth_power = Aether_power(Power_name, Power_desc)
    aeth_power.apid = apid
    return aeth_power

def create_aeth_power_table():
    """Creates aether power table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Aether_power(
                id VARCHAR(16),
                Power_name VARCHAR(100),
                Power_description TEXT,
                CONSTRAINT pk_aether_power PRIMARY KEY (id)
            );
            ''')
    except Exception as e:
        print(f"Error creating Aether Power table: {e}")

