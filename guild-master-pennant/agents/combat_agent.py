"""
Combat Agent - 戦闘システムの担当エージェント

ユニコーンオーバーロード風の自動戦闘システムを実装する。
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class CombatAgent(BaseAgent):
    """
    戦闘システムの設計と実装を担当するエージェント

    責務:
    - 自動戦闘システムの実装
    - ターン管理
    - ダメージ計算
    - 戦闘結果の判定
    """

    def __init__(self, blackboard):
        super().__init__(
            name="CombatAgent",
            blackboard=blackboard,
            role="戦闘システムの設計と実装"
        )
        self._initialized = False
        self._gdscript_generated = False

    def think(self) -> None:
        """
        戦闘システムの自律的な設計と実装
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
        self.logger.info("Initializing Combat System...")

        self.update_task_status(
            "combat_system",
            "in_progress",
            "Designing auto-battle system"
        )

        self.record_decision(
            decision="Implement Unicorn Overlord-style auto-battle",
            rationale="戦術に基づく自動戦闘で、プレイヤーは戦術設定に集中できる"
        )

        self._initialized = True
        self.send_message("all", "Combat system initialized", "info")

    def _generate_gdscript(self) -> None:
        """
        戦闘システムのGDScriptを生成
        """
        self.logger.info("Generating Combat GDScript...")

        # CombatManager.gd の生成
        combat_manager_script = self._create_combat_manager_script()
        self.generate_file(
            filepath="game/scripts/CombatManager.gd",
            content=combat_manager_script,
            description="戦闘管理 - ターン制自動戦闘システム"
        )

        # CombatAction.gd の生成
        combat_action_script = self._create_combat_action_script()
        self.generate_file(
            filepath="game/scripts/CombatAction.gd",
            content=combat_action_script,
            description="戦闘アクション - 行動の実行と結果計算"
        )

        self._gdscript_generated = True
        self.update_task_status(
            "combat_system",
            "completed",
            "Combat GDScript generated successfully"
        )

        self.send_message(
            "all",
            "Combat system GDScript generated",
            "info",
            {"files": ["CombatManager.gd", "CombatAction.gd"]}
        )

    def _create_combat_manager_script(self) -> str:
        """
        CombatManager.gd スクリプトを生成
        """
        return '''# CombatManager.gd
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
    _log("\\n--- ターン %d ---" % turn_number)

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
    _log("\\n=== 戦闘終了 ===")

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
'''

    def _create_combat_action_script(self) -> str:
        """
        CombatAction.gd スクリプトを生成
        """
        return '''# CombatAction.gd
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
'''

    def _handle_message(self, message: Dict) -> None:
        """
        メッセージを処理
        """
        msg_type = message.get("type")
        sender = message.get("sender")
        content = message.get("content")

        if msg_type == "request":
            if "combat" in content.lower():
                self.send_message(
                    sender,
                    "Combat system is ready. Auto-battle with tactics support.",
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
