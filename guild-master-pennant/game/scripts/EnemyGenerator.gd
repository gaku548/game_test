# EnemyGenerator.gd
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
