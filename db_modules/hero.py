"""Hero module"""
import secrets
from db_modules.db import DB

def get_new_hid():
    """Hero id generation"""
    new_hid = secrets.token_hex(8)
    while load_hero(new_hid) is not None:
        new_hid = secrets.token_hex(8)
    return new_hid

class Hero:
    """Object hero"""

    def __init__(
            self, 
            Hero_name: str, 
            Rarity: str, 
            Class: str, 
            Mana_speed: str, 
            Power_id: str,
            El_type: str,
            Origin: str,
            SpecialSkill: str):
        self.hid = None
        self.Hero_name = Hero_name
        self.Rarity = Rarity
        self.Class = Class
        self.Mana_speed = Mana_speed
        self.Power_id = Power_id
        self.El_type = El_type
        self.Origin = Origin
        self.SpecialSkill = SpecialSkill
    
    def store(self):
        """Save hero into DB"""
        if self.hid is None:
            self.hid = get_new_hid()
            try:
                with DB:
                    DB.execute(
                        "INSERT INTO Hero (id, Hero_name, Rarity, Class, Mana_speed, Power_id, El_type, Origin, SpecialSkill) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.hid, self.Hero_name, self.Rarity, self.Class, self.Mana_speed, self.Power_id, self.El_type, self.Origin, self.SpecialSkill)
                    )
            except Exception as e:
                print(f"Error storing hero: {e}")
    
    def exists(self):
        """Checks if hero exists in the DB"""
        res = DB.execute('SELECT * FROM Hero WHERE id=?', (self.hid,)).fetchone()
        return res is not None

def load_hero(hid: str):
    res = None
    if hid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Hero WHERE id=?", (hid,)).fetchone()
        except Exception as e:
            print(f"Error loading hero: {e}")

    if res is None:
        return None

    hid, Hero_name, Rarity, Class, Mana_speed, Power_id, El_type, Origin, SpecialSkill = res
    hero = Hero(Hero_name, Rarity, Class, Mana_speed, Power_id, El_type, Origin, SpecialSkill)
    hero.hid = hid
    return hero

def create_hero_table():
    """Creates hero table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Hero(
                    id VARCHAR(16),
                    Hero_name VARCHAR(100),
                    Rarity VARCHAR(100),
                    Class VARCHAR(100),
                    Mana_speed VARCHAR(50),
                    Power_id VARCHAR(16),
                    El_type VARCHAR(16),
                    Origin VARCHAR(16),
                    SpecialSkill TEXT,
                    CONSTRAINT pk_hero PRIMARY KEY (id),
                    CONSTRAINT fk_hero_origin FOREIGN KEY (Origin) REFERENCES Origin(id),
                    CONSTRAINT fk_hero_power FOREIGN KEY (Power_id) REFERENCES Aether_power(id),
                    CONSTRAINT fk_hero_el_power FOREIGN KEY (El_type) REFERENCES Elemental_type(id),
                );
            ''')
    except Exception as e:
        print(f"Error creating hero table: {e}")

