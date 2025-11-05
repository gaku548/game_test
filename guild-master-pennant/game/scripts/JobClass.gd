# JobClass.gd
# 職業定義 - 5つの職業と基礎能力値

extends Node
class_name JobClass

# 職業一覧
enum Job {
    WARRIOR,
    MAGE,
    PRIEST,
    THIEF,
    ARCHER
}

# 職業データ
const JOB_DATA: Dictionary = {
    "Warrior": {
        "base_hp": 100,
        "base_attack": 15,
        "base_defense": 12,
        "base_magic": 3,
        "base_speed": 8,
        "description": "高いHPと攻撃力を持つ前衛職"
    },
    "Mage": {
        "base_hp": 60,
        "base_attack": 5,
        "base_defense": 5,
        "base_magic": 20,
        "base_speed": 10,
        "description": "魔力が高く、魔法攻撃に特化"
    },
    "Priest": {
        "base_hp": 70,
        "base_attack": 7,
        "base_defense": 8,
        "base_magic": 15,
        "base_speed": 9,
        "description": "回復魔法と補助魔法が得意"
    },
    "Thief": {
        "base_hp": 75,
        "base_attack": 12,
        "base_defense": 7,
        "base_magic": 5,
        "base_speed": 18,
        "description": "高速で回避率が高い"
    },
    "Archer": {
        "base_hp": 80,
        "base_attack": 13,
        "base_defense": 8,
        "base_magic": 6,
        "base_speed": 12,
        "description": "後列から安定した火力を提供"
    },
}


static func get_job_name(job: Job) -> String:
    """職業名を取得"""
    match job:
        Job.WARRIOR:
            return "Warrior"
        Job.MAGE:
            return "Mage"
        Job.PRIEST:
            return "Priest"
        Job.THIEF:
            return "Thief"
        Job.ARCHER:
            return "Archer"
    return "Unknown"


static func get_job_data(job_name: String) -> Dictionary:
    """職業データを取得"""
    return JOB_DATA.get(job_name, {})


static func get_all_jobs() -> Array:
    """すべての職業名を取得"""
    return JOB_DATA.keys()


static func create_adventurer(name: String, job_name: String) -> Adventurer:
    """冒険者を作成"""
    return Adventurer.new(name, job_name)
