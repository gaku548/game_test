# DungeonManager.gd
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
    print("\n======= 階層 %d =======" % current_floor)
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
    print("\n全滅... 到達階層: %d" % max_floor_reached)
    emit_signal("dungeon_failed", max_floor_reached)


func stop_dungeon() -> void:
    """ダンジョン探索を中断"""
    is_exploring = false
    print("\nダンジョン探索を中断 - 到達階層: %d" % max_floor_reached)


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
