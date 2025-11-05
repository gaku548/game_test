"""
CombatAgent - 戦闘システムの設計と実装を担当

CombatManager.gd と CombatAction.gd を生成する
"""

from .base_agent import BaseAgent


class CombatAgent(BaseAgent):
    """
    戦闘システムを担当するエージェント

    責務:
    - ターン制戦闘システムの設計
    - ダメージ計算の実装
    - 行動順決定ロジック
    - 戦闘状態管理
    """

    def __init__(self, blackboard):
        super().__init__("CombatAgent", blackboard, "Combat System Designer")

    def think(self) -> None:
        """戦闘システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_combat_action_script()
        self._generate_combat_manager_script()

        # 完了を通知
        self.broadcast("戦闘システムのGDScriptを生成しました")
        self.update_task("combat_system", "completed", "CombatManager.gd and CombatAction.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing CombatAgent...")

        self.record_decision(
            "戦闘システムの設計",
            "速度順のターン制戦闘。位置による被弾率を考慮したターゲット選択。"
            "ダメージ計算は攻撃力-防御力/2の基本式に乱数を加える。"
        )

        self.update_task("combat_system", "in_progress", "Designing turn-based combat")
        self._initialized = True

    def _generate_combat_action_script(self) -> None:
        """CombatAction.gd を生成"""
        script = '''# CombatAction.gd
# 戦闘アクション - 攻撃、防御、スキルなどの行動を表現

extends Resource
class_name CombatAction

enum ActionType {
\tATTACK,
\tDEFEND,
\tSKILL,
\tITEM,
\tWAIT
}

var action_type: ActionType = ActionType.ATTACK
var actor: Adventurer = null
var target: Resource = null  # Adventurer or Enemy
var skill: Resource = null
var item: Resource = null

func _init(type: ActionType = ActionType.ATTACK):
\taction_type = type

# ダメージを計算（攻撃アクション）
static func calculate_damage(attacker: Resource, defender: Resource) -> int:
\tvar base_damage: int = 0
\t
\t# 攻撃力を取得
\tif attacker.has_method("get_effective_attack"):
\t\tbase_damage = attacker.get_effective_attack()
\telse:
\t\tbase_damage = attacker.attack if "attack" in attacker else 10
\t
\t# 防御力を取得
\tvar defense: int = 0
\tif defender.has_method("get_effective_defense"):
\t\tdefense = defender.get_effective_defense()
\telse:
\t\tdefense = defender.defense if "defense" in defender else 5
\t
\t# ダメージ計算: 攻撃力 - 防御力/2
\tvar damage = base_damage - (defense / 2)
\t
\t# 乱数要素 (90% - 110%)
\tvar random_factor = randf_range(0.9, 1.1)
\tdamage = int(damage * random_factor)
\t
\t# 最低1ダメージ
\treturn max(1, damage)

# アクションを実行
func execute() -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"damage": 0,
\t\t"healing": 0,
\t\t"message": ""
\t}
\t
\tif actor == null:
\t\tresult["message"] = "No actor"
\t\treturn result
\t
\tmatch action_type:
\t\tActionType.ATTACK:
\t\t\tresult = _execute_attack()
\t\tActionType.DEFEND:
\t\t\tresult = _execute_defend()
\t\tActionType.SKILL:
\t\t\tresult = _execute_skill()
\t\tActionType.ITEM:
\t\t\tresult = _execute_item()
\t\tActionType.WAIT:
\t\t\tresult["success"] = true
\t\t\tresult["message"] = actor.adventurer_name + " waits"
\t
\treturn result

# 攻撃を実行
func _execute_attack() -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"damage": 0,
\t\t"message": ""
\t}
\t
\tif target == null:
\t\tresult["message"] = "No target"
\t\treturn result
\t
\tif not target.is_alive:
\t\tresult["message"] = "Target is already defeated"
\t\treturn result
\t
\t# ダメージ計算
\tvar damage = calculate_damage(actor, target)
\tvar actual_damage = target.take_damage(damage)
\t
\tresult["success"] = true
\tresult["damage"] = actual_damage
\t
\tvar attacker_name = actor.adventurer_name if "adventurer_name" in actor else actor.name
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tresult["message"] = "%s attacks %s for %d damage!" % [attacker_name, target_name, actual_damage]
\t
\tif not target.is_alive:
\t\tresult["message"] += " %s is defeated!" % target_name
\t
\treturn result

# 防御を実行
func _execute_defend() -> Dictionary:
\tvar result = {
\t\t"success": true,
\t\t"message": ""
\t}
\t
\tvar actor_name = actor.adventurer_name if "adventurer_name" in actor else "Actor"
\tresult["message"] = "%s takes a defensive stance" % actor_name
\t
\t# 防御バフを付与（次のダメージ軽減）
\tif actor.has_method("add_status_effect"):
\t\tactor.add_status_effect("defending", 1)
\t
\treturn result

# スキルを実行
func _execute_skill() -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"message": ""
\t}
\t
\tif skill == null:
\t\tresult["message"] = "No skill selected"
\t\treturn result
\t
\tif skill.has_method("execute"):
\t\tresult = skill.execute(actor, target)
\telse:
\t\tresult["message"] = "Skill cannot be executed"
\t
\treturn result

# アイテムを使用
func _execute_item() -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"message": "Item system not implemented"
\t}
\treturn result
'''

        self.save_gdscript(
            "game/scripts/CombatAction.gd",
            script,
            "Combat action execution with damage calculation and action types"
        )

    def _generate_combat_manager_script(self) -> None:
        """CombatManager.gd を生成"""
        script = '''# CombatManager.gd
# 戦闘管理システム - ターン制戦闘の進行を管理

extends Node
class_name CombatManager

signal combat_started
signal turn_started(turn_number: int)
signal action_executed(action_result: Dictionary)
signal combat_ended(victory: bool)

var party: Array[Adventurer] = []
var enemies: Array[Resource] = []
var current_turn: int = 0
var is_combat_active: bool = false
var combat_log: Array[Dictionary] = []

# 戦闘を開始
func start_combat(party_members: Array[Adventurer], enemy_list: Array[Resource]) -> void:
\tparty = party_members
\tenemies = enemy_list
\tcurrent_turn = 0
\tis_combat_active = true
\tcombat_log.clear()
\t
\tprint("=== Combat Started ===")
\tprint("Party: %d members" % party.size())
\tprint("Enemies: %d" % enemies.size())
\t
\tcombat_started.emit()

# 1ターンを実行
func execute_turn() -> void:
\tif not is_combat_active:
\t\treturn
\t
\tcurrent_turn += 1
\tturn_started.emit(current_turn)
\t
\tprint("\\n--- Turn %d ---" % current_turn)
\t
\t# 行動順を決定（速度順）
\tvar action_order = _determine_action_order()
\t
\t# 各ユニットの行動を実行
\tfor unit_data in action_order:
\t\tvar unit = unit_data["unit"]
\t\tvar is_party_member = unit_data["is_party"]
\t\t
\t\tif not unit.is_alive:
\t\t\tcontinue
\t\t
\t\t# 行動を決定
\t\tvar action = _decide_action(unit, is_party_member)
\t\t
\t\t# 行動を実行
\t\tvar result = action.execute()
\t\tcombat_log.append(result)
\t\taction_executed.emit(result)
\t\t
\t\tif result["success"]:
\t\t\tprint(result["message"])
\t
\t# 勝敗判定
\t_check_victory_condition()

# 行動順を決定（速度順）
func _determine_action_order() -> Array[Dictionary]:
\tvar all_units: Array[Dictionary] = []
\t
\t# パーティメンバーを追加
\tfor member in party:
\t\tif member.is_alive:
\t\t\tall_units.append({"unit": member, "is_party": true, "speed": member.speed})
\t
\t# 敵を追加
\tfor enemy in enemies:
\t\tif enemy.is_alive:
\t\t\tall_units.append({"unit": enemy, "is_party": false, "speed": enemy.speed})
\t
\t# 速度でソート
\tall_units.sort_custom(func(a, b): return a["speed"] > b["speed"])
\t
\treturn all_units

# 行動を決定
func _decide_action(unit: Resource, is_party_member: bool) -> CombatAction:
\tvar action = CombatAction.new(CombatAction.ActionType.ATTACK)
\taction.actor = unit
\t
\t# ターゲット選択
\tif is_party_member:
\t\t# 味方 → 敵を攻撃
\t\tvar alive_enemies = enemies.filter(func(e): return e.is_alive)
\t\tif alive_enemies.size() > 0:
\t\t\taction.target = alive_enemies[0]  # 最初の敵を攻撃
\telse:
\t\t# 敵 → 味方を攻撃（被弾率に基づく）
\t\tvar alive_party = party.filter(func(p): return p.is_alive)
\t\tif alive_party.size() > 0:
\t\t\taction.target = _select_target_by_hit_rate(alive_party)
\t
\treturn action

# 被弾率に基づいてターゲットを選択
func _select_target_by_hit_rate(targets: Array) -> Resource:
\tvar total_weight: float = 0.0
\tvar weights: Array[float] = []
\t
\tfor target in targets:
\t\tvar hit_rate = target.get_hit_rate() if target.has_method("get_hit_rate") else 1.0 / targets.size()
\t\tweights.append(hit_rate)
\t\ttotal_weight += hit_rate
\t
\tvar rand = randf() * total_weight
\tvar cumulative: float = 0.0
\t
\tfor i in range(targets.size()):
\t\tcumulative += weights[i]
\t\tif rand <= cumulative:
\t\t\treturn targets[i]
\t
\treturn targets[0]

# 勝敗判定
func _check_victory_condition() -> void:
\tvar party_alive = party.any(func(p): return p.is_alive)
\tvar enemies_alive = enemies.any(func(e): return e.is_alive)
\t
\tif not party_alive:
\t\t_end_combat(false)
\telif not enemies_alive:
\t\t_end_combat(true)

# 戦闘終了
func _end_combat(victory: bool) -> void:
\tis_combat_active = false
\t
\tprint("\\n=== Combat Ended ===")
\tif victory:
\t\tprint("Victory!")
\telse:
\t\tprint("Defeat...")
\t
\tcombat_ended.emit(victory)

# 戦闘ログを取得
func get_combat_log() -> Array[Dictionary]:
\treturn combat_log.duplicate()

# 戦闘状態を取得
func is_active() -> bool:
\treturn is_combat_active
'''

        self.save_gdscript(
            "game/scripts/CombatManager.gd",
            script,
            "Turn-based combat manager with speed-based action order"
        )
