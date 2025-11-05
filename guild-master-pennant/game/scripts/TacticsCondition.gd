# TacticsCondition.gd
# 戦術条件 - HP、敵タイプなどの条件判定

extends Node
class_name TacticsCondition


# HP条件
static func hp_below_percent(unit, percent: float) -> bool:
    """HP が指定パーセント以下"""
    return unit.current_hp < unit.max_hp * percent


static func hp_above_percent(unit, percent: float) -> bool:
    """HP が指定パーセント以上"""
    return unit.current_hp >= unit.max_hp * percent


static func hp_below_value(unit, value: int) -> bool:
    """HP が指定値以下"""
    return unit.current_hp <= value


# 敵条件
static func enemy_count_above(enemies: Array, count: int) -> bool:
    """生存している敵が指定数以上"""
    var alive_count = 0
    for enemy in enemies:
        if enemy.is_alive:
            alive_count += 1
    return alive_count >= count


static func enemy_count_below(enemies: Array, count: int) -> bool:
    """生存している敵が指定数以下"""
    var alive_count = 0
    for enemy in enemies:
        if enemy.is_alive:
            alive_count += 1
    return alive_count <= count


static func has_enemy_type(enemies: Array, enemy_type: String) -> bool:
    """指定タイプの敵がいる"""
    for enemy in enemies:
        if enemy.is_alive and "type" in enemy and enemy.type == enemy_type:
            return true
    return false


# 味方条件
static func has_injured_ally(party: Array, threshold: float = 0.8) -> bool:
    """負傷した味方がいる"""
    for member in party:
        if member.is_alive and member.current_hp < member.max_hp * threshold:
            return true
    return false


static func ally_count_below(party: Array, count: int) -> bool:
    """生存している味方が指定数以下"""
    var alive_count = 0
    for member in party:
        if member.is_alive:
            alive_count += 1
    return alive_count <= count


# 位置条件
static func is_in_front_row(unit) -> bool:
    """前列にいる"""
    return unit.is_in_front_row() if "is_in_front_row" in unit else unit.formation_position < 3


static func is_in_back_row(unit) -> bool:
    """後列にいる"""
    return not is_in_front_row(unit)


# スキル条件
static func has_skill(unit, skill_name: String) -> bool:
    """指定スキルを持っている"""
    if "skills" in unit:
        for skill in unit.skills:
            if skill.name == skill_name:
                return true
    return false


static func can_use_magic(unit) -> bool:
    """魔法が使える"""
    return unit.magic > 0


# 複合条件
static func and_condition(conditions: Array) -> bool:
    """すべての条件を満たす"""
    for condition in conditions:
        if not condition:
            return false
    return true


static func or_condition(conditions: Array) -> bool:
    """いずれかの条件を満たす"""
    for condition in conditions:
        if condition:
            return true
    return false


# よく使う条件のプリセット
static func emergency_condition(unit, party: Array) -> bool:
    """緊急状態（HPが30%以下または味方が2人以下）"""
    return hp_below_percent(unit, 0.3) or ally_count_below(party, 2)


static func offensive_condition(unit, enemies: Array) -> bool:
    """攻撃的状態（HPが50%以上かつ敵が2体以上）"""
    return hp_above_percent(unit, 0.5) and enemy_count_above(enemies, 2)


static func defensive_condition(unit, party: Array) -> bool:
    """防御的状態（HPが50%以下または負傷した味方がいる）"""
    return hp_below_percent(unit, 0.5) or has_injured_ally(party, 0.7)
