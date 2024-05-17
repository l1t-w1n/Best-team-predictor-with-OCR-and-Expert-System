"""Ability module"""
import secrets
from db_modules.db import DB

def get_new_abid():
    """Ability id generation"""
    new_abid = secrets.token_hex(8)
    while load_ability(new_abid) is not None:
        new_abid = secrets.token_hex(8)
    return new_abid

class Ability:
    """Object Ability"""

    def __init__(
            self, 
            Ab_name: str,
            Ab_description: str):
        self.abid = None
        self.Ab_name = Ab_name
        self.Ab_description = Ab_description
    
    def store(self):
        """Save ability into DB"""
        if self.abid is None:
            self.abid = get_new_abid()
            print(self.abid)
            try:
                with DB:
                    DB.execute(
                        "INSERT INTO Ability (id, Ab_name, Ab_description) VALUES (?, ?, ?)",
                        (self.abid, self.Ab_name, self.Ab_description)
                    )
            except Exception as e:
                print(f"Error storing ability: {e}")
    
    def exists(self):
        """Checks if ability exists in the DB"""
        res = DB.execute('SELECT * FROM Ability WHERE id=?', (self.abid,)).fetchone()
        return res is not None
    
def load_ability(abid: str):
    res = None
    if abid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Ability WHERE id=?", (abid,)).fetchone()
        except Exception as e:
            print(f"Error loading ability: {e}")

    if res is None:
        return None

    abid, Ab_name, Ab_description = res
    ability = Ability(Ab_name, Ab_description)
    ability.abid = abid
    return ability

def create_ability_table():
    """Creates ability table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Ability(
                    id VARCHAR(16),
                    Ab_name VARCHAR(100),
                    Ab_description BIGTEXT,
                    CONSTRAINT pk_ability PRIMARY KEY (id)
                );
            ''')
    except Exception as e:
        print(f"Error creating Ability table: {e}")
