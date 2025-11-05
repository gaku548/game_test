"""
Skill Agent - スキルシステムの担当エージェント

パワプロ特能風のスキルシステムを実装する。
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class SkillAgent(BaseAgent):
    """
    スキルシステムの設計と実装を担当するエージェント

    責務:
    - パワプロ特能風スキル定義
    - スキル倍率設定
    - スキル効果の実装
    """

    def __init__(self, blackboard):
        super().__init__(
            name="SkillAgent",
            blackboard=blackboard,
            role="スキルシステムの設計と実装"
        )
        self._initialized = False
        self._gdscript_generated = False

    def think(self) -> None:
        """
        スキルシステムの自律的な設計と実装
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
        self.logger.info("Initializing Skill System...")

        self._define_skills()

        self.update_task_status(
            "skill_system",
            "in_progress",
            "Defining power-pro style skills"
        )

        self.record_decision(
            decision="Implement multiplier-based skills like Pawapuro special abilities",
            rationale="攻撃、回復、補助スキルに倍率を設定して柔軟なバランス調整を可能に"
        )

        self._initialized = True
        self.send_message("all", "Skill system initialized", "info")

    def _define_skills(self) -> None:
        """
        スキルを定義
        """
        skills = {
            # 攻撃スキル
            "強撃": {
                "type": "attack",
                "multiplier": 1.5,
                "target": "single",
                "description": "単体に1.5倍の物理ダメージ"
            },
            "ファイア": {
                "type": "magic_attack",
                "multiplier": 1.8,
                "target": "single",
                "description": "単体に1.8倍の魔法ダメージ"
            },
            "乱れ撃ち": {
                "type": "attack",
                "multiplier": 0.8,
                "target": "all",
                "description": "全体に0.8倍の物理ダメージ"
            },
            "必殺剣": {
                "type": "attack",
                "multiplier": 2.5,
                "target": "single",
                "description": "単体に2.5倍の強力な物理ダメージ"
            },

            # 回復スキル
            "ヒール": {
                "type": "heal",
                "multiplier": 2.0,
                "target": "single",
                "description": "単体のHPを魔力×2.0回復"
            },
            "全体回復": {
                "type": "heal",
                "multiplier": 1.2,
                "target": "all_allies",
                "description": "全体のHPを魔力×1.2回復"
            },

            # 補助スキル
            "攻撃強化": {
                "type": "buff",
                "effect": "attack",
                "multiplier": 1.3,
                "duration": 3,
                "target": "single",
                "description": "3ターン攻撃力1.3倍"
            },
            "防御強化": {
                "type": "buff",
                "effect": "defense",
                "multiplier": 1.5,
                "duration": 3,
                "target": "single",
                "description": "3ターン防御力1.5倍"
            },

            # パッシブスキル
            "会心の一撃": {
                "type": "passive",
                "effect": "critical",
                "chance": 0.2,
                "multiplier": 2.0,
                "description": "20%の確率でダメージ2.0倍"
            },
            "カウンター": {
                "type": "passive",
                "effect": "counter",
                "chance": 0.3,
                "multiplier": 0.5,
                "description": "30%の確率で反撃（0.5倍ダメージ）"
            },
            "根性": {
                "type": "passive",
                "effect": "endure",
                "chance": 0.15,
                "description": "15%の確率で致死ダメージをHP1で耐える"
            }
        }

        # Blackboardに保存
        self.blackboard.set_value("skills", skills)

        self.logger.info(f"Defined {len(skills)} skills")

    def _generate_gdscript(self) -> None:
        """
        スキルシステムのGDScriptを生成
        """
        self.logger.info("Generating Skill GDScript...")

        skills = self.blackboard.get_value("skills")

        # SkillSystem.gd の生成
        skill_system_script = self._create_skill_system_script(skills)
        self.generate_file(
            filepath="game/scripts/SkillSystem.gd",
            content=skill_system_script,
            description="スキルシステム - パワプロ特能風スキル管理"
        )

        # Skill.gd の生成
        skill_script = self._create_skill_script(skills)
        self.generate_file(
            filepath="game/scripts/Skill.gd",
            content=skill_script,
            description="スキルデータ定義"
        )

        self._gdscript_generated = True
        self.update_task_status(
            "skill_system",
            "completed",
            "Skill GDScript generated successfully"
        )

        self.send_message(
            "all",
            "Skill system GDScript generated",
            "info",
            {"files": ["SkillSystem.gd", "Skill.gd"]}
        )

    def _create_skill_system_script(self, skills: Dict) -> str:
        """
        SkillSystem.gd スクリプトを生成
        """
        return '''# SkillSystem.gd
# スキルシステム - パワプロ特能風スキル管理

extends Node

var active_buffs: Dictionary = {}  # {unit_id: [buff1, buff2, ...]}


func execute_skill(caster, skill: Dictionary, target) -> Dictionary:
    """スキルを実行"""
    var result = {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": false,
        "effects": []
    }

    match skill.type:
        "attack":
            result = _execute_attack_skill(caster, skill, target)

        "magic_attack":
            result = _execute_magic_attack_skill(caster, skill, target)

        "heal":
            result = _execute_heal_skill(caster, skill, target)

        "buff":
            result = _execute_buff_skill(caster, skill, target)

    return result


func _execute_attack_skill(caster, skill: Dictionary, target) -> Dictionary:
    """攻撃スキルを実行"""
    var damage = CombatAction.calculate_physical_damage(caster, target, skill.multiplier)

    # パッシブスキル: 会心の一撃
    if _check_passive(caster, "critical"):
        damage = int(damage * 2.0)
        print("%s の会心の一撃！" % _get_unit_name(caster))

    var actual_damage = target.take_damage(damage)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "damage": actual_damage
    }


func _execute_magic_attack_skill(caster, skill: Dictionary, target) -> Dictionary:
    """魔法攻撃スキルを実行"""
    var damage = CombatAction.calculate_magic_damage(caster, target, skill.multiplier)
    var actual_damage = target.take_damage(damage)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "damage": actual_damage
    }


func _execute_heal_skill(caster, skill: Dictionary, target) -> Dictionary:
    """回復スキルを実行"""
    var healing = CombatAction.calculate_healing(caster, skill.multiplier)
    var actual_healing = target.heal(healing)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "healing": actual_healing
    }


func _execute_buff_skill(caster, skill: Dictionary, target) -> Dictionary:
    """補助スキルを実行"""
    var buff = {
        "effect": skill.effect,
        "multiplier": skill.multiplier,
        "duration": skill.duration,
        "remaining_turns": skill.duration
    }

    var unit_id = _get_unit_id(target)
    if not active_buffs.has(unit_id):
        active_buffs[unit_id] = []

    active_buffs[unit_id].append(buff)

    return {
        "caster": _get_unit_name(caster),
        "skill": skill.name,
        "success": true,
        "target": _get_unit_name(target),
        "buff": skill.effect
    }


func _check_passive(unit, passive_type: String) -> bool:
    """パッシブスキルの発動判定"""
    if "passive_skills" not in unit:
        return false

    for passive in unit.passive_skills:
        if passive.effect == passive_type:
            return randf() < passive.chance

    return false


func update_buffs_turn() -> void:
    """バフのターン経過処理"""
    for unit_id in active_buffs.keys():
        var buffs = active_buffs[unit_id]
        var remaining_buffs = []

        for buff in buffs:
            buff.remaining_turns -= 1
            if buff.remaining_turns > 0:
                remaining_buffs.append(buff)

        if remaining_buffs.size() > 0:
            active_buffs[unit_id] = remaining_buffs
        else:
            active_buffs.erase(unit_id)


func get_buff_multiplier(unit, stat_type: String) -> float:
    """バフによる能力値倍率を取得"""
    var unit_id = _get_unit_id(unit)

    if not active_buffs.has(unit_id):
        return 1.0

    var multiplier = 1.0
    for buff in active_buffs[unit_id]:
        if buff.effect == stat_type:
            multiplier *= buff.multiplier

    return multiplier


func clear_all_buffs() -> void:
    """すべてのバフをクリア"""
    active_buffs.clear()


func _get_unit_id(unit) -> String:
    """ユニットIDを取得"""
    if "adventurer_name" in unit:
        return unit.adventurer_name
    return str(unit.get_instance_id())


func _get_unit_name(unit) -> String:
    """ユニット名を取得"""
    if "adventurer_name" in unit:
        return unit.adventurer_name
    return "Enemy"
'''

    def _create_skill_script(self, skills: Dict) -> str:
        """
        Skill.gd スクリプトを生成
        """
        # スキルデータをGDScript形式に変換
        skill_data_str = ""
        for skill_name, skill_info in skills.items():
            skill_data_str += f'''
    "{skill_name}": {{
        "name": "{skill_name}",
        "type": "{skill_info['type']}",
        "multiplier": {skill_info.get('multiplier', 1.0)},
        "target": "{skill_info.get('target', 'single')}",
        "description": "{skill_info['description']}",'''

            # オプショナルなフィールド
            if "effect" in skill_info:
                skill_data_str += f'\n        "effect": "{skill_info["effect"]}",'
            if "duration" in skill_info:
                skill_data_str += f'\n        "duration": {skill_info["duration"]},'
            if "chance" in skill_info:
                skill_data_str += f'\n        "chance": {skill_info["chance"]},'

            skill_data_str += "\n    },"

        return f'''# Skill.gd
# スキルデータ定義

extends Node
class_name Skill

# スキルタイプ
enum SkillType {{
    ATTACK,
    MAGIC_ATTACK,
    HEAL,
    BUFF,
    PASSIVE
}}

# すべてのスキルデータ
const SKILL_DATA: Dictionary = {{{skill_data_str}
}}


static func get_skill(skill_name: String) -> Dictionary:
    """スキルデータを取得"""
    return SKILL_DATA.get(skill_name, {{}})


static func get_all_skills() -> Dictionary:
    """すべてのスキルを取得"""
    return SKILL_DATA


static func get_skills_by_type(skill_type: String) -> Array:
    """タイプ別にスキルを取得"""
    var filtered = []
    for skill_name in SKILL_DATA:
        var skill = SKILL_DATA[skill_name]
        if skill.type == skill_type:
            filtered.append(skill)
    return filtered


static func get_attack_skills() -> Array:
    """攻撃スキルを取得"""
    return get_skills_by_type("attack") + get_skills_by_type("magic_attack")


static func get_heal_skills() -> Array:
    """回復スキルを取得"""
    return get_skills_by_type("heal")


static func get_buff_skills() -> Array:
    """補助スキルを取得"""
    return get_skills_by_type("buff")


static func get_passive_skills() -> Array:
    """パッシブスキルを取得"""
    return get_skills_by_type("passive")
'''

    def _handle_message(self, message: Dict) -> None:
        """
        メッセージを処理
        """
        msg_type = message.get("type")
        sender = message.get("sender")
        content = message.get("content")

        if msg_type == "request":
            if "skill" in content.lower():
                self.send_message(
                    sender,
                    "Skill system is ready. Pawapuro-style skills with multipliers.",
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
