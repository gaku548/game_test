# CombatAction.gd
# 戦闘アクション - 行動の実行と結果計算

extends Node
class_name CombatAction

# アクションタイプ
enum ActionType {
    ATTACK,
    SKILL,
    DEFEND,
    WAIT,
    ITEM
}


static func create_attack_action(actor, target) -> Dictionary:
    """攻撃アクションを作成"""
    return {
        "type": "attack",
        "actor": actor,
        "target": target
    }


static func create_skill_action(actor, skill: Dictionary, target) -> Dictionary:
    """スキルアクションを作成"""
    return {
        "type": "skill",
        "actor": actor,
        "skill": skill,
        "target": target
    }


static func create_defend_action(actor) -> Dictionary:
    """防御アクションを作成"""
    return {
        "type": "defend",
        "actor": actor
    }


static func create_wait_action(actor) -> Dictionary:
    """待機アクションを作成"""
    return {
        "type": "wait",
        "actor": actor
    }


static func calculate_physical_damage(attacker, defender, multiplier: float = 1.0) -> int:
    """物理ダメージを計算"""
    var attack_power = attacker.get_effective_attack() if "get_effective_attack" in attacker else attacker.attack
    var defense_power = defender.get_effective_defense() if "get_effective_defense" in defender else defender.defense

    var base_damage = attack_power * multiplier - (defense_power / 2)
    var damage = int(base_damage * randf_range(0.9, 1.1))

    return max(1, damage)


static func calculate_magic_damage(attacker, defender, multiplier: float = 1.0) -> int:
    """魔法ダメージを計算"""
    var magic_power = attacker.magic
    var magic_defense = defender.defense / 3  # 魔法防御は物理防御の1/3

    var base_damage = magic_power * multiplier - magic_defense
    var damage = int(base_damage * randf_range(0.9, 1.1))

    return max(1, damage)


static func calculate_healing(caster, multiplier: float = 1.0) -> int:
    """回復量を計算"""
    var magic_power = caster.magic
    var healing = int(magic_power * multiplier * randf_range(0.95, 1.05))

    return max(1, healing)


static func action_to_string(action: Dictionary) -> String:
    """アクションを文字列に変換"""
    match action.type:
        "attack":
            return "%s の攻撃" % action.actor.adventurer_name
        "skill":
            return "%s の %s" % [action.actor.adventurer_name, action.skill.name]
        "defend":
            return "%s の防御" % action.actor.adventurer_name
        "wait":
            return "%s は様子を見ている" % action.actor.adventurer_name

    return "不明なアクション"
