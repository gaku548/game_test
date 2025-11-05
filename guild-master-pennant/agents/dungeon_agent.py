"""
Dungeon Agent - ダンジョン踏破システムの担当エージェント

連続戦闘と階層管理を実装する。
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class DungeonAgent(BaseAgent):
    """
    ダンジョン踏破システムの設計と実装を担当するエージェント

    責務:
    - ダンジョン階層管理
    - 連続戦闘システム
    - 敵の強化ロジック
    - 踏破階層記録
    """

    def __init__(self, blackboard):
        super().__init__(
            name="DungeonAgent",
            blackboard=blackboard,
            role="ダンジョン踏破システムの設計と実装"
        )
        self._initialized = False
        self._gdscript_generated = False

    def think(self) -> None:
        """
        ダンジョンシステムの自律的な設計と実装
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
        self.logger.info("Initializing Dungeon System...")

        self.update_task_status(
            "dungeon_system",
            "in_progress",
            "Designing continuous dungeon exploration"
        )

        self.record_decision(
            decision="Implement floor-based dungeon with scaling enemies",
            rationale="階層ごとに敵を1.1倍強化し、到達階層数でギルドの成績を評価"
        )

        self._initialized = True
        self.send_message("all", "Dungeon system initialized", "info")

    def _generate_gdscript(self) -> None:
        """
        ダンジョンシステムのGDScriptを生成
        """
        self.logger.info("Generating Dungeon GDScript...")

        # DungeonManager.gd の生成
        dungeon_manager_script = self._create_dungeon_manager_script()
        self.generate_file(
            filepath="game/scripts/DungeonManager.gd",
            content=dungeon_manager_script,
            description="ダンジョン管理 - 階層管理と連続戦闘"
        )

        # EnemyGenerator.gd の生成
        enemy_generator_script = self._create_enemy_generator_script()
        self.generate_file(
            filepath="game/scripts/EnemyGenerator.gd",
            content=enemy_generator_script,
            description="敵生成 - 階層に応じた敵の生成と強化"
        )

        self._gdscript_generated = True
        self.update_task_status(
            "dungeon_system",
            "completed",
            "Dungeon GDScript generated successfully"
        )

        self.send_message(
            "all",
            "Dungeon system GDScript generated",
            "info",
            {"files": ["DungeonManager.gd", "EnemyGenerator.gd"]}
        )

    def _create_dungeon_manager_script(self) -> str:
        """
        DungeonManager.gd スクリプトを生成
        """
        return '''# DungeonManager.gd
# ダンジョン管理 - 階層管理と連続戦闘

extends Node
class_name DungeonManager

signal floor_started(floor_number: int)
signal floor_cleared(floor_number: int)
signal dungeon_failed(floor_reached: int)
signal dungeon_completed(max_floor: int)

var current_floor: int = 0
var max_floor_reached: int = 0
var is_exploring: bool = false

var party_manager: PartyManager
var combat_manager: CombatManager
var enemy_generator: EnemyGenerator

const FLOOR_SCALING: float = 1.1  # 階層ごとの敵強化倍率


func _ready():
    """初期化"""
    party_manager = PartyManager.new()
    combat_manager = CombatManager.new()
    enemy_generator = EnemyGenerator.new()

    add_child(party_manager)
    add_child(combat_manager)
    add_child(enemy_generator)


func start_dungeon(party: Array) -> void:
    """ダンジョン探索開始"""
    if party.size() == 0:
        push_error("パーティが空です")
        return

    is_exploring = true
    current_floor = 1
    max_floor_reached = 0

    # パーティを設定
    for member in party:
        party_manager.add_member(member)

    _start_floor()


func _start_floor() -> void:
    """階層を開始"""
    print("\\n======= 階層 %d =======" % current_floor)
    emit_signal("floor_started", current_floor)

    # 敵を生成
    var enemies = enemy_generator.generate_enemies_for_floor(current_floor)

    # 戦闘開始
    combat_manager.start_combat(party_manager.get_alive_members(), enemies)

    # 戦闘ループ
    _combat_loop()


func _combat_loop() -> void:
    """戦闘ループ"""
    while combat_manager.is_active():
        combat_manager.execute_turn()

        # 少し待つ（実際のゲームではプレイヤーの入力を待つ）
        await get_tree().create_timer(0.5).timeout

    # 戦闘結果を確認
    _check_combat_result()


func _check_combat_result() -> void:
    """戦闘結果を確認"""
    var alive_members = party_manager.get_alive_members()

    if alive_members.size() == 0:
        # 全滅
        _fail_dungeon()
    else:
        # 階層クリア
        _clear_floor()


func _clear_floor() -> void:
    """階層クリア"""
    print("階層 %d クリア！" % current_floor)
    emit_signal("floor_cleared", current_floor)

    max_floor_reached = current_floor

    # 次の階層へ
    current_floor += 1
    _start_floor()


func _fail_dungeon() -> void:
    """ダンジョン失敗（全滅）"""
    is_exploring = false
    print("\\n全滅... 到達階層: %d" % max_floor_reached)
    emit_signal("dungeon_failed", max_floor_reached)


func stop_dungeon() -> void:
    """ダンジョン探索を中断"""
    is_exploring = false
    print("\\nダンジョン探索を中断 - 到達階層: %d" % max_floor_reached)


func get_dungeon_status() -> Dictionary:
    """ダンジョンの状態を取得"""
    return {
        "current_floor": current_floor,
        "max_floor_reached": max_floor_reached,
        "is_exploring": is_exploring,
        "party_status": party_manager.get_party_status() if party_manager else {}
    }


func get_floor_scaling(floor: int) -> float:
    """階層による敵の強化倍率を計算"""
    return pow(FLOOR_SCALING, floor - 1)


func get_record() -> Dictionary:
    """ダンジョン踏破記録を取得"""
    return {
        "max_floor_reached": max_floor_reached,
        "scaling_factor": FLOOR_SCALING,
        "final_enemy_strength": get_floor_scaling(max_floor_reached)
    }
'''

    def _create_enemy_generator_script(self) -> str:
        """
        EnemyGenerator.gd スクリプトを生成
        """
        return '''# EnemyGenerator.gd
# 敵生成 - 階層に応じた敵の生成と強化

extends Node
class_name EnemyGenerator

# 敵のベーステンプレート
const ENEMY_TEMPLATES: Dictionary = {
    "Goblin": {
        "hp": 50,
        "attack": 10,
        "defense": 5,
        "magic": 0,
        "speed": 12
    },
    "Orc": {
        "hp": 80,
        "attack": 15,
        "defense": 10,
        "magic": 0,
        "speed": 6
    },
    "Dark Mage": {
        "hp": 40,
        "attack": 5,
        "defense": 3,
        "magic": 18,
        "speed": 10
    },
    "Skeleton": {
        "hp": 60,
        "attack": 12,
        "defense": 8,
        "magic": 0,
        "speed": 8
    },
    "Dragon": {
        "hp": 200,
        "attack": 25,
        "defense": 20,
        "magic": 15,
        "speed": 14
    }
}


func generate_enemies_for_floor(floor: int) -> Array:
    """階層に応じて敵を生成"""
    var enemies = []
    var scaling = pow(1.1, floor - 1)  # 階層ごとに1.1倍

    # 階層に応じた敵の数と種類を決定
    var enemy_count = _get_enemy_count_for_floor(floor)
    var enemy_types = _select_enemy_types_for_floor(floor)

    for i in range(enemy_count):
        var enemy_type = enemy_types[i % enemy_types.size()]
        var enemy = _create_enemy(enemy_type, scaling)
        enemies.append(enemy)

    return enemies


func _get_enemy_count_for_floor(floor: int) -> int:
    """階層に応じた敵の数を決定"""
    if floor <= 5:
        return 2
    elif floor <= 10:
        return 3
    else:
        return 4


func _select_enemy_types_for_floor(floor: int) -> Array:
    """階層に応じた敵の種類を選択"""
    if floor <= 3:
        return ["Goblin", "Goblin"]
    elif floor <= 7:
        return ["Goblin", "Orc", "Skeleton"]
    elif floor <= 15:
        return ["Orc", "Dark Mage", "Skeleton"]
    elif floor <= 25:
        return ["Orc", "Dark Mage", "Skeleton", "Dragon"]
    else:
        return ["Dragon", "Dark Mage", "Orc", "Skeleton"]


func _create_enemy(enemy_type: String, scaling: float) -> Node:
    """敵を作成"""
    var template = ENEMY_TEMPLATES.get(enemy_type, ENEMY_TEMPLATES["Goblin"])

    var enemy = Node.new()
    enemy.name = enemy_type

    # 基本ステータスに倍率を適用
    enemy.set("max_hp", int(template.hp * scaling))
    enemy.set("current_hp", int(template.hp * scaling))
    enemy.set("attack", int(template.attack * scaling))
    enemy.set("defense", int(template.defense * scaling))
    enemy.set("magic", int(template.magic * scaling))
    enemy.set("speed", int(template.speed * scaling))
    enemy.set("is_alive", true)
    enemy.set("type", enemy_type)

    # 敵のメソッド
    enemy.set_script(load("res://scripts/EnemyBehavior.gd") if ResourceLoader.exists("res://scripts/EnemyBehavior.gd") else null)

    # 簡易的なメソッドを追加（GDScriptのset_scriptが使えない場合）
    if not enemy.has_method("take_damage"):
        _add_enemy_methods(enemy)

    return enemy


func _add_enemy_methods(enemy: Node) -> void:
    """敵にメソッドを追加（簡易実装）"""
    # Note: 実際には EnemyBehavior.gd スクリプトで実装する
    # ここでは概念的な説明のみ

    # take_damage メソッド
    # func take_damage(damage: int) -> int:
    #     var actual_damage = max(1, damage - enemy.defense)
    #     enemy.current_hp -= actual_damage
    #     if enemy.current_hp <= 0:
    #         enemy.current_hp = 0
    #         enemy.is_alive = false
    #     return actual_damage

    pass


func get_enemy_info(enemy_type: String) -> Dictionary:
    """敵の情報を取得"""
    return ENEMY_TEMPLATES.get(enemy_type, {})


func get_all_enemy_types() -> Array:
    """すべての敵タイプを取得"""
    return ENEMY_TEMPLATES.keys()
'''

    def _handle_message(self, message: Dict) -> None:
        """
        メッセージを処理
        """
        msg_type = message.get("type")
        sender = message.get("sender")
        content = message.get("content")

        if msg_type == "request":
            if "dungeon" in content.lower():
                self.send_message(
                    sender,
                    "Dungeon system is ready. Floor-based scaling exploration.",
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
