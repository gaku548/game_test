# Skill.gd
# スキルデータ定義

extends Node
class_name Skill

# スキルタイプ
enum SkillType {
    ATTACK,
    MAGIC_ATTACK,
    HEAL,
    BUFF,
    PASSIVE
}

# すべてのスキルデータ
const SKILL_DATA: Dictionary = {
    "強撃": {
        "name": "強撃",
        "type": "attack",
        "multiplier": 1.5,
        "target": "single",
        "description": "単体に1.5倍の物理ダメージ",
    },
    "ファイア": {
        "name": "ファイア",
        "type": "magic_attack",
        "multiplier": 1.8,
        "target": "single",
        "description": "単体に1.8倍の魔法ダメージ",
    },
    "乱れ撃ち": {
        "name": "乱れ撃ち",
        "type": "attack",
        "multiplier": 0.8,
        "target": "all",
        "description": "全体に0.8倍の物理ダメージ",
    },
    "必殺剣": {
        "name": "必殺剣",
        "type": "attack",
        "multiplier": 2.5,
        "target": "single",
        "description": "単体に2.5倍の強力な物理ダメージ",
    },
    "ヒール": {
        "name": "ヒール",
        "type": "heal",
        "multiplier": 2.0,
        "target": "single",
        "description": "単体のHPを魔力×2.0回復",
    },
    "全体回復": {
        "name": "全体回復",
        "type": "heal",
        "multiplier": 1.2,
        "target": "all_allies",
        "description": "全体のHPを魔力×1.2回復",
    },
    "攻撃強化": {
        "name": "攻撃強化",
        "type": "buff",
        "multiplier": 1.3,
        "target": "single",
        "description": "3ターン攻撃力1.3倍",
        "effect": "attack",
        "duration": 3,
    },
    "防御強化": {
        "name": "防御強化",
        "type": "buff",
        "multiplier": 1.5,
        "target": "single",
        "description": "3ターン防御力1.5倍",
        "effect": "defense",
        "duration": 3,
    },
    "会心の一撃": {
        "name": "会心の一撃",
        "type": "passive",
        "multiplier": 2.0,
        "target": "single",
        "description": "20%の確率でダメージ2.0倍",
        "effect": "critical",
        "chance": 0.2,
    },
    "カウンター": {
        "name": "カウンター",
        "type": "passive",
        "multiplier": 0.5,
        "target": "single",
        "description": "30%の確率で反撃（0.5倍ダメージ）",
        "effect": "counter",
        "chance": 0.3,
    },
    "根性": {
        "name": "根性",
        "type": "passive",
        "multiplier": 1.0,
        "target": "single",
        "description": "15%の確率で致死ダメージをHP1で耐える",
        "effect": "endure",
        "chance": 0.15,
    },
}


static func get_skill(skill_name: String) -> Dictionary:
    """スキルデータを取得"""
    return SKILL_DATA.get(skill_name, {})


static func get_all_skills() -> Dictionary:
    """すべてのスキルを取得"""
    return SKILL_DATA


static func get_skills_by_type(skill_type: String) -> Array:
    """タイプ別にスキルを取得"""
    var filtered = []
    for skill_name in SKILL_DATA:
        var skill = SKILL_DATA[skill_name]
        if skill.type == skill_type:
            filtered.append(skill)
    return filtered


static func get_attack_skills() -> Array:
    """攻撃スキルを取得"""
    return get_skills_by_type("attack") + get_skills_by_type("magic_attack")


static func get_heal_skills() -> Array:
    """回復スキルを取得"""
    return get_skills_by_type("heal")


static func get_buff_skills() -> Array:
    """補助スキルを取得"""
    return get_skills_by_type("buff")


static func get_passive_skills() -> Array:
    """パッシブスキルを取得"""
    return get_skills_by_type("passive")
