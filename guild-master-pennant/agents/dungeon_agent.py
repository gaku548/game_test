"""
DungeonAgent - ダンジョン踏破システムの設計と実装を担当

DungeonManager.gd と EnemyGenerator.gd を生成する
"""

from .base_agent import BaseAgent


class DungeonAgent(BaseAgent):
    """
    ダンジョン踏破システムを担当するエージェント

    責務:
    - ダンジョン階層管理
    - 敵生成システム
    - 階層別難易度調整
    - 連続戦闘管理
    """

    def __init__(self, blackboard):
        super().__init__("DungeonAgent", blackboard, "Dungeon System Designer")

    def think(self) -> None:
        """ダンジョンシステムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_enemy_generator_script()
        self._generate_dungeon_manager_script()

        # 完了を通知
        self.broadcast("ダンジョンシステムのGDScriptを生成しました")
        self.update_task("dungeon_system", "completed", "DungeonManager.gd and EnemyGenerator.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing DungeonAgent...")

        self.record_decision(
            "ダンジョンシステムの設計",
            "階層ごとに敵が1.1倍強化される連続戦闘システム。"
            "階層に応じた敵編成で難易度が上昇する。"
        )

        self.update_task("dungeon_system", "in_progress", "Designing dungeon progression")
        self._initialized = True

    def _generate_enemy_generator_script(self) -> None:
        """EnemyGenerator.gd を生成 - Enemy クラスを含む"""
        script = '''# EnemyGenerator.gd
# 敵生成システム - 階層に応じた敵の生成と強化

extends Node
class_name EnemyGenerator

# 敵クラス
class Enemy extends Resource:
\tvar name: String = "Enemy"
\tvar type: String = "Goblin"
\tvar max_hp: int = 50
\tvar current_hp: int = 50
\tvar attack: int = 10
\tvar defense: int = 5
\tvar magic: int = 0
\tvar speed: int = 10
\tvar is_alive: bool = true
\t
\tfunc _init(enemy_type: String = "Goblin", scaling: float = 1.0):
\t\ttype = enemy_type
\t\tname = enemy_type
\t\t_apply_stats(scaling)
\t
\tfunc _apply_stats(scaling: float) -> void:
\t\tvar base_stats = _get_base_stats()
\t\tmax_hp = int(base_stats["hp"] * scaling)
\t\tcurrent_hp = max_hp
\t\tattack = int(base_stats["attack"] * scaling)
\t\tdefense = int(base_stats["defense"] * scaling)
\t\tmagic = int(base_stats["magic"] * scaling)
\t\tspeed = int(base_stats["speed"] * scaling)
\t
\tfunc _get_base_stats() -> Dictionary:
\t\tmatch type:
\t\t\t"Goblin":
\t\t\t\treturn {"hp": 50, "attack": 10, "defense": 5, "magic": 0, "speed": 12}
\t\t\t"Orc":
\t\t\t\treturn {"hp": 80, "attack": 15, "defense": 10, "magic": 0, "speed": 6}
\t\t\t"Dark Mage":
\t\t\t\treturn {"hp": 40, "attack": 5, "defense": 3, "magic": 18, "speed": 10}
\t\t\t"Skeleton":
\t\t\t\treturn {"hp": 60, "attack": 12, "defense": 8, "magic": 0, "speed": 8}
\t\t\t"Dragon":
\t\t\t\treturn {"hp": 200, "attack": 25, "defense": 20, "magic": 15, "speed": 14}
\t\t\t_:
\t\t\t\treturn {"hp": 50, "attack": 10, "defense": 5, "magic": 0, "speed": 10}
\t
\tfunc take_damage(damage: int) -> int:
\t\tvar actual_damage = max(1, damage - defense)
\t\tcurrent_hp -= actual_damage
\t\tif current_hp <= 0:
\t\t\tcurrent_hp = 0
\t\t\tis_alive = false
\t\treturn actual_damage
\t
\tfunc get_hp_percentage() -> float:
\t\tif max_hp == 0:
\t\t\treturn 0.0
\t\treturn float(current_hp) / float(max_hp)

# 階層別敵編成テンプレート
const FLOOR_TEMPLATES = {
\t1: ["Goblin", "Goblin"],
\t2: ["Goblin", "Goblin", "Skeleton"],
\t3: ["Goblin", "Skeleton", "Skeleton"],
\t5: ["Orc", "Goblin", "Goblin"],
\t7: ["Orc", "Skeleton", "Dark Mage"],
\t10: ["Orc", "Orc", "Dark Mage"],
\t15: ["Dragon", "Orc", "Dark Mage"],
\t20: ["Dragon", "Dragon", "Dark Mage"]
}

# 階層に応じた敵を生成
func generate_enemies_for_floor(floor: int) -> Array:
\tvar enemies: Array = []
\t
\t# スケーリング計算（1階層ごとに1.1倍）
\tvar scaling = pow(1.1, floor - 1)
\t
\t# 敵編成を決定
\tvar enemy_types = _get_enemy_types_for_floor(floor)
\t
\t# 敵を生成
\tfor enemy_type in enemy_types:
\t\tvar enemy = Enemy.new(enemy_type, scaling)
\t\tenemies.append(enemy)
\t
\tprint("Floor %d: Generated %d enemies (scaling: %.2fx)" % [floor, enemies.size(), scaling])
\treturn enemies

# 階層に応じた敵タイプを取得
func _get_enemy_types_for_floor(floor: int) -> Array[String]:
\tvar enemy_types: Array[String] = []
\t
\t# テンプレートから最も近い階層を探す
\tvar template_floor = 1
\tfor floor_num in FLOOR_TEMPLATES.keys():
\t\tif floor >= floor_num:
\t\t\ttemplate_floor = floor_num
\t
\tenemy_types = FLOOR_TEMPLATES[template_floor].duplicate()
\t
\treturn enemy_types

# ランダムな敵を生成
func generate_random_enemy(floor: int) -> Enemy:
\tvar scaling = pow(1.1, floor - 1)
\tvar enemy_types = ["Goblin", "Orc", "Skeleton", "Dark Mage"]
\t
\tif floor >= 15:
\t\tenemy_types.append("Dragon")
\t
\tvar random_type = enemy_types[randi() % enemy_types.size()]
\treturn Enemy.new(random_type, scaling)

# ボス敵を生成
func generate_boss(floor: int) -> Enemy:
\tvar scaling = pow(1.1, floor - 1) * 1.5  # ボスは1.5倍
\treturn Enemy.new("Dragon", scaling)

# 敵の強さを評価
func calculate_enemy_power(enemy: Enemy) -> int:
\treturn enemy.max_hp + enemy.attack * 2 + enemy.defense + enemy.magic

# 階層の難易度を計算
func calculate_floor_difficulty(floor: int) -> Dictionary:
\tvar enemies = generate_enemies_for_floor(floor)
\tvar total_power = 0
\t
\tfor enemy in enemies:
\t\ttotal_power += calculate_enemy_power(enemy)
\t
\treturn {
\t\t"floor": floor,
\t\t"enemy_count": enemies.size(),
\t\t"total_power": total_power,
\t\t"scaling": pow(1.1, floor - 1)
\t}
'''

        self.save_gdscript(
            "game/scripts/EnemyGenerator.gd",
            script,
            "Enemy generation system with floor-based scaling and templates"
        )

    def _generate_dungeon_manager_script(self) -> None:
        """DungeonManager.gd を生成"""
        script = '''# DungeonManager.gd
# ダンジョン管理システム - 階層管理と連続戦闘

extends Node
class_name DungeonManager

signal floor_started(floor: int)
signal floor_completed(floor: int, victory: bool)
signal dungeon_completed(max_floor: int)
signal party_defeated(floor: int)

var current_floor: int = 0
var max_floor_reached: int = 0
var is_dungeon_active: bool = false

var party_manager: PartyManager = null
var combat_manager: CombatManager = null
var enemy_generator: EnemyGenerator = null

var floor_history: Array[Dictionary] = []

func _ready():
\tenemy_generator = EnemyGenerator.new()

# ダンジョン探索を開始
func start_dungeon(party: PartyManager, combat: CombatManager, starting_floor: int = 1) -> void:
\tparty_manager = party
\tcombat_manager = combat
\tcurrent_floor = starting_floor
\tmax_floor_reached = 0
\tis_dungeon_active = true
\tfloor_history.clear()
\t
\tprint("=== Dungeon Started ===")
\tprint("Starting from floor %d" % current_floor)

# 次の階層へ進む
func advance_to_next_floor() -> void:
\tif not is_dungeon_active:
\t\treturn
\t
\tcurrent_floor += 1
\tmax_floor_reached = max(max_floor_reached, current_floor)
\t
\tfloor_started.emit(current_floor)
\tprint("\\n=== Floor %d ===" % current_floor)
\t
\t# 敵を生成
\tvar enemies = enemy_generator.generate_enemies_for_floor(current_floor)
\t
\t# 戦闘開始
\tstart_floor_combat(enemies)

# 階層の戦闘を開始
func start_floor_combat(enemies: Array) -> void:
\tvar party_members = party_manager.party_members
\t
\tprint("Party vs %d enemies" % enemies.size())
\t
\t# 戦闘マネージャーで戦闘開始
\tcombat_manager.start_combat(party_members, enemies)
\t
\t# 戦闘ループ（自動進行）
\twhile combat_manager.is_active():
\t\tcombat_manager.execute_turn()
\t\t
\t\t# 安全装置: 最大100ターン
\t\tif combat_manager.current_turn > 100:
\t\t\tprint("Turn limit reached!")
\t\t\tbreak
\t
\t# 戦闘結果を記録
\t_record_floor_result()

# 階層結果を記録
func _record_floor_result() -> void:
\tvar victory = party_manager.get_alive_members().size() > 0
\t
\tvar result = {
\t\t"floor": current_floor,
\t\t"victory": victory,
\t\t"turns": combat_manager.current_turn,
\t\t"party_survivors": party_manager.get_alive_members().size()
\t}
\tfloor_history.append(result)
\t
\tfloor_completed.emit(current_floor, victory)
\t
\tif victory:
\t\tprint("Floor %d cleared!" % current_floor)
\telse:
\t\tprint("Party defeated on floor %d" % current_floor)
\t\t_end_dungeon(false)

# ダンジョンを終了
func _end_dungeon(completed: bool) -> void:
\tis_dungeon_active = false
\t
\tprint("\\n=== Dungeon Run Ended ===")
\tprint("Max floor reached: %d" % max_floor_reached)
\t
\tif completed:
\t\tdungeon_completed.emit(max_floor_reached)
\telse:
\t\tparty_defeated.emit(current_floor)

# 連続で階層を進む
func run_continuous_floors(max_floors: int = 50) -> Dictionary:
\tadvance_to_next_floor()
\t
\twhile is_dungeon_active and current_floor < max_floors:
\t\t# 前の階層の結果をチェック
\t\tvar last_result = floor_history[floor_history.size() - 1]
\t\t
\t\tif not last_result["victory"]:
\t\t\tbreak
\t\t
\t\t# パーティを回復（階層クリア報酬として）
\t\tparty_manager.full_heal_party()
\t\t
\t\t# 次の階層へ
\t\tadvance_to_next_floor()
\t
\treturn get_dungeon_summary()

# ダンジョン結果のサマリーを取得
func get_dungeon_summary() -> Dictionary:
\tvar total_turns = 0
\tvar victories = 0
\t
\tfor result in floor_history:
\t\ttotal_turns += result["turns"]
\t\tif result["victory"]:
\t\t\tvictories += 1
\t
\treturn {
\t\t"max_floor_reached": max_floor_reached,
\t\t"total_floors": floor_history.size(),
\t\t"total_victories": victories,
\t\t"total_turns": total_turns,
\t\t"final_scaling": pow(1.1, max_floor_reached - 1) if max_floor_reached > 0 else 1.0
\t}

# 現在の進行状況を表示
func get_progress_text() -> String:
\tvar text = "=== Dungeon Progress ===\\n"
\ttext += "Current Floor: %d\\n" % current_floor
\ttext += "Max Floor Reached: %d\\n" % max_floor_reached
\ttext += "Floors Cleared: %d\\n" % floor_history.size()
\t
\tif floor_history.size() > 0:
\t\ttext += "\\nRecent Floors:\\n"
\t\tvar recent_count = min(5, floor_history.size())
\t\tfor i in range(recent_count):
\t\t\tvar idx = floor_history.size() - recent_count + i
\t\t\tvar result = floor_history[idx]
\t\t\tvar status = "✓" if result["victory"] else "✗"
\t\t\ttext += "  %s Floor %d (%d turns)\\n" % [status, result["floor"], result["turns"]]
\t
\treturn text

# 推奨パーティレベルを計算
func get_recommended_power_for_floor(floor: int) -> int:
\tvar difficulty = enemy_generator.calculate_floor_difficulty(floor)
\treturn difficulty["total_power"]

# ダンジョンの状態をリセット
func reset() -> void:
\tcurrent_floor = 0
\tmax_floor_reached = 0
\tis_dungeon_active = false
\tfloor_history.clear()
\tprint("Dungeon reset")
'''

        self.save_gdscript(
            "game/scripts/DungeonManager.gd",
            script,
            "Dungeon progression system with floor management and continuous combat"
        )
