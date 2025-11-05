"""
SkillAgent - スキルシステムの設計と実装を担当

SkillSystem.gd と Skill.gd を生成する
"""

from .base_agent import BaseAgent


class SkillAgent(BaseAgent):
    """
    スキルシステムを担当するエージェント

    責務:
    - スキルデータ構造の設計
    - 攻撃・回復・補助スキルの実装
    - パッシブスキルシステム
    """

    def __init__(self, blackboard):
        super().__init__("SkillAgent", blackboard, "Skill System Designer")

    def think(self) -> None:
        """スキルシステムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_skill_script()
        self._generate_skill_system_script()

        # 完了を通知
        self.broadcast("スキルシステムのGDScriptを生成しました")
        self.update_task("skill_system", "completed", "SkillSystem.gd and Skill.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing SkillAgent...")

        self.record_decision(
            "スキルシステムの設計",
            "パワプロ特能風の倍率設定。攻撃、回復、補助、パッシブの4種類を実装。"
        )

        self.update_task("skill_system", "in_progress", "Designing skill types and effects")
        self._initialized = True

    def _generate_skill_script(self) -> None:
        """Skill.gd を生成"""
        script = '''# Skill.gd
# スキルデータ定義

extends Resource
class_name Skill

enum SkillType {
\tATTACK,     # 攻撃スキル
\tHEAL,       # 回復スキル
\tBUFF,       # 補助スキル（強化）
\tDEBUFF,     # 補助スキル（弱体化）
\tPASSIVE     # パッシブスキル
}

enum TargetType {
\tSINGLE_ENEMY,
\tALL_ENEMIES,
\tSINGLE_ALLY,
\tALL_ALLIES,
\tSELF
}

var skill_name: String = ""
var skill_type: SkillType = SkillType.ATTACK
var target_type: TargetType = TargetType.SINGLE_ENEMY
var power_multiplier: float = 1.0  # 威力倍率
var cost_mp: int = 0  # MP消費（将来実装）
var description: String = ""

func _init(name: String = "Skill", type: SkillType = SkillType.ATTACK):
\tskill_name = name
\tskill_type = type

# スキルを実行
func execute(actor: Adventurer, target: Resource) -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"damage": 0,
\t\t"healing": 0,
\t\t"message": ""
\t}
\t
\tmatch skill_type:
\t\tSkillType.ATTACK:
\t\t\tresult = _execute_attack(actor, target)
\t\tSkillType.HEAL:
\t\t\tresult = _execute_heal(actor, target)
\t\tSkillType.BUFF:
\t\t\tresult = _execute_buff(actor, target)
\t\tSkillType.DEBUFF:
\t\t\tresult = _execute_debuff(actor, target)
\t\tSkillType.PASSIVE:
\t\t\tresult["message"] = "Passive skills are always active"
\t
\treturn result

# 攻撃スキル実行
func _execute_attack(actor: Adventurer, target: Resource) -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"damage": 0,
\t\t"message": ""
\t}
\t
\tif target == null or not target.is_alive:
\t\tresult["message"] = "Invalid target"
\t\treturn result
\t
\t# ダメージ計算（通常攻撃の倍率版）
\tvar base_damage = CombatAction.calculate_damage(actor, target)
\tvar skill_damage = int(base_damage * power_multiplier)
\tvar actual_damage = target.take_damage(skill_damage)
\t
\tresult["success"] = true
\tresult["damage"] = actual_damage
\t
\tvar actor_name = actor.adventurer_name if "adventurer_name" in actor else "Actor"
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tresult["message"] = "%s uses %s on %s for %d damage!" % [actor_name, skill_name, target_name, actual_damage]
\t
\tif not target.is_alive:
\t\tresult["message"] += " %s is defeated!" % target_name
\t
\treturn result

# 回復スキル実行
func _execute_heal(actor: Adventurer, target: Resource) -> Dictionary:
\tvar result = {
\t\t"success": false,
\t\t"healing": 0,
\t\t"message": ""
\t}
\t
\tif target == null or not target.is_alive:
\t\tresult["message"] = "Invalid target"
\t\treturn result
\t
\t# 回復量計算（魔力ベース）
\tvar heal_amount = int(actor.magic * power_multiplier)
\tvar actual_healing = target.heal(heal_amount)
\t
\tresult["success"] = true
\tresult["healing"] = actual_healing
\t
\tvar actor_name = actor.adventurer_name if "adventurer_name" in actor else "Actor"
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tresult["message"] = "%s uses %s on %s, healing %d HP!" % [actor_name, skill_name, target_name, actual_healing]
\t
\treturn result

# バフスキル実行
func _execute_buff(actor: Adventurer, target: Resource) -> Dictionary:
\tvar result = {
\t\t"success": true,
\t\t"message": ""
\t}
\t
\tif target == null or not target.is_alive:
\t\tresult["success"] = false
\t\tresult["message"] = "Invalid target"
\t\treturn result
\t
\tvar actor_name = actor.adventurer_name if "adventurer_name" in actor else "Actor"
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tresult["message"] = "%s uses %s on %s!" % [actor_name, skill_name, target_name]
\t
\t# TODO: バフ効果の実装
\t
\treturn result

# デバフスキル実行
func _execute_debuff(actor: Adventurer, target: Resource) -> Dictionary:
\tvar result = {
\t\t"success": true,
\t\t"message": ""
\t}
\t
\tif target == null or not target.is_alive:
\t\tresult["success"] = false
\t\tresult["message"] = "Invalid target"
\t\treturn result
\t
\tvar actor_name = actor.adventurer_name if "adventurer_name" in actor else "Actor"
\tvar target_name = target.adventurer_name if "adventurer_name" in target else target.name
\t
\tresult["message"] = "%s uses %s on %s!" % [actor_name, skill_name, target_name]
\t
\t# TODO: デバフ効果の実装
\t
\treturn result

# スキル情報を取得
func get_info() -> String:
\tvar info = "【%s】\\n" % skill_name
\tinfo += "%s\\n" % description
\tinfo += "Type: %s\\n" % _get_type_name()
\tinfo += "Power: x%.1f\\n" % power_multiplier
\treturn info

func _get_type_name() -> String:
\tmatch skill_type:
\t\tSkillType.ATTACK:
\t\t\treturn "Attack"
\t\tSkillType.HEAL:
\t\t\treturn "Heal"
\t\tSkillType.BUFF:
\t\t\treturn "Buff"
\t\tSkillType.DEBUFF:
\t\t\treturn "Debuff"
\t\tSkillType.PASSIVE:
\t\t\treturn "Passive"
\t\t_:
\t\t\treturn "Unknown"
'''

        self.save_gdscript(
            "game/scripts/Skill.gd",
            script,
            "Skill data with attack, heal, buff, debuff, and passive types"
        )

    def _generate_skill_system_script(self) -> None:
        """SkillSystem.gd を生成"""
        script = '''# SkillSystem.gd
# スキルシステム - スキルの管理と実行

extends Node
class_name SkillSystem

# プリセットスキルのデータベース
var skill_database: Dictionary = {}

func _ready():
\t_initialize_skills()

# スキルデータベースを初期化
func _initialize_skills() -> void:
\t# 攻撃スキル
\tvar strong_attack = Skill.new("Strong Attack", Skill.SkillType.ATTACK)
\tstrong_attack.power_multiplier = 1.5
\tstrong_attack.target_type = Skill.TargetType.SINGLE_ENEMY
\tstrong_attack.description = "強力な一撃"
\tskill_database["strong_attack"] = strong_attack
\t
\tvar fire_magic = Skill.new("Fire", Skill.SkillType.ATTACK)
\tfire_magic.power_multiplier = 2.0
\tfire_magic.target_type = Skill.TargetType.SINGLE_ENEMY
\tfire_magic.description = "炎魔法"
\tskill_database["fire"] = fire_magic
\t
\tvar critical_strike = Skill.new("Critical Strike", Skill.SkillType.ATTACK)
\tcritical_strike.power_multiplier = 2.5
\tcritical_strike.target_type = Skill.TargetType.SINGLE_ENEMY
\tcritical_strike.description = "必殺の一撃"
\tskill_database["critical_strike"] = critical_strike
\t
\t# 回復スキル
\tvar heal = Skill.new("Heal", Skill.SkillType.HEAL)
\theal.power_multiplier = 2.0
\theal.target_type = Skill.TargetType.SINGLE_ALLY
\theal.description = "単体回復"
\tskill_database["heal"] = heal
\t
\tvar mass_heal = Skill.new("Mass Heal", Skill.SkillType.HEAL)
\tmass_heal.power_multiplier = 1.5
\tmass_heal.target_type = Skill.TargetType.ALL_ALLIES
\tmass_heal.description = "全体回復"
\tskill_database["mass_heal"] = mass_heal
\t
\t# 補助スキル
\tvar power_up = Skill.new("Power Up", Skill.SkillType.BUFF)
\tpower_up.power_multiplier = 1.3
\tpower_up.target_type = Skill.TargetType.SINGLE_ALLY
\tpower_up.description = "攻撃力上昇"
\tskill_database["power_up"] = power_up
\t
\tvar defense_up = Skill.new("Defense Up", Skill.SkillType.BUFF)
\tdefense_up.power_multiplier = 1.3
\tdefense_up.target_type = Skill.TargetType.SINGLE_ALLY
\tdefense_up.description = "防御力上昇"
\tskill_database["defense_up"] = defense_up
\t
\t# パッシブスキル
\tvar counter = Skill.new("Counter", Skill.SkillType.PASSIVE)
\tcounter.description = "被ダメージ時に反撃"
\tskill_database["counter"] = counter
\t
\tvar guts = Skill.new("Guts", Skill.SkillType.PASSIVE)
\tguts.description = "致死ダメージでHP1で耐える"
\tskill_database["guts"] = guts
\t
\tprint("Skill database initialized with %d skills" % skill_database.size())

# スキルを取得
func get_skill(skill_id: String) -> Skill:
\tif skill_database.has(skill_id):
\t\treturn skill_database[skill_id]
\treturn null

# 職業別のデフォルトスキルセットを取得
func get_default_skills_for_job(job_type: JobClass.Type) -> Array[Skill]:
\tvar skills: Array[Skill] = []
\t
\tmatch job_type:
\t\tJobClass.Type.WARRIOR:
\t\t\tskills.append(get_skill("strong_attack"))
\t\t\tskills.append(get_skill("critical_strike"))
\t\t
\t\tJobClass.Type.MAGE:
\t\t\tskills.append(get_skill("fire"))
\t\t
\t\tJobClass.Type.PRIEST:
\t\t\tskills.append(get_skill("heal"))
\t\t\tskills.append(get_skill("mass_heal"))
\t\t
\t\tJobClass.Type.THIEF:
\t\t\tskills.append(get_skill("critical_strike"))
\t\t
\t\tJobClass.Type.ARCHER:
\t\t\tskills.append(get_skill("strong_attack"))
\t
\treturn skills

# カスタムスキルを作成
func create_custom_skill(skill_name: String, skill_type: Skill.SkillType, power: float, description: String = "") -> Skill:
\tvar skill = Skill.new(skill_name, skill_type)
\tskill.power_multiplier = power
\tskill.description = description
\treturn skill

# スキル一覧を表示
func list_all_skills() -> String:
\tvar list = "=== Skill Database ===\\n"
\tfor skill_id in skill_database:
\t\tvar skill = skill_database[skill_id]
\t\tlist += "- %s (x%.1f): %s\\n" % [skill.skill_name, skill.power_multiplier, skill.description]
\treturn list

# 職業別推奨スキルを表示
func show_recommended_skills(job_type: JobClass.Type) -> String:
\tvar job_name = JobClass.get_job_name(job_type)
\tvar skills = get_default_skills_for_job(job_type)
\t
\tvar text = "Recommended skills for %s:\\n" % job_name
\tfor skill in skills:
\t\ttext += "  - %s\\n" % skill.skill_name
\t
\treturn text
'''

        self.save_gdscript(
            "game/scripts/SkillSystem.gd",
            script,
            "Skill management system with preset skills and job-specific defaults"
        )
