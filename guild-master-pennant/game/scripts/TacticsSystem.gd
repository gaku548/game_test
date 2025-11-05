# TacticsSystem.gd
# 戦術システム - 条件分岐と優先度管理

extends Node

# 戦術ルール
class TacticRule:
    var priority: int = 0
    var condition: Callable
    var action_type: String = "attack"
    var action_params: Dictionary = {}

    func _init(p_priority: int, p_condition: Callable, p_action_type: String, p_params: Dictionary = {}):
        priority = p_priority
        condition = p_condition
        action_type = p_action_type
        action_params = p_params


# 各ユニットの戦術セット
var unit_tactics: Dictionary = {}


func set_unit_tactics(unit, tactics: Array) -> void:
    """ユニットに戦術を設定"""
    var unit_id = _get_unit_id(unit)
    unit_tactics[unit_id] = tactics


func decide_action(unit, party: Array, enemies: Array) -> Dictionary:
    """戦術に基づいて行動を決定"""
    var unit_id = _get_unit_id(unit)

    if not unit_tactics.has(unit_id):
        # デフォルト戦術を設定
        _set_default_tactics(unit)

    var tactics = unit_tactics[unit_id]

    # 優先度順にソート済みと仮定
    tactics.sort_custom(func(a, b): return a.priority > b.priority)

    # 条件を満たす最初のルールを実行
    for rule in tactics:
        if rule.condition.call(unit, party, enemies):
            return _create_action(unit, rule, party, enemies)

    # どの条件も満たさない場合は待機
    return {"type": "wait", "actor": unit}


func _set_default_tactics(unit) -> void:
    """デフォルト戦術を設定"""
    var tactics = []

    match unit.job_class:
        "Warrior":
            # 戦士: HPが低い敵を優先攻撃
            tactics.append(TacticRule.new(
                10,
                func(u, p, e): return true,
                "attack",
                {"target_selection": "lowest_hp"}
            ))

        "Mage":
            # 魔法使い: HPが50%以下なら防御、それ以外は魔法攻撃
            tactics.append(TacticRule.new(
                20,
                func(u, p, e): return u.current_hp < u.max_hp * 0.5,
                "defend"
            ))
            tactics.append(TacticRule.new(
                10,
                func(u, p, e): return u.magic > 0,
                "skill",
                {"skill_name": "ファイア"}
            ))

        "Priest":
            # 僧侶: 味方のHPが50%以下なら回復、それ以外は攻撃
            tactics.append(TacticRule.new(
                30,
                func(u, p, e): return _has_injured_ally(p, 0.5),
                "skill",
                {"skill_name": "ヒール", "target_selection": "lowest_hp_ally"}
            ))
            tactics.append(TacticRule.new(
                10,
                func(u, p, e): return true,
                "attack"
            ))

        "Thief":
            # 盗賊: 敵が2体以上なら範囲攻撃、それ以外は通常攻撃
            tactics.append(TacticRule.new(
                20,
                func(u, p, e): return _count_alive(e) >= 2,
                "skill",
                {"skill_name": "乱れ撃ち"}
            ))
            tactics.append(TacticRule.new(
                10,
                func(u, p, e): return true,
                "attack"
            ))

        "Archer":
            # 弓使い: 常に通常攻撃
            tactics.append(TacticRule.new(
                10,
                func(u, p, e): return true,
                "attack"
            ))

    set_unit_tactics(unit, tactics)


func _create_action(unit, rule: TacticRule, party: Array, enemies: Array) -> Dictionary:
    """ルールから行動を作成"""
    var action = {
        "type": rule.action_type,
        "actor": unit
    }

    match rule.action_type:
        "attack":
            var target = _select_target(enemies, rule.action_params.get("target_selection", "random"))
            action.target = target

        "skill":
            var skill_name = rule.action_params.get("skill_name", "")
            var skill = _find_skill(unit, skill_name)

            if skill:
                action.skill = skill

                var target_selection = rule.action_params.get("target_selection", "random")
                if target_selection == "lowest_hp_ally":
                    action.target = _select_target(party, "lowest_hp")
                else:
                    action.target = _select_target(enemies, target_selection)
            else:
                # スキルがない場合は攻撃
                action.type = "attack"
                action.target = _select_target(enemies, "random")

        "defend":
            pass  # 防御は特にターゲット不要

    return action


func _select_target(targets: Array, selection_method: String):
    """ターゲットを選択"""
    var alive_targets = []
    for t in targets:
        if t.is_alive:
            alive_targets.append(t)

    if alive_targets.size() == 0:
        return null

    match selection_method:
        "lowest_hp":
            var lowest = alive_targets[0]
            for t in alive_targets:
                if t.current_hp < lowest.current_hp:
                    lowest = t
            return lowest

        "highest_hp":
            var highest = alive_targets[0]
            for t in alive_targets:
                if t.current_hp > highest.current_hp:
                    highest = t
            return highest

        "random":
            return alive_targets[randi() % alive_targets.size()]

    return alive_targets[0]


func _find_skill(unit, skill_name: String) -> Dictionary:
    """ユニットからスキルを検索"""
    if "skills" in unit:
        for skill in unit.skills:
            if skill.name == skill_name:
                return skill
    return {}


func _has_injured_ally(party: Array, threshold: float) -> bool:
    """負傷した味方がいるか"""
    for member in party:
        if member.is_alive and member.current_hp < member.max_hp * threshold:
            return true
    return false


func _count_alive(units: Array) -> int:
    """生存ユニット数を数える"""
    var count = 0
    for unit in units:
        if unit.is_alive:
            count += 1
    return count


func _get_unit_id(unit) -> String:
    """ユニットの一意IDを取得"""
    if "adventurer_name" in unit:
        return unit.adventurer_name
    return str(unit.get_instance_id())


func create_custom_tactic(priority: int, condition: Callable, action_type: String, params: Dictionary = {}) -> TacticRule:
    """カスタム戦術を作成"""
    return TacticRule.new(priority, condition, action_type, params)


func get_tactics_description(unit) -> Array:
    """戦術の説明を取得"""
    var unit_id = _get_unit_id(unit)

    if not unit_tactics.has(unit_id):
        return []

    var tactics = unit_tactics[unit_id]
    var descriptions = []

    for rule in tactics:
        descriptions.append({
            "priority": rule.priority,
            "action": rule.action_type,
            "params": rule.action_params
        })

    return descriptions
