# Adventurer.gd
# 冒険者クラス - パーティメンバーの基本クラス

extends Node
class_name Adventurer

# 能力値
var max_hp: int = 100
var current_hp: int = 100
var attack: int = 10
var defense: int = 10
var magic: int = 10
var speed: int = 10

# 職業
var job_class: String = "Warrior"

# ステータス
var level: int = 1
var experience: int = 0
var is_alive: bool = true

# 位置情報
var formation_position: int = 0  # 0-2: 前列, 3: 後列

# スキル
var skills: Array = []
var passive_skills: Array = []

# 装備
var weapon: Dictionary = {}
var armor: Dictionary = {}

# 名前
var adventurer_name: String = ""


func _init(p_name: String = "冒険者", p_job_class: String = "Warrior"):
    """初期化"""
    adventurer_name = p_name
    job_class = p_job_class
    _apply_job_base_stats()


func _apply_job_base_stats() -> void:
    """職業に応じた基礎能力値を適用"""
    match job_class:
        "Warrior":
            max_hp = 100
            attack = 15
            defense = 12
            magic = 3
            speed = 8
        "Mage":
            max_hp = 60
            attack = 5
            defense = 5
            magic = 20
            speed = 10
        "Priest":
            max_hp = 70
            attack = 7
            defense = 8
            magic = 15
            speed = 9
        "Thief":
            max_hp = 75
            attack = 12
            defense = 7
            magic = 5
            speed = 18
        "Archer":
            max_hp = 80
            attack = 13
            defense = 8
            magic = 6
            speed = 12

    current_hp = max_hp


func take_damage(damage: int) -> int:
    """ダメージを受ける"""
    var actual_damage = max(1, damage - defense)
    current_hp -= actual_damage

    if current_hp <= 0:
        current_hp = 0
        is_alive = false

    return actual_damage


func heal(amount: int) -> int:
    """回復する"""
    if not is_alive:
        return 0

    var old_hp = current_hp
    current_hp = min(max_hp, current_hp + amount)
    return current_hp - old_hp


func is_in_front_row() -> bool:
    """前列にいるか"""
    return formation_position < 3


func get_position_attack_modifier() -> float:
    """位置による攻撃力修正"""
    return 1.1 if is_in_front_row() else 1.0


func get_position_defense_modifier() -> float:
    """位置による防御力修正"""
    return 1.0 if is_in_front_row() else 1.1


func get_hit_rate() -> float:
    """被弾率"""
    if is_in_front_row():
        return 0.6 / 3.0  # 前列3人で60%を分担
    else:
        return 0.1  # 後列は10%


func get_effective_attack() -> int:
    """実効攻撃力（位置修正込み）"""
    return int(attack * get_position_attack_modifier())


func get_effective_defense() -> int:
    """実効防御力（位置修正込み）"""
    return int(defense * get_position_defense_modifier())


func add_skill(skill: Dictionary) -> void:
    """スキルを追加"""
    skills.append(skill)


func add_passive_skill(skill: Dictionary) -> void:
    """パッシブスキルを追加"""
    passive_skills.append(skill)


func get_status() -> Dictionary:
    """ステータスを取得"""
    return {
        "name": adventurer_name,
        "job_class": job_class,
        "level": level,
        "hp": "%d/%d" % [current_hp, max_hp],
        "attack": get_effective_attack(),
        "defense": get_effective_defense(),
        "magic": magic,
        "speed": speed,
        "is_alive": is_alive,
        "position": "前列" if is_in_front_row() else "後列"
    }


func to_dict() -> Dictionary:
    """辞書形式にシリアライズ"""
    return {
        "name": adventurer_name,
        "job_class": job_class,
        "level": level,
        "max_hp": max_hp,
        "current_hp": current_hp,
        "attack": attack,
        "defense": defense,
        "magic": magic,
        "speed": speed,
        "formation_position": formation_position,
        "is_alive": is_alive,
        "skills": skills,
        "passive_skills": passive_skills
    }
