from enum import Enum

class Religion(Enum):
    CATHOLIC = "catholic"
    ORTHODOX = "orthodox"
    ISLAM = "islam"
    PAGANISM = "pagan"
    HERETIC = "heretic"
    SUNGOD = "sungod"

class FactionEnum(Enum):
    WALES = "wales"
    IRELAND = "ireland"
    NOVGOROD = "novgorod"
    TEUTONIC_ORDER = "teutonic_order"
    LITHUANIA = "lithuania"
    JERUSALEM = "jerusalem"
    ANTIOCH = "antioch"
    NORWAY = "norway"
    SCOTLAND = "scotland"
    MILAN = "milan"
    VENICE = "venice"
    SICILY = "sicily"
    SPAIN = "spain"
    DENMARK = "denmark"
    POLAND = "poland"
    HUNGARY = "hungary"
    RUSSIA = "russia"
    MONGOLS = "mongols"
    EGYPT = "egypt"
    FRANCE = "france"
    ENGLAND = "england"
    TURKS = "turks"
    MOORS = "moors"
    HOLY_ROMAN_EMPIRE = "hre"
    BYZANTIUM = "byzantium"
    PORTUGAL = "portugal"
    TIMURIDS = "timurids"
    AZTECS = "aztecs"
    PAPAL_STATES = "papal_states"
    SLAVE = "slave"
    
class AIModel(Enum):
    BALANCED_SMITH = "balanced smith"
    
class Role(Enum):
    LEADER = "leader"
    HEIR = "heir"
    NEVERLEADER="never_a_leader"
    SLAVER="sub faction "
        
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
        