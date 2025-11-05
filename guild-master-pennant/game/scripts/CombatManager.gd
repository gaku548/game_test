# CombatManager.gd
# 戦闘管理 - ターン制自動戦闘システム

extends Node
class_name CombatManager

signal combat_started
signal turn_executed(turn_number: int, results: Array)
signal combat_ended(victory: bool)

var party: Array = []  # 味方パーティ
var enemies: Array = []  # 敵パーティ
var turn_number: int = 0
var is_combat_active: bool = false
var combat_log: Array = []


func start_combat(p_party: Array, p_enemies: Array) -> void:
    """戦闘開始"""
    party = p_party
    enemies = p_enemies
    turn_number = 0
    is_combat_active = true
    combat_log.clear()

    _log("=== 戦闘開始 ===")
    emit_signal("combat_started")


func execute_turn() -> Array:
    """1ターンを実行"""
    if not is_combat_active:
        return []

    turn_number += 1
    _log("\n--- ターン %d ---" % turn_number)

    var turn_results = []

    # 行動順を決定（速度順）
    var action_order = _determine_action_order()

    # 各ユニットが行動
    for unit in action_order:
        if not unit.is_alive:
            continue

        # 戦術に基づいて行動を決定
        var action = _determine_action(unit)

        # 行動を実行
        var result = _execute_action(unit, action)
        turn_results.append(result)

        # 勝敗判定
        if _check_victory():
            _end_combat(true)
            break
        if _check_defeat():
            _end_combat(false)
            break

    emit_signal("turn_executed", turn_number, turn_results)
    return turn_results


func _determine_action_order() -> Array:
    """行動順を決定（速度順）"""
    var all_units = party + enemies
    var alive_units = []

    for unit in all_units:
        if unit.is_alive:
            alive_units.append(unit)

    # 速度でソート
    alive_units.sort_custom(func(a, b): return a.speed > b.speed)
    return alive_units


func _determine_action(unit) -> Dictionary:
    """ユニットの行動を決定（戦術システムと連携）"""
    # 戦術システムがない場合は基本行動
    var is_enemy = unit in enemies

    if is_enemy:
        # 敵は単純な攻撃
        var targets = _get_alive_units(party)
        if targets.size() > 0:
            return {
                "type": "attack",
                "actor": unit,
                "target": _select_target_by_hit_rate(targets)
            }
    else:
        # 味方は戦術に基づく（TacticsSystemと連携）
        var tactics_system = get_node_or_null("/root/TacticsSystem")
        if tactics_system:
            return tactics_system.decide_action(unit, party, enemies)
        else:
            # 戦術システムがない場合は基本攻撃
            var targets = _get_alive_units(enemies)
            if targets.size() > 0:
                return {
                    "type": "attack",
                    "actor": unit,
                    "target": targets[0]  # 最初の敵を攻撃
                }

    return {"type": "wait", "actor": unit}


func _execute_action(actor, action: Dictionary) -> Dictionary:
    """行動を実行"""
    var result = {
        "actor": actor.adventurer_name if "adventurer_name" in actor else "Enemy",
        "action": action.type,
        "success": false
    }

    match action.type:
        "attack":
            var target = action.target
            var damage = _calculate_damage(actor, target)
            var actual_damage = target.take_damage(damage)

            result.success = true
            result.target = target.adventurer_name if "adventurer_name" in target else "Enemy"
            result.damage = actual_damage

            _log("%s が %s に %d ダメージ！" % [result.actor, result.target, actual_damage])

            if not target.is_alive:
                _log("%s は倒れた！" % result.target)

        "skill":
            # スキルシステムと連携
            var skill_system = get_node_or_null("/root/SkillSystem")
            if skill_system:
                result = skill_system.execute_skill(actor, action.skill, action.target)

        "defend":
            result.success = true
            _log("%s は防御した" % result.actor)

        "wait":
            result.success = true

    return result


func _calculate_damage(attacker, defender) -> int:
    """ダメージ計算"""
    var base_damage = attacker.get_effective_attack() if "get_effective_attack" in attacker else attacker.attack
    var defense = defender.get_effective_defense() if "get_effective_defense" in defender else defender.defense

    # 基本ダメージ = 攻撃力 - 防御力 / 2
    var damage = base_damage - (defense / 2)

    # ランダム要素 (90% ~ 110%)
    damage = int(damage * randf_range(0.9, 1.1))

    return max(1, damage)


func _select_target_by_hit_rate(targets: Array):
    """被弾率に基づいてターゲットを選択"""
    var total_weight = 0.0
    var weights = []

    for target in targets:
        var hit_rate = target.get_hit_rate() if "get_hit_rate" in target else 1.0 / targets.size()
        weights.append(hit_rate)
        total_weight += hit_rate

    var rand = randf() * total_weight
    var cumulative = 0.0

    for i in range(targets.size()):
        cumulative += weights[i]
        if rand <= cumulative:
            return targets[i]

    return targets[0]


func _get_alive_units(units: Array) -> Array:
    """生存しているユニットを取得"""
    var alive = []
    for unit in units:
        if unit.is_alive:
            alive.append(unit)
    return alive


func _check_victory() -> bool:
    """勝利判定"""
    return _get_alive_units(enemies).size() == 0


func _check_defeat() -> bool:
    """敗北判定"""
    return _get_alive_units(party).size() == 0


func _end_combat(victory: bool) -> void:
    """戦闘終了"""
    is_combat_active = false
    _log("\n=== 戦闘終了 ===")

    if victory:
        _log("勝利！")
    else:
        _log("敗北...")

    emit_signal("combat_ended", victory)


func _log(message: String) -> void:
    """ログ記録"""
    combat_log.append(message)
    print(message)


func get_combat_log() -> Array:
    """戦闘ログを取得"""
    return combat_log


func is_active() -> bool:
    """戦闘中かどうか"""
    return is_combat_active
