import random
from objects.script_enums import FactionEnum, AIModel, Gender, Role
from objects.faction import Faction
from objects.character.character import FemaleCharacter, MaleCharacter

seed_value = None
random.seed(seed_value)

def create_factions_configuration(regions, names, region_amount):
    
    
    factions_list = create_factions(names)
    assign_settlements(factions_list, regions, region_amount)
    
    #Create Characters for faction based on amount of regions
    assign_characters(factions_list)
    
    for faction in factions_list:
        print()
        print(faction.faction_name)
        for char in faction.characters:
            print(char.character_name)
    #Create family records for Faction characters
    
    #Generate Text for descr_strat
    
    return

def create_factions(names_list):
    
    factions_list = list()
    
    for factionEnum in FactionEnum:
        faction = Faction(
            faction_name=factionEnum.value,
            ai_model=AIModel.BALANCED_SMITH,
            ai_label=getAILabel(factionEnum.value),
            denari=15000,
            kings_purse=6000,
            settlements=None,
            characters=None,
            character_records=None,
            factionCharacterNames=assign_names_for_faction(factionEnum, names_list)
        )
        
        factions_list.append(faction)
    
    return factions_list

def getAILabel(factionName):
    match factionName:
            case "turks", "egypt", "moors":
                return "islam"
            case "russia", "novgorod", "byzantium":
                return "orthodox"
            case "lithuania":
                return "pagan"
            case "mongols", "timurids":
                return "mongol"
            case "aztecs":
                return "aztecs"
            case "jerusalem", "teutonic_order", "antioch":
                return "teutonic"
            case "papal_states":
                return "papal_faction"
            case "slaves":
                return "slave_faction"
            case _:
                return "catholic"
            
def assign_settlements(factions, regions, region_amount):

    special_regions = {"Tenochtitlan Province", "North_America"}
    available_regions = [r for r in regions if r.province_name not in special_regions]    
    random.shuffle(available_regions)
    
    for faction in factions:
        
        if faction is None:
            continue
        
        if faction.faction_name in {FactionEnum.AZTECS.value, FactionEnum.SLAVE.value}:
            continue
        
        chosen = available_regions[:region_amount]
        faction.settlements = chosen
        available_regions = available_regions[region_amount:]

    aztecs = next(f for f in factions if f.faction_name == FactionEnum.AZTECS.value)
    tenochtitlan = next(r for r in regions if r.province_name == "Tenochtitlan_Province")
    aztecs.settlements = [tenochtitlan]
        
    slave = next(f for f in factions if f.faction_name == FactionEnum.SLAVE.value)
    north_america = next(r for r in regions if r.province_name == "North_America")
    slave.settlements = [north_america]
    slave.settlements.extend(available_regions)
    
def assign_characters(factions):

    for faction in factions:
        
        royal_family = []
        capital_region = faction.settlements[0]
        
        if faction is None:
            continue  
        
        elif faction.faction_name in {FactionEnum.SLAVE.value}:          
             
            
            for i in faction.settlements[::3]:
                general = create_slave_character(i.settlement_positionX, i.settlement_positionY, FactionEnum.ANTIOCH)
                royal_family.append(general)
            
            faction.characters = royal_family    
                
        elif faction.faction_name in {FactionEnum.PAPAL_STATES.value}:
            pope = create_pope_character(capital_region)
            royal_family.append(pope)
            
            for i in faction.settlements:
                general = create_general_character(i.settlement_positionX, i.settlement_positionY)
                royal_family.append(general)
            
            faction.characters = royal_family
                
        else:
            king = create_king_character(capital_region)
            queen = create_queen_character()
            prince = create_prince_character(capital_region)
            
            royal_family = [king,queen,prince]
            faction.characters = royal_family
            
            for i in faction.settlements:
                general = create_general_character(i.settlement_positionX, i.settlement_positionY)
                faction.characters.append(general)
                
        assign_character_names(faction)
                  
def create_king_character(capital_region):
    
    return MaleCharacter(
        character_name="",
        role=Role.LEADER,
        age=33,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="Factionleader 1 , GoodCommander 4 , Energetic 1 , StrategyChivalry 4, Intelligent 1",
        ancillaries=create_ancillaries(),
        army_units=create_army()
    )
    
def create_queen_character():
    
    return FemaleCharacter(
        character_name="",
        role=Role.NEVERLEADER,
        age=32
    )
    
def create_prince_character(capital_region):
    
    return MaleCharacter(
        character_name="",
        role=Role.HEIR,
        age=17,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="Factionheir 1 , BattleDread 2 , StrategyDread 1 , Intelligent 2 , PublicFaith 1 , LoyaltyStarter 1, Fertile 1",
        ancillaries=create_ancillaries(),
        army_units=create_army()
    )
    
def create_general_character(x, y):
    
    return MaleCharacter(
        character_name="",
        role=None,
        age=16,
        positionX=x,
        positionY=y,
        traits="GoodCommander 2 , BattleChivalry 2 , StrategyChivalry 1 , ReligionStarter 1 , PublicFaith 1 , LoyaltyStarter 1",
        ancillaries=create_ancillaries(),
        army_units=create_army()
    )
    
def create_pope_character(capital_region):
    
    return MaleCharacter(
        character_name="",
        role=Role.LEADER,
        age=40,
        positionX=capital_region.settlement_positionX,
        positionY=capital_region.settlement_positionY,
        traits="traits IAmPope 1 , GoodCommander 2 , PoliticsSkill 3 , PublicFaith 1 , GoodAdministrator 2 , Austere 1 , Intelligent 2 , ReligionStarter 1 , Fertile 1",
        ancillaries=create_ancillaries(),
        army_units=create_army()
    )
    
def create_slave_character(x, y, faction):
    
    return MaleCharacter(
        character_name="",
        role=Role.SLAVER.value + faction.value,
        age=25,
        positionX=x,
        positionY=y,
        traits="GoodCommander 4 , GoodAttacker 3 , PublicFaith 3 , BattleChivalry 4 , StrategyChivalry 3 , ReligiousActivity 2 , ReligionStarter 1",
        ancillaries=None,
        army_units=create_army()
    )
    
def create_ancillaries():
    return None

def create_army():
    return None
        
def assign_names_for_faction(faction, names_list):
    
    for name_block in names_list:
        if name_block.faction == faction:        
            return name_block
        
    return None

def assign_character_names(faction):

    pool = faction.factionCharacterNames
    
    if not pool:
        print(f"No name pool found for {faction.faction_name}")
        return

    royal_surname = ""
    if pool.surnames:
        royal_surname = random.choice(pool.surnames)
        pool.surnames.remove(royal_surname)

    
    for character in faction.characters:
        
        is_male = character.gender == Gender.MALE
        first_pool = pool.male_names if is_male else pool.female_names
        
        if not first_pool:
            continue
        
        fname = random.choice(first_pool)
        first_pool.remove(fname)

        bname = ""
        if character.role in [Role.LEADER, Role.NEVERLEADER, Role.HEIR]:
            # Royals get the pre-selected family name
            sname = royal_surname
            # Optional: Give royals a byname and remove it from pool
            if pool.bynames:
                bname = random.choice(pool.bynames)
                pool.bynames.remove(bname)
        else:
            # Non-royals get random surnames/bynames
            sname = ""
            if pool.surnames:
                sname = random.choice(pool.surnames)
                pool.surnames.remove(sname)
            
            if pool.bynames:
                bname = random.choice(pool.bynames)
                pool.bynames.remove(bname)

        # 5. Assign and format
        character.character_name = f"{fname} {sname} {bname}".strip().replace("  ", " ")

#character	sub_faction spain, El_Cid, named character, male, age 32, x 160, y 172 
#character	Brian O'Neill, named character, male, leader, age 38, x 137, y 276,
