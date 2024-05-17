"""Elemental Type module"""
import secrets
from db_modules.db import DB

def get_new_etid():
    """Elemental Type id generation"""
    new_etid = secrets.token_hex(8)
    while load_elemental_type(new_etid) is not None:
        new_etid = secrets.token_hex(8)
    return new_etid

class Elemental_type:
    """Object Elemental Type"""

    def __init__(
            self, 
            El_type: str,
            Strong_against: str,
            Weak_against: str):
        self.etid = None
        self.El_type = El_type
        self.Strong_against = Strong_against
        self.Weak_against = Weak_against
    
    def store(self):
        """Save elemental type into DB"""
        if self.etid is None:
            self.etid = get_new_etid()
            try:
                with DB:
                    DB.execute(
                        "INSERT INTO Elemental_type (id, El_type, Strong_against, Weak_against) VALUES (?, ?, ?, ?)",
                        (self.etid, self.El_type, self.Strong_against, self.Weak_against)
                    )
            except Exception as e:
                print(f"Error storing elemental type: {e}")
    
    def exists(self):
        """Checks if elemental type exists in the DB"""
        res = DB.execute('SELECT * FROM Elemental_type WHERE id=?', (self.etid,)).fetchone()
        return res is not None

def load_elemental_type(etid: str):
    res = None
    if etid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Elemental_type WHERE id=?", (etid,)).fetchone()
        except Exception as e:
            print(f"Error loading elemental type: {e}")

    if res is None:
        return None

    etid, El_type, Strong_against, Weak_against = res
    elemental_type = Elemental_type(El_type, Strong_against, Weak_against)
    elemental_type.etid = etid
    return elemental_type

def create_elemental_type_table():
    """Creates elemental type table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Elemental_type(
                    id VARCHAR(16),
                    El_type VARCHAR(100),
                    Strong_against VARCHAR(100),
                    Weak_against VARCHAR(100),
                    CONSTRAINT pk_elemental_type PRIMARY KEY (id)
                );
            ''')
    except Exception as e:
        print(f"Error creating Elemental Type table: {e}")
