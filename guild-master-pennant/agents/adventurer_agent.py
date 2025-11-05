"""
Adventurer Agent - 冒険者システムの担当エージェント

冒険者の能力値、職業、ステータス管理を担当する。
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class AdventurerAgent(BaseAgent):
    """
    冒険者システムの設計と実装を担当するエージェント

    責務:
    - 5職業の定義（戦士、魔法使い、僧侶、盗賊、弓使い）
    - 能力値システム（HP、攻撃、防御、魔力、速度）
    - 冒険者クラスのGDScript生成
    """

    def __init__(self, blackboard):
        super().__init__(
            name="AdventurerAgent",
            blackboard=blackboard,
            role="冒険者システムの設計と実装"
        )
        self._initialized = False
        self._gdscript_generated = False

    def think(self) -> None:
        """
        冒険者システムの自律的な設計と実装
        """
        # 初期化
        if not self._initialized:
            self._initialize()
            return

        # GDScriptがまだ生成されていない場合
        if not self._gdscript_generated:
            self._generate_gdscript()
            return

        # 新しいメッセージをチェック
        messages = self.get_new_messages()
        for message in messages:
            self._handle_message(message)

    def _initialize(self) -> None:
        """
        初期化処理
        """
        self.logger.info("Initializing Adventurer System...")

        # 職業の定義
        self._define_job_classes()

        # タスクを登録
        self.update_task_status(
            "adventurer_system",
            "in_progress",
            "Defining job classes and stat system"
        )

        self._initialized = True
        self.send_message("all", "Adventurer system initialized", "info")

    def _define_job_classes(self) -> None:
        """
        5つの職業を定義
        """
        job_classes = {
            "Warrior": {
                "base_hp": 100,
                "base_attack": 15,
                "base_defense": 12,
                "base_magic": 3,
                "base_speed": 8,
                "description": "高いHPと攻撃力を持つ前衛職"
            },
            "Mage": {
                "base_hp": 60,
                "base_attack": 5,
                "base_defense": 5,
                "base_magic": 20,
                "base_speed": 10,
                "description": "魔力が高く、魔法攻撃に特化"
            },
            "Priest": {
                "base_hp": 70,
                "base_attack": 7,
                "base_defense": 8,
                "base_magic": 15,
                "base_speed": 9,
                "description": "回復魔法と補助魔法が得意"
            },
            "Thief": {
                "base_hp": 75,
                "base_attack": 12,
                "base_defense": 7,
                "base_magic": 5,
                "base_speed": 18,
                "description": "高速で回避率が高い"
            },
            "Archer": {
                "base_hp": 80,
                "base_attack": 13,
                "base_defense": 8,
                "base_magic": 6,
                "base_speed": 12,
                "description": "後列から安定した火力を提供"
            }
        }

        # Blackboardに保存
        self.blackboard.set_value("job_classes", job_classes)

        self.record_decision(
            decision="Defined 5 job classes with balanced stats",
            rationale="戦士（高HP/攻撃）、魔法使い（魔力特化）、僧侶（回復）、盗賊（速度）、弓使い（バランス）でパーティ構成の幅を確保"
        )

    def _generate_gdscript(self) -> None:
        """
        冒険者システムのGDScriptを生成
        """
        self.logger.info("Generating Adventurer GDScript...")

        job_classes = self.blackboard.get_value("job_classes")

        # Adventurer.gd の生成
        adventurer_script = self._create_adventurer_script(job_classes)
        self.generate_file(
            filepath="game/scripts/Adventurer.gd",
            content=adventurer_script,
            description="冒険者クラス - 能力値、職業、ステータス管理"
        )

        # JobClass.gd の生成
        job_class_script = self._create_job_class_script(job_classes)
        self.generate_file(
            filepath="game/scripts/JobClass.gd",
            content=job_class_script,
            description="職業定義 - 5つの職業と基礎能力値"
        )

        self._gdscript_generated = True
        self.update_task_status(
            "adventurer_system",
            "completed",
            "GDScript files generated successfully"
        )

        self.send_message(
            "all",
            "Adventurer system GDScript generated",
            "info",
            {"files": ["Adventurer.gd", "JobClass.gd"]}
        )

    def _create_adventurer_script(self, job_classes: Dict) -> str:
        """
        Adventurer.gd スクリプトを生成
        """
        return '''# Adventurer.gd
# 冒険者クラス - パーティメンバーの基本クラス

extends Node
class_name Adventurer

# 能力値
var max_hp: int = 100
var current_hp: int = 100
var attack: int = 10
var defense: int = 10
var magic: int = 10
var speed: int = 10

# 職業
var job_class: String = "Warrior"

# ステータス
var level: int = 1
var experience: int = 0
var is_alive: bool = true

# 位置情報
var formation_position: int = 0  # 0-2: 前列, 3: 後列

# スキル
var skills: Array = []
var passive_skills: Array = []

# 装備
var weapon: Dictionary = {}
var armor: Dictionary = {}

# 名前
var adventurer_name: String = ""


func _init(p_name: String = "冒険者", p_job_class: String = "Warrior"):
    """初期化"""
    adventurer_name = p_name
    job_class = p_job_class
    _apply_job_base_stats()


func _apply_job_base_stats() -> void:
    """職業に応じた基礎能力値を適用"""
    match job_class:
        "Warrior":
            max_hp = 100
            attack = 15
            defense = 12
            magic = 3
            speed = 8
        "Mage":
            max_hp = 60
            attack = 5
            defense = 5
            magic = 20
            speed = 10
        "Priest":
            max_hp = 70
            attack = 7
            defense = 8
            magic = 15
            speed = 9
        "Thief":
            max_hp = 75
            attack = 12
            defense = 7
            magic = 5
            speed = 18
        "Archer":
            max_hp = 80
            attack = 13
            defense = 8
            magic = 6
            speed = 12

    current_hp = max_hp


func take_damage(damage: int) -> int:
    """ダメージを受ける"""
    var actual_damage = max(1, damage - defense)
    current_hp -= actual_damage

    if current_hp <= 0:
        current_hp = 0
        is_alive = false

    return actual_damage


func heal(amount: int) -> int:
    """回復する"""
    if not is_alive:
        return 0

    var old_hp = current_hp
    current_hp = min(max_hp, current_hp + amount)
    return current_hp - old_hp


func is_in_front_row() -> bool:
    """前列にいるか"""
    return formation_position < 3


func get_position_attack_modifier() -> float:
    """位置による攻撃力修正"""
    return 1.1 if is_in_front_row() else 1.0


func get_position_defense_modifier() -> float:
    """位置による防御力修正"""
    return 1.0 if is_in_front_row() else 1.1


func get_hit_rate() -> float:
    """被弾率"""
    if is_in_front_row():
        return 0.6 / 3.0  # 前列3人で60%を分担
    else:
        return 0.1  # 後列は10%


func get_effective_attack() -> int:
    """実効攻撃力（位置修正込み）"""
    return int(attack * get_position_attack_modifier())


func get_effective_defense() -> int:
    """実効防御力（位置修正込み）"""
    return int(defense * get_position_defense_modifier())


func add_skill(skill: Dictionary) -> void:
    """スキルを追加"""
    skills.append(skill)


func add_passive_skill(skill: Dictionary) -> void:
    """パッシブスキルを追加"""
    passive_skills.append(skill)


func get_status() -> Dictionary:
    """ステータスを取得"""
    return {
        "name": adventurer_name,
        "job_class": job_class,
        "level": level,
        "hp": "%d/%d" % [current_hp, max_hp],
        "attack": get_effective_attack(),
        "defense": get_effective_defense(),
        "magic": magic,
        "speed": speed,
        "is_alive": is_alive,
        "position": "前列" if is_in_front_row() else "後列"
    }


func to_dict() -> Dictionary:
    """辞書形式にシリアライズ"""
    return {
        "name": adventurer_name,
        "job_class": job_class,
        "level": level,
        "max_hp": max_hp,
        "current_hp": current_hp,
        "attack": attack,
        "defense": defense,
        "magic": magic,
        "speed": speed,
        "formation_position": formation_position,
        "is_alive": is_alive,
        "skills": skills,
        "passive_skills": passive_skills
    }
'''

    def _create_job_class_script(self, job_classes: Dict) -> str:
        """
        JobClass.gd スクリプトを生成
        """
        # 職業データをGDScriptの定数として展開
        job_data_str = ""
        for job_name, stats in job_classes.items():
            job_data_str += f'''
    "{job_name}": {{
        "base_hp": {stats["base_hp"]},
        "base_attack": {stats["base_attack"]},
        "base_defense": {stats["base_defense"]},
        "base_magic": {stats["base_magic"]},
        "base_speed": {stats["base_speed"]},
        "description": "{stats["description"]}"
    }},'''

        return f'''# JobClass.gd
# 職業定義 - 5つの職業と基礎能力値

extends Node
class_name JobClass

# 職業一覧
enum Job {{
    WARRIOR,
    MAGE,
    PRIEST,
    THIEF,
    ARCHER
}}

# 職業データ
const JOB_DATA: Dictionary = {{{job_data_str}
}}


static func get_job_name(job: Job) -> String:
    """職業名を取得"""
    match job:
        Job.WARRIOR:
            return "Warrior"
        Job.MAGE:
            return "Mage"
        Job.PRIEST:
            return "Priest"
        Job.THIEF:
            return "Thief"
        Job.ARCHER:
            return "Archer"
    return "Unknown"


static func get_job_data(job_name: String) -> Dictionary:
    """職業データを取得"""
    return JOB_DATA.get(job_name, {{}})


static func get_all_jobs() -> Array:
    """すべての職業名を取得"""
    return JOB_DATA.keys()


static func create_adventurer(name: String, job_name: String) -> Adventurer:
    """冒険者を作成"""
    return Adventurer.new(name, job_name)
'''

    def _handle_message(self, message: Dict) -> None:
        """
        メッセージを処理

        Args:
            message: 受信したメッセージ
        """
        msg_type = message.get("type")
        sender = message.get("sender")
        content = message.get("content")

        if msg_type == "request":
            # リクエストに応答
            if "adventurer" in content.lower():
                self.send_message(
                    sender,
                    "Adventurer system is ready. 5 job classes defined.",
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
            "gdscript_generated": self._gdscript_generated,
            "job_classes": 5
        }
