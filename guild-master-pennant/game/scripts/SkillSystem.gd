# SkillSystem.gd
# スキルシステム - パワプロ特能風スキル管理

extends Node

var active_buffs: Dictionary = {}  # {unit_id: [buff1, buff2, ...]}


func execute_skill(caster, skill: Dictionary, target) -> Dictionary:
    """スキルを実行"""
    var result = {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": false,
        "effects": []
    }

    match skill.type:
        "attack":
            result = _execute_attack_skill(caster, skill, target)

        "magic_attack":
            result = _execute_magic_attack_skill(caster, skill, target)

        "heal":
            result = _execute_heal_skill(caster, skill, target)

        "buff":
            result = _execute_buff_skill(caster, skill, target)

    return result


func _execute_attack_skill(caster, skill: Dictionary, target) -> Dictionary:
    """攻撃スキルを実行"""
    var damage = CombatAction.calculate_physical_damage(caster, target, skill.multiplier)

    # パッシブスキル: 会心の一撃
    if _check_passive(caster, "critical"):
        damage = int(damage * 2.0)
        print("%s の会心の一撃！" % _get_unit_name(caster))

    var actual_damage = target.take_damage(damage)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "damage": actual_damage
    }


func _execute_magic_attack_skill(caster, skill: Dictionary, target) -> Dictionary:
    """魔法攻撃スキルを実行"""
    var damage = CombatAction.calculate_magic_damage(caster, target, skill.multiplier)
    var actual_damage = target.take_damage(damage)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "damage": actual_damage
    }


func _execute_heal_skill(caster, skill: Dictionary, target) -> Dictionary:
    """回復スキルを実行"""
    var healing = CombatAction.calculate_healing(caster, skill.multiplier)
    var actual_healing = target.heal(healing)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "healing": actual_healing
    }


func _execute_buff_skill(caster, skill: Dictionary, target) -> Dictionary:
    """補助スキルを実行"""
    var buff = {
        "effect": skill.effect,
        "multiplier": skill.multiplier,
        "duration": skill.duration,
        "remaining_turns": skill.duration
    }

    var unit_id = _get_unit_id(target)
    if not active_buffs.has(unit_id):
        active_buffs[unit_id] = []

    active_buffs[unit_id].append(buff)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "buff": skill.effect
    }


func _check_passive(unit, passive_type: String) -> bool:
    """パッシブスキルの発動判定"""
    if "passive_skills" not in unit:
        return false

    for passive in unit.passive_skills:
        if passive.effect == passive_type:
            return randf() < passive.chance

    return false


func update_buffs_turn() -> void:
    """バフのターン経過処理"""
    for unit_id in active_buffs.keys():
        var buffs = active_buffs[unit_id]
        var remaining_buffs = []

        for buff in buffs:
            buff.remaining_turns -= 1
            if buff.remaining_turns > 0:
                remaining_buffs.append(buff)

        if remaining_buffs.size() > 0:
            active_buffs[unit_id] = remaining_buffs
        else:
            active_buffs.erase(unit_id)


func get_buff_multiplier(unit, stat_type: String) -> float:
    """バフによる能力値倍率を取得"""
    var unit_id = _get_unit_id(unit)

    if not active_buffs.has(unit_id):
        return 1.0

    var multiplier = 1.0
    for buff in active_buffs[unit_id]:
        if buff.effect == stat_type:
            multiplier *= buff.multiplier

    return multiplier


func clear_all_buffs() -> void:
    """すべてのバフをクリア"""
    active_buffs.clear()


func _get_unit_id(unit) -> String:
    """ユニットIDを取得"""
    if "adventurer_name" in unit:
        return unit.adventurer_name
    return str(unit.get_instance_id())


func _get_unit_name(unit) -> String:
    """ユニット名を取得"""
    if "adventurer_name" in unit:
        return unit.adventurer_name
    return "Enemy"
