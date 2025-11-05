"""
Tactics Agent - 戦術システムの担当エージェント

ユニコーンオーバーロード風の戦術設定と条件分岐行動を実装する。
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class TacticsAgent(BaseAgent):
    """
    戦術システムの設計と実装を担当するエージェント

    責務:
    - 戦術の条件定義
    - 行動の優先度管理
    - AI行動決定ロジック
    """

    def __init__(self, blackboard):
        super().__init__(
            name="TacticsAgent",
            blackboard=blackboard,
            role="戦術システムの設計と実装"
        )
        self._initialized = False
        self._gdscript_generated = False

    def think(self) -> None:
        """
        戦術システムの自律的な設計と実装
        """
        if not self._initialized:
            self._initialize()
            return

        if not self._gdscript_generated:
            self._generate_gdscript()
            return

        messages = self.get_new_messages()
        for message in messages:
            self._handle_message(message)

    def _initialize(self) -> None:
        """
        初期化処理
        """
        self.logger.info("Initializing Tactics System...")

        self.update_task_status(
            "tactics_system",
            "in_progress",
            "Designing conditional tactics system"
        )

        self.record_decision(
            decision="Implement priority-based conditional tactics",
            rationale="条件（HP, 敵の種類など）→行動の優先度リストで柔軟な戦術を実現"
        )

        self._initialized = True
        self.send_message("all", "Tactics system initialized", "info")

    def _generate_gdscript(self) -> None:
        """
        戦術システムのGDScriptを生成
        """
        self.logger.info("Generating Tactics GDScript...")

        # TacticsSystem.gd の生成
        tactics_system_script = self._create_tactics_system_script()
        self.generate_file(
            filepath="game/scripts/TacticsSystem.gd",
            content=tactics_system_script,
            description="戦術システム - 条件分岐と優先度管理"
        )

        # TacticsCondition.gd の生成
        tactics_condition_script = self._create_tactics_condition_script()
        self.generate_file(
            filepath="game/scripts/TacticsCondition.gd",
            content=tactics_condition_script,
            description="戦術条件 - HP、敵タイプなどの条件判定"
        )

        self._gdscript_generated = True
        self.update_task_status(
            "tactics_system",
            "completed",
            "Tactics GDScript generated successfully"
        )

        self.send_message(
            "all",
            "Tactics system GDScript generated",
            "info",
            {"files": ["TacticsSystem.gd", "TacticsCondition.gd"]}
        )

    def _create_tactics_system_script(self) -> str:
        """
        TacticsSystem.gd スクリプトを生成
        """
        return '''# TacticsSystem.gd
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
'''

    def _create_tactics_condition_script(self) -> str:
        """
        TacticsCondition.gd スクリプトを生成
        """
        return '''# TacticsCondition.gd
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
'''

    def _handle_message(self, message: Dict) -> None:
        """
        メッセージを処理
        """
        msg_type = message.get("type")
        sender = message.get("sender")
        content = message.get("content")

        if msg_type == "request":
            if "tactics" in content.lower():
                self.send_message(
                    sender,
                    "Tactics system is ready. Priority-based conditional actions.",
                    "response"
                )

    def get_status(self) -> Dict[str, Any]:
        """
        エージェントの現在の状態を取得
        """
        return {
            "name": self.name,
            "role": self.role,
            "initialized": self._initialized,
            "gdscript_generated": self._gdscript_generated
        }
