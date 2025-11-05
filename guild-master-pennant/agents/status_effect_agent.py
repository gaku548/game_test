"""
StatusEffectAgent - 状態異常システムの設計と実装を担当

StatusEffect.gd と StatusEffectManager.gd を生成する
"""

from .base_agent import BaseAgent


class StatusEffectAgent(BaseAgent):
    """
    状態異常システムを担当するエージェント

    責務:
    - 状態異常の種類定義
    - 状態異常の効果処理
    - 持続ターン管理
    """

    def __init__(self, blackboard):
        super().__init__("StatusEffectAgent", blackboard, "Status Effect System Designer")

    def think(self) -> None:
        """状態異常システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_status_effect_script()
        self._generate_status_effect_manager_script()

        # 完了を通知
        self.broadcast("状態異常システムのGDScriptを生成しました")
        self.update_task("status_effect_system", "completed", "StatusEffect.gd and StatusEffectManager.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing StatusEffectAgent...")

        self.record_decision(
            "状態異常システムの設計",
            "毒、麻痺、気絶、火傷などの状態異常を実装。"
            "ターン経過による効果とバフ/デバフの重複管理。"
        )

        self.update_task("status_effect_system", "in_progress", "Designing status effects")
        self._initialized = True

    def _generate_status_effect_script(self) -> None:
        """StatusEffect.gd を生成"""
        script = '''# StatusEffect.gd
# 状態異常クラス

extends Resource
class_name StatusEffect

enum EffectType {
\tPOISON,         # 毒 - ターン開始時ダメージ
\tBURN,           # 火傷 - ターン開始時ダメージ
\tPARALYZE,       # 麻痺 - 行動不能の確率
\tSTUN,           # 気絶 - 1ターン行動不能
\tSLEEP,          # 睡眠 - 攻撃されるまで行動不能
\tBLIND,          # 盲目 - 命中率低下
\tATTACK_UP,      # 攻撃力上昇
\tDEFENSE_UP,     # 防御力上昇
\tSPEED_UP,       # 速度上昇
\tATTACK_DOWN,    # 攻撃力低下
\tDEFENSE_DOWN,   # 防御力低下
\tSPEED_DOWN,     # 速度低下
\tREGENERATION,   # HP回復
\tINVINCIBLE      # 無敵
}

var effect_type: EffectType = EffectType.POISON
var effect_name: String = ""
var duration: int = 3  # 持続ターン数
var power: int = 5     # 効果の強さ
var is_buff: bool = false  # バフか（true）デバフか（false）

func _init(type: EffectType = EffectType.POISON, turns: int = 3, effect_power: int = 5):
\teffect_type = type
\tduration = turns
\tpower = effect_power
\teffect_name = _get_effect_name()
\tis_buff = _is_buff_type()

# 効果名を取得
func _get_effect_name() -> String:
\tmatch effect_type:
\t\tEffectType.POISON:
\t\t\treturn "Poison"
\t\tEffectType.BURN:
\t\t\treturn "Burn"
\t\tEffectType.PARALYZE:
\t\t\treturn "Paralyze"
\t\tEffectType.STUN:
\t\t\treturn "Stun"
\t\tEffectType.SLEEP:
\t\t\treturn "Sleep"
\t\tEffectType.BLIND:
\t\t\treturn "Blind"
\t\tEffectType.ATTACK_UP:
\t\t\treturn "Attack Up"
\t\tEffectType.DEFENSE_UP:
\t\t\treturn "Defense Up"
\t\tEffectType.SPEED_UP:
\t\t\treturn "Speed Up"
\t\tEffectType.ATTACK_DOWN:
\t\t\treturn "Attack Down"
\t\tEffectType.DEFENSE_DOWN:
\t\t\treturn "Defense Down"
\t\tEffectType.SPEED_DOWN:
\t\t\treturn "Speed Down"
\t\tEffectType.REGENERATION:
\t\t\treturn "Regeneration"
\t\tEffectType.INVINCIBLE:
\t\t\treturn "Invincible"
\t\t_:
\t\t\treturn "Unknown"

# バフタイプか判定
func _is_buff_type() -> bool:
\treturn effect_type in [
\t\tEffectType.ATTACK_UP,
\t\tEffectType.DEFENSE_UP,
\t\tEffectType.SPEED_UP,
\t\tEffectType.REGENERATION,
\t\tEffectType.INVINCIBLE
\t]

# ターン開始時の効果を適用
func apply_turn_effect(target: Resource) -> Dictionary:
\tvar result = {
\t\t"damage": 0,
\t\t"healing": 0,
\t\t"message": ""
\t}
\t
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tmatch effect_type:
\t\tEffectType.POISON:
\t\t\tvar damage = power
\t\t\ttarget.take_damage(damage)
\t\t\tresult["damage"] = damage
\t\t\tresult["message"] = "%s takes %d poison damage" % [target_name, damage]
\t\t
\t\tEffectType.BURN:
\t\t\tvar damage = power
\t\t\ttarget.take_damage(damage)
\t\t\tresult["damage"] = damage
\t\t\tresult["message"] = "%s takes %d burn damage" % [target_name, damage]
\t\t
\t\tEffectType.REGENERATION:
\t\t\tif target.has_method("heal"):
\t\t\t\tvar healing = target.heal(power)
\t\t\t\tresult["healing"] = healing
\t\t\t\tresult["message"] = "%s regenerates %d HP" % [target_name, healing]
\t
\t# ターン数を減少
\tduration -= 1
\t
\treturn result

# 行動可能か判定
func can_act() -> bool:
\tmatch effect_type:
\t\tEffectType.STUN, EffectType.SLEEP:
\t\t\treturn false
\t\tEffectType.PARALYZE:
\t\t\t# 50%の確率で行動不能
\t\t\treturn randf() > 0.5
\t\t_:
\t\t\treturn true

# 攻撃力への影響を取得
func get_attack_modifier() -> float:
\tmatch effect_type:
\t\tEffectType.ATTACK_UP:
\t\t\treturn 1.0 + (float(power) / 100.0)
\t\tEffectType.ATTACK_DOWN:
\t\t\treturn 1.0 - (float(power) / 100.0)
\t\t_:
\t\t\treturn 1.0

# 防御力への影響を取得
func get_defense_modifier() -> float:
\tmatch effect_type:
\t\tEffectType.DEFENSE_UP:
\t\t\treturn 1.0 + (float(power) / 100.0)
\t\tEffectType.DEFENSE_DOWN:
\t\t\treturn 1.0 - (float(power) / 100.0)
\t\t_:
\t\t\treturn 1.0

# 速度への影響を取得
func get_speed_modifier() -> float:
\tmatch effect_type:
\t\tEffectType.SPEED_UP:
\t\t\treturn 1.0 + (float(power) / 100.0)
\t\tEffectType.SPEED_DOWN:
\t\t\treturn 1.0 - (float(power) / 100.0)
\t\t_:
\t\t\treturn 1.0

# 無敵かどうか
func is_invincible() -> bool:
\treturn effect_type == EffectType.INVINCIBLE

# 効果が終了したか
func is_expired() -> bool:
\treturn duration <= 0

# 効果の説明を取得
func get_description() -> String:
\tvar desc = "%s" % effect_name
\tif duration > 0:
\t\tdesc += " (%d turns)" % duration
\treturn desc
'''

        self.save_gdscript(
            "game/scripts/StatusEffect.gd",
            script,
            "Status effect class with various debuffs and buffs"
        )

    def _generate_status_effect_manager_script(self) -> None:
        """StatusEffectManager.gd を生成"""
        script = '''# StatusEffectManager.gd
# 状態異常管理システム

extends Node
class_name StatusEffectManager

# ユニットごとの状態異常を管理
var active_effects: Dictionary = {}  # {unit: [StatusEffect, ...]}

# 状態異常を付与
func add_effect(target: Resource, effect: StatusEffect) -> void:
\tif not active_effects.has(target):
\t\tactive_effects[target] = []
\t
\t# 同じタイプの効果があれば上書き
\tvar existing_index = -1
\tfor i in range(active_effects[target].size()):
\t\tif active_effects[target][i].effect_type == effect.effect_type:
\t\t\texisting_index = i
\t\t\tbreak
\t
\tif existing_index >= 0:
\t\tactive_effects[target][existing_index] = effect
\telse:
\t\tactive_effects[target].append(effect)
\t
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\tprint("%s is affected by %s" % [target_name, effect.effect_name])

# 状態異常を削除
func remove_effect(target: Resource, effect_type: StatusEffect.EffectType) -> void:
\tif not active_effects.has(target):
\t\treturn
\t
\tvar new_effects = []
\tfor effect in active_effects[target]:
\t\tif effect.effect_type != effect_type:
\t\t\tnew_effects.append(effect)
\t
\tactive_effects[target] = new_effects

# 全ての状態異常をクリア
func clear_all_effects(target: Resource) -> void:
\tif active_effects.has(target):
\t\tactive_effects[target].clear()

# ターン開始時の処理
func process_turn_start(target: Resource) -> Array[Dictionary]:
\tvar results: Array[Dictionary] = []
\t
\tif not active_effects.has(target):
\t\treturn results
\t
\tvar remaining_effects = []
\t
\tfor effect in active_effects[target]:
\t\t# 効果を適用
\t\tvar result = effect.apply_turn_effect(target)
\t\tif result["message"] != "":
\t\t\tresults.append(result)
\t\t\tprint(result["message"])
\t\t
\t\t# 期限切れでなければ保持
\t\tif not effect.is_expired():
\t\t\tremaining_effects.append(effect)
\t\telse:
\t\t\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t\t\tprint("%s's %s has worn off" % [target_name, effect.effect_name])
\t
\tactive_effects[target] = remaining_effects
\treturn results

# 行動可能か判定
func can_act(target: Resource) -> bool:
\tif not active_effects.has(target):
\t\treturn true
\t
\tfor effect in active_effects[target]:
\t\tif not effect.can_act():
\t\t\treturn false
\t
\treturn true

# ステータス修正値を取得
func get_stat_modifiers(target: Resource) -> Dictionary:
\tvar modifiers = {
\t\t"attack": 1.0,
\t\t"defense": 1.0,
\t\t"speed": 1.0,
\t\t"invincible": false
\t}
\t
\tif not active_effects.has(target):
\t\treturn modifiers
\t
\tfor effect in active_effects[target]:
\t\tmodifiers["attack"] *= effect.get_attack_modifier()
\t\tmodifiers["defense"] *= effect.get_defense_modifier()
\t\tmodifiers["speed"] *= effect.get_speed_modifier()
\t\t
\t\tif effect.is_invincible():
\t\t\tmodifiers["invincible"] = true
\t
\treturn modifiers

# 状態異常を持っているか
func has_effect(target: Resource, effect_type: StatusEffect.EffectType) -> bool:
\tif not active_effects.has(target):
\t\treturn false
\t
\tfor effect in active_effects[target]:
\t\tif effect.effect_type == effect_type:
\t\t\treturn true
\t
\treturn false

# 状態異常リストを取得
func get_effects(target: Resource) -> Array:
\tif active_effects.has(target):
\t\treturn active_effects[target]
\treturn []

# 状態異常の説明を取得
func get_effects_description(target: Resource) -> String:
\tif not active_effects.has(target) or active_effects[target].size() == 0:
\t\treturn "No effects"
\t
\tvar desc = "Effects: "
\tvar effect_names = []
\tfor effect in active_effects[target]:
\t\teffect_names.append(effect.get_description())
\t
\treturn desc + ", ".join(effect_names)

# プリセット状態異常を作成
static func create_poison(power: int = 5, duration: int = 3) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.POISON, duration, power)

static func create_burn(power: int = 7, duration: int = 2) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.BURN, duration, power)

static func create_stun() -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.STUN, 1, 0)

static func create_paralyze(duration: int = 2) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.PARALYZE, duration, 0)

static func create_attack_up(power: int = 30, duration: int = 3) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.ATTACK_UP, duration, power)

static func create_defense_up(power: int = 30, duration: int = 3) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.DEFENSE_UP, duration, power)

static func create_regeneration(power: int = 10, duration: int = 3) -> StatusEffect:
\treturn StatusEffect.new(StatusEffect.EffectType.REGENERATION, duration, power)

# 全ユニットの状態異常をクリア
func clear_all() -> void:
\tactive_effects.clear()
\tprint("All status effects cleared")
'''

        self.save_gdscript(
            "game/scripts/StatusEffectManager.gd",
            script,
            "Status effect management with turn-based processing and stat modifiers"
        )
