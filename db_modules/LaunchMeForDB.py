from db_modules.db import drop_tables,init_tables,DB
from db_modules.ability import create_ability_table,Ability
from db_modules.aether_power import create_aeth_power_table
from db_modules.origin import create_origin_table
from db_modules.elemental_type import Elemental_type,create_elemental_type_table
from db_modules.possess import create_possess_table
from db_modules.max_hero import create_max_hero_table
from db_modules.current_hero import create_current_hero_table

drop_tables()
init_tables()
create_ability_table()
create_aeth_power_table()
create_origin_table()
create_elemental_type_table()
create_possess_table()
create_max_hero_table()
create_current_hero_table()
fire = Elemental_type("Fire/Red", "Nature/Green",None)
nature = Elemental_type("Nature/Green", "Ice/Blue",None)
ice = Elemental_type("Ice/Blue","Fire/Red",None)
holy = Elemental_type("Holy/Yellow","Dark/Purple", "Holy/Yellow")
dark = Elemental_type("Dark/Purple", "Holy/Yellow", "Dark/Purple")
fire.store()
nature.store()
ice.store()
holy.store()
dark.store()
#name = "Resist Poison"
#ab1 = Ability(name," This character has innate resistance against Poison.")
#ab1.store()
#ab2 = DB.execute("Select id From Ability Where Ab_name = '"+name+"'").fetchone()
