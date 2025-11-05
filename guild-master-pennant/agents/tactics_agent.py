"""
TacticsAgent - 戦術システムの設計と実装を担当

TacticsSystem.gd と TacticsCondition.gd を生成する
"""

from .base_agent import BaseAgent


class TacticsAgent(BaseAgent):
    """
    戦術システムを担当するエージェント

    責務:
    - 条件分岐型戦術システムの設計
    - 戦術条件の実装
    - 優先度管理システム
    """

    def __init__(self, blackboard):
        super().__init__("TacticsAgent", blackboard, "Tactics System Designer")

    def think(self) -> None:
        """戦術システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_tactics_condition_script()
        self._generate_tactics_system_script()

        # 完了を通知
        self.broadcast("戦術システムのGDScriptを生成しました")
        self.update_task("tactics_system", "completed", "TacticsSystem.gd and TacticsCondition.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing TacticsAgent...")

        self.record_decision(
            "戦術システムの設計",
            "ユニコーンオーバーロード風の条件分岐型自動戦闘。"
            "条件（HP、敵タイプ、味方状態）に基づいて行動を決定。"
        )

        self.update_task("tactics_system", "in_progress", "Designing conditional tactics")
        self._initialized = True

    def _generate_tactics_condition_script(self) -> None:
        """TacticsCondition.gd を生成"""
        script = '''# TacticsCondition.gd
# 戦術条件 - 戦術を発動する条件を判定

extends Resource
class_name TacticsCondition

enum ConditionType {
\tHP_BELOW,          # HPが指定値以下
\tHP_ABOVE,          # HP が指定値以上
\tENEMY_TYPE,        # 敵のタイプ
\tALLY_HP_LOW,       # 味方のHPが低い
\tALLY_COUNT,        # 味方の生存数
\tENEMY_COUNT,       # 敵の数
\tALWAYS            # 常に真
}

var condition_type: ConditionType = ConditionType.ALWAYS
var threshold: float = 0.0
var target_type: String = ""

func _init(type: ConditionType = ConditionType.ALWAYS, value: float = 0.0):
\tcondition_type = type
\tthreshold = value

# 条件を評価
func evaluate(actor: Adventurer, allies: Array[Adventurer], enemies: Array) -> bool:
\tmatch condition_type:
\t\tConditionType.HP_BELOW:
\t\t\treturn actor.get_hp_percentage() < threshold
\t\t
\t\tConditionType.HP_ABOVE:
\t\t\treturn actor.get_hp_percentage() > threshold
\t\t
\t\tConditionType.ENEMY_TYPE:
\t\t\t# 特定タイプの敵がいるか
\t\t\tfor enemy in enemies:
\t\t\t\tif enemy.is_alive and "type" in enemy:
\t\t\t\t\tif enemy.type == target_type:
\t\t\t\t\t\treturn true
\t\t\treturn false
\t\t
\t\tConditionType.ALLY_HP_LOW:
\t\t\t# HP が threshold 以下の味方がいる
\t\t\tfor ally in allies:
\t\t\t\tif ally.is_alive and ally.get_hp_percentage() < threshold:
\t\t\t\t\treturn true
\t\t\treturn false
\t\t
\t\tConditionType.ALLY_COUNT:
\t\t\tvar alive_count = allies.filter(func(a): return a.is_alive).size()
\t\t\treturn alive_count <= int(threshold)
\t\t
\t\tConditionType.ENEMY_COUNT:
\t\t\tvar alive_count = enemies.filter(func(e): return e.is_alive).size()
\t\t\treturn alive_count >= int(threshold)
\t\t
\t\tConditionType.ALWAYS:
\t\t\treturn true
\t
\treturn false

# 条件の説明を取得
func get_description() -> String:
\tmatch condition_type:
\t\tConditionType.HP_BELOW:
\t\t\treturn "HP < %.0f%%" % (threshold * 100)
\t\tConditionType.HP_ABOVE:
\t\t\treturn "HP > %.0f%%" % (threshold * 100)
\t\tConditionType.ENEMY_TYPE:
\t\t\treturn "Enemy type: %s" % target_type
\t\tConditionType.ALLY_HP_LOW:
\t\t\treturn "Ally HP < %.0f%%" % (threshold * 100)
\t\tConditionType.ALLY_COUNT:
\t\t\treturn "Allies <= %d" % int(threshold)
\t\tConditionType.ENEMY_COUNT:
\t\t\treturn "Enemies >= %d" % int(threshold)
\t\tConditionType.ALWAYS:
\t\t\treturn "Always"
\t\t_:
\t\t\treturn "Unknown"
'''

        self.save_gdscript(
            "game/scripts/TacticsCondition.gd",
            script,
            "Tactics condition evaluation for conditional combat AI"
        )

    def _generate_tactics_system_script(self) -> None:
        """TacticsSystem.gd を生成"""
        script = '''# TacticsSystem.gd
# 戦術システム - 条件に基づいて行動を決定

extends Resource
class_name TacticsSystem

# 戦術ルール
class TacticsRule:
\tvar priority: int = 0
\tvar condition: TacticsCondition = null
\tvar action_type: CombatAction.ActionType = CombatAction.ActionType.ATTACK
\tvar skill: Resource = null
\tvar description: String = ""
\t
\tfunc _init(prio: int, cond: TacticsCondition, action: CombatAction.ActionType):
\t\tpriority = prio
\t\tcondition = cond
\t\taction_type = action

var tactics_rules: Array[TacticsRule] = []

# デフォルト戦術を設定（職業別）
func setup_default_tactics(job_type: JobClass.Type) -> void:
\ttactics_rules.clear()
\t
\tmatch job_type:
\t\tJobClass.Type.WARRIOR:
\t\t\t_setup_warrior_tactics()
\t\tJobClass.Type.MAGE:
\t\t\t_setup_mage_tactics()
\t\tJobClass.Type.PRIEST:
\t\t\t_setup_priest_tactics()
\t\tJobClass.Type.THIEF:
\t\t\t_setup_thief_tactics()
\t\tJobClass.Type.ARCHER:
\t\t\t_setup_archer_tactics()

# 戦士のデフォルト戦術
func _setup_warrior_tactics() -> void:
\t# HP低下時は防御
\tvar rule1 = TacticsRule.new(
\t\t1,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.HP_BELOW, 0.3),
\t\tCombatAction.ActionType.DEFEND
\t)
\trule1.description = "HP < 30%: Defend"
\ttactics_rules.append(rule1)
\t
\t# それ以外は攻撃
\tvar rule2 = TacticsRule.new(
\t\t10,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALWAYS),
\t\tCombatAction.ActionType.ATTACK
\t)
\trule2.description = "Always: Attack"
\ttactics_rules.append(rule2)

# 魔法使いのデフォルト戦術
func _setup_mage_tactics() -> void:
\t# 敵が多い時は範囲攻撃（将来実装）
\tvar rule1 = TacticsRule.new(
\t\t1,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ENEMY_COUNT, 3),
\t\tCombatAction.ActionType.SKILL
\t)
\trule1.description = "Enemies >= 3: Area Magic"
\ttactics_rules.append(rule1)
\t
\t# 基本は魔法攻撃
\tvar rule2 = TacticsRule.new(
\t\t10,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALWAYS),
\t\tCombatAction.ActionType.ATTACK
\t)
\trule2.description = "Always: Magic Attack"
\ttactics_rules.append(rule2)

# 僧侶のデフォルト戦術
func _setup_priest_tactics() -> void:
\t# 味方のHPが低い時は回復
\tvar rule1 = TacticsRule.new(
\t\t1,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALLY_HP_LOW, 0.5),
\t\tCombatAction.ActionType.SKILL
\t)
\trule1.description = "Ally HP < 50%: Heal"
\ttactics_rules.append(rule1)
\t
\t# 自分のHPが低い時も回復
\tvar rule2 = TacticsRule.new(
\t\t2,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.HP_BELOW, 0.4),
\t\tCombatAction.ActionType.SKILL
\t)
\trule2.description = "HP < 40%: Self Heal"
\ttactics_rules.append(rule2)
\t
\t# それ以外は攻撃
\tvar rule3 = TacticsRule.new(
\t\t10,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALWAYS),
\t\tCombatAction.ActionType.ATTACK
\t)
\trule3.description = "Always: Attack"
\ttactics_rules.append(rule3)

# 盗賊のデフォルト戦術
func _setup_thief_tactics() -> void:
\t# 常に攻撃（速度を活かす）
\tvar rule1 = TacticsRule.new(
\t\t10,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALWAYS),
\t\tCombatAction.ActionType.ATTACK
\t)
\trule1.description = "Always: Quick Attack"
\ttactics_rules.append(rule1)

# 弓使いのデフォルト戦術
func _setup_archer_tactics() -> void:
\t# 常に攻撃
\tvar rule1 = TacticsRule.new(
\t\t10,
\t\tTacticsCondition.new(TacticsCondition.ConditionType.ALWAYS),
\t\tCombatAction.ActionType.ATTACK
\t)
\trule1.description = "Always: Ranged Attack"
\ttactics_rules.append(rule1)

# 行動を決定
func decide_action(actor: Adventurer, allies: Array[Adventurer], enemies: Array) -> CombatAction:
\t# 優先度順にソート
\ttactics_rules.sort_custom(func(a, b): return a.priority < b.priority)
\t
\t# 最初にマッチした戦術を使用
\tfor rule in tactics_rules:
\t\tif rule.condition.evaluate(actor, allies, enemies):
\t\t\tvar action = CombatAction.new(rule.action_type)
\t\t\taction.actor = actor
\t\t\taction.skill = rule.skill
\t\t\treturn action
\t
\t# デフォルトは攻撃
\tvar default_action = CombatAction.new(CombatAction.ActionType.ATTACK)
\tdefault_action.actor = actor
\treturn default_action

# カスタム戦術ルールを追加
func add_rule(priority: int, condition: TacticsCondition, action_type: CombatAction.ActionType, description: String = "") -> void:
\tvar rule = TacticsRule.new(priority, condition, action_type)
\trule.description = description
\ttactics_rules.append(rule)

# 戦術ルールをクリア
func clear_rules() -> void:
\ttactics_rules.clear()

# 戦術一覧を取得
func get_tactics_summary() -> String:
\tvar summary = "Tactics Rules:\\n"
\tfor rule in tactics_rules:
\t\tsummary += "  [Priority %d] %s\\n" % [rule.priority, rule.description]
\treturn summary
'''

        self.save_gdscript(
            "game/scripts/TacticsSystem.gd",
            script,
            "Conditional tactics system with priority-based rule evaluation"
        )
