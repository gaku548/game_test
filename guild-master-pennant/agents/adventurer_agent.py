"""
AdventurerAgent - 冒険者システムの設計と実装を担当

Adventurer.gd と JobClass.gd を生成する
"""

from .base_agent import BaseAgent


class AdventurerAgent(BaseAgent):
    """
    冒険者システムを担当するエージェント

    責務:
    - 冒険者クラスの設計
    - 職業システムの設計
    - 能力値システムの設計
    - 位置修正の実装
    """

    def __init__(self, blackboard):
        super().__init__("AdventurerAgent", blackboard, "Adventurer System Designer")

    def think(self) -> None:
        """冒険者システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_job_class_script()
        self._generate_adventurer_script()

        # 完了を通知
        self.broadcast("冒険者システムのGDScriptを生成しました")
        self.update_task("adventurer_system", "completed", "Adventurer.gd and JobClass.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing AdventurerAgent...")

        self.record_decision(
            "冒険者システムの設計",
            "5つの職業（戦士、魔法使い、僧侶、盗賊、弓使い）を実装。"
            "位置による能力修正と被弾率を考慮した設計。"
        )

        self.update_task("adventurer_system", "in_progress", "Designing adventurer classes")
        self._initialized = True

    def _generate_job_class_script(self) -> None:
        """JobClass.gd を生成"""
        script = '''# JobClass.gd
# 冒険者の職業クラス定義

extends Resource
class_name JobClass

enum Type {
\tWARRIOR,   # 戦士 - 高HP/攻撃
\tMAGE,      # 魔法使い - 魔力特化
\tPRIEST,    # 僧侶 - 回復
\tTHIEF,     # 盗賊 - 速度
\tARCHER     # 弓使い - バランス
}

# 職業名
static func get_job_name(job_type: Type) -> String:
\tmatch job_type:
\t\tType.WARRIOR:
\t\t\treturn "Warrior"
\t\tType.MAGE:
\t\t\treturn "Mage"
\t\tType.PRIEST:
\t\t\treturn "Priest"
\t\tType.THIEF:
\t\t\treturn "Thief"
\t\tType.ARCHER:
\t\t\treturn "Archer"
\t\t_:
\t\t\treturn "Unknown"

# 職業別基礎ステータス
static func get_base_stats(job_type: Type) -> Dictionary:
\tmatch job_type:
\t\tType.WARRIOR:
\t\t\treturn {
\t\t\t\t"max_hp": 100,
\t\t\t\t"attack": 15,
\t\t\t\t"defense": 12,
\t\t\t\t"magic": 3,
\t\t\t\t"speed": 8
\t\t\t}
\t\tType.MAGE:
\t\t\treturn {
\t\t\t\t"max_hp": 60,
\t\t\t\t"attack": 5,
\t\t\t\t"defense": 5,
\t\t\t\t"magic": 20,
\t\t\t\t"speed": 10
\t\t\t}
\t\tType.PRIEST:
\t\t\treturn {
\t\t\t\t"max_hp": 70,
\t\t\t\t"attack": 7,
\t\t\t\t"defense": 8,
\t\t\t\t"magic": 15,
\t\t\t\t"speed": 9
\t\t\t}
\t\tType.THIEF:
\t\t\treturn {
\t\t\t\t"max_hp": 75,
\t\t\t\t"attack": 12,
\t\t\t\t"defense": 7,
\t\t\t\t"magic": 5,
\t\t\t\t"speed": 18
\t\t\t}
\t\tType.ARCHER:
\t\t\treturn {
\t\t\t\t"max_hp": 80,
\t\t\t\t"attack": 13,
\t\t\t\t"defense": 8,
\t\t\t\t"magic": 6,
\t\t\t\t"speed": 12
\t\t\t}
\t\t_:
\t\t\treturn {
\t\t\t\t"max_hp": 50,
\t\t\t\t"attack": 10,
\t\t\t\t"defense": 10,
\t\t\t\t"magic": 10,
\t\t\t\t"speed": 10
\t\t\t}

# 職業の特徴説明
static func get_description(job_type: Type) -> String:
\tmatch job_type:
\t\tType.WARRIOR:
\t\t\treturn "高いHPと攻撃力を持つ前衛職"
\t\tType.MAGE:
\t\t\treturn "強力な魔法攻撃を操る魔術師"
\t\tType.PRIEST:
\t\t\treturn "味方を回復できるサポート職"
\t\tType.THIEF:
\t\t\treturn "素早い動きで先制攻撃を狙う"
\t\tType.ARCHER:
\t\t\treturn "バランスの取れた遠距離攻撃職"
\t\t_:
\t\t\treturn ""
'''

        self.save_gdscript(
            "game/scripts/JobClass.gd",
            script,
            "Job class definitions with base stats for 5 job types"
        )

    def _generate_adventurer_script(self) -> None:
        """Adventurer.gd を生成"""
        script = '''# Adventurer.gd
# 冒険者クラス - パーティメンバーの基本単位

extends Resource
class_name Adventurer

# 基本情報
var adventurer_name: String = ""
var job_class: JobClass.Type = JobClass.Type.WARRIOR

# ステータス
var max_hp: int = 100
var current_hp: int = 100
var attack: int = 10
var defense: int = 10
var magic: int = 10
var speed: int = 10

# 隊列位置 (0-5: 0-2が前列、3-5が後列)
var formation_position: int = 0

# 状態
var is_alive: bool = true

# 装備とスキル
var equipped_skills: Array[Resource] = []
var status_effects: Array = []

func _init(name: String = "Adventurer", job: JobClass.Type = JobClass.Type.WARRIOR):
\tadventurer_name = name
\tjob_class = job
\t_apply_job_stats()

# 職業別ステータスを適用
func _apply_job_stats() -> void:
\tvar stats = JobClass.get_base_stats(job_class)
\tmax_hp = stats["max_hp"]
\tcurrent_hp = max_hp
\tattack = stats["attack"]
\tdefense = stats["defense"]
\tmagic = stats["magic"]
\tspeed = stats["speed"]

# 前列にいるか
func is_in_front_row() -> bool:
\treturn formation_position < 3

# 実効攻撃力（位置修正込み）
func get_effective_attack() -> int:
\tvar modifier = 1.1 if is_in_front_row() else 1.0
\treturn int(attack * modifier)

# 実効防御力（位置修正込み）
func get_effective_defense() -> int:
\tvar modifier = 1.0 if is_in_front_row() else 1.1
\treturn int(defense * modifier)

# 被弾率
func get_hit_rate() -> float:
\tif is_in_front_row():
\t\treturn 0.6 / 3.0  # 前列3人で60%を分担
\telse:
\t\treturn 0.1  # 後列は10%

# ダメージを受ける
func take_damage(damage: int) -> int:
\tvar actual_damage = max(1, damage - get_effective_defense())
\tcurrent_hp -= actual_damage
\t
\tif current_hp <= 0:
\t\tcurrent_hp = 0
\t\tis_alive = false
\t
\treturn actual_damage

# 回復
func heal(amount: int) -> int:
\tif not is_alive:
\t\treturn 0
\t
\tvar old_hp = current_hp
\tcurrent_hp = min(max_hp, current_hp + amount)
\treturn current_hp - old_hp

# HP割合を取得
func get_hp_percentage() -> float:
\tif max_hp == 0:
\t\treturn 0.0
\treturn float(current_hp) / float(max_hp)

# 蘇生
func revive(hp_amount: int = -1) -> void:
\tif hp_amount < 0:
\t\thp_amount = max_hp / 2
\tcurrent_hp = min(hp_amount, max_hp)
\tis_alive = true

# ステータス表示用
func get_status_text() -> String:
\tvar status = "Name: %s (%s)\\n" % [adventurer_name, JobClass.get_job_name(job_class)]
\tstatus += "HP: %d/%d\\n" % [current_hp, max_hp]
\tstatus += "ATK: %d  DEF: %d\\n" % [attack, defense]
\tstatus += "MAG: %d  SPD: %d\\n" % [magic, speed]
\tstatus += "Position: %s" % ("Front" if is_in_front_row() else "Back")
\treturn status
'''

        self.save_gdscript(
            "game/scripts/Adventurer.gd",
            script,
            "Adventurer class with stats, position modifiers, and combat methods"
        )
