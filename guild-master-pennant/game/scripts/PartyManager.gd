# PartyManager.gd
# パーティ管理 - 4人編成と隊列システム

extends Node
class_name PartyManager

signal party_changed
signal member_added(member)
signal member_removed(member)
signal formation_changed

# パーティメンバー（最大4人）
var members: Array = []
const MAX_PARTY_SIZE: int = 4

# 隊列配置（0-2: 前列, 3: 後列）
# 前列: [0] [1] [2]
# 後列:     [3]
var formation: Array = [null, null, null, null]


func add_member(adventurer) -> bool:
    """メンバーを追加"""
    if members.size() >= MAX_PARTY_SIZE:
        push_warning("パーティは満員です")
        return false

    members.append(adventurer)
    _auto_arrange_formation()

    emit_signal("member_added", adventurer)
    emit_signal("party_changed")

    return true


func remove_member(adventurer) -> bool:
    """メンバーを削除"""
    var index = members.find(adventurer)
    if index == -1:
        return false

    members.remove_at(index)
    _remove_from_formation(adventurer)

    emit_signal("member_removed", adventurer)
    emit_signal("party_changed")

    return true


func set_formation(positions: Array) -> bool:
    """隊列を設定

    Args:
        positions: [member1, member2, member3, member4] の配列
    """
    if positions.size() != MAX_PARTY_SIZE:
        push_warning("隊列は4人である必要があります")
        return false

    # すべてのメンバーがパーティに所属しているか確認
    for member in positions:
        if member != null and not members.has(member):
            push_warning("パーティに所属していないメンバーを配置できません")
            return false

    formation = positions.duplicate()

    # 各メンバーに位置を設定
    for i in range(formation.size()):
        if formation[i] != null:
            formation[i].formation_position = i

    emit_signal("formation_changed")
    return true


func _auto_arrange_formation() -> void:
    """自動的に隊列を配置"""
    # 既存の配置をクリア
    for i in range(formation.size()):
        formation[i] = null

    # メンバーを職業に応じて配置
    var front_row_count = 0
    var back_row_assigned = false

    for member in members:
        match member.job_class:
            "Warrior", "Thief":
                # 前列に配置
                if front_row_count < 3:
                    formation[front_row_count] = member
                    member.formation_position = front_row_count
                    front_row_count += 1

            "Mage", "Priest", "Archer":
                # 可能なら後列に配置
                if not back_row_assigned:
                    formation[3] = member
                    member.formation_position = 3
                    back_row_assigned = true
                elif front_row_count < 3:
                    formation[front_row_count] = member
                    member.formation_position = front_row_count
                    front_row_count += 1

    emit_signal("formation_changed")


func _remove_from_formation(adventurer) -> void:
    """隊列から削除"""
    for i in range(formation.size()):
        if formation[i] == adventurer:
            formation[i] = null
            break

    _auto_arrange_formation()


func get_front_row() -> Array:
    """前列のメンバーを取得"""
    var front = []
    for i in range(3):
        if formation[i] != null:
            front.append(formation[i])
    return front


func get_back_row() -> Array:
    """後列のメンバーを取得"""
    var back = []
    if formation[3] != null:
        back.append(formation[3])
    return back


func get_alive_members() -> Array:
    """生存しているメンバーを取得"""
    var alive = []
    for member in members:
        if member.is_alive:
            alive.append(member)
    return alive


func get_member_at_position(position: int):
    """指定位置のメンバーを取得"""
    if position >= 0 and position < formation.size():
        return formation[position]
    return null


func swap_positions(pos1: int, pos2: int) -> bool:
    """2つの位置を入れ替え"""
    if pos1 < 0 or pos1 >= formation.size() or pos2 < 0 or pos2 >= formation.size():
        return false

    var temp = formation[pos1]
    formation[pos1] = formation[pos2]
    formation[pos2] = temp

    # 位置情報を更新
    if formation[pos1] != null:
        formation[pos1].formation_position = pos1
    if formation[pos2] != null:
        formation[pos2].formation_position = pos2

    emit_signal("formation_changed")
    return true


func is_full() -> bool:
    """パーティが満員か"""
    return members.size() >= MAX_PARTY_SIZE


func is_empty() -> bool:
    """パーティが空か"""
    return members.size() == 0


func get_party_status() -> Dictionary:
    """パーティの状態を取得"""
    var status = {
        "size": members.size(),
        "alive_count": get_alive_members().size(),
        "front_row": [],
        "back_row": [],
        "total_attack": 0,
        "total_defense": 0,
        "average_hp_percent": 0.0
    }

    var total_hp = 0
    var total_max_hp = 0

    # 前列
    for member in get_front_row():
        status.front_row.append(member.adventurer_name)
        status.total_attack += member.get_effective_attack()
        status.total_defense += member.get_effective_defense()
        total_hp += member.current_hp
        total_max_hp += member.max_hp

    # 後列
    for member in get_back_row():
        status.back_row.append(member.adventurer_name)
        status.total_attack += member.get_effective_attack()
        status.total_defense += member.get_effective_defense()
        total_hp += member.current_hp
        total_max_hp += member.max_hp

    if total_max_hp > 0:
        status.average_hp_percent = float(total_hp) / float(total_max_hp) * 100.0

    return status


func heal_all(amount: int) -> void:
    """全員を回復"""
    for member in members:
        member.heal(amount)


func revive_all() -> void:
    """全員を蘇生"""
    for member in members:
        if not member.is_alive:
            member.is_alive = true
            member.current_hp = member.max_hp


func get_formation_display() -> String:
    """隊列を視覚的に表示"""
    var display = "前列: "

    for i in range(3):
        if formation[i] != null:
            display += "[%s] " % formation[i].adventurer_name
        else:
            display += "[空] "

    display += "\n後列: "

    if formation[3] != null:
        display += "   [%s]" % formation[3].adventurer_name
    else:
        display += "   [空]"

    return display


func to_dict() -> Dictionary:
    """辞書形式にシリアライズ"""
    var member_dicts = []
    for member in members:
        member_dicts.append(member.to_dict())

    var formation_names = []
    for f in formation:
        if f != null:
            formation_names.append(f.adventurer_name)
        else:
            formation_names.append(null)

    return {
        "members": member_dicts,
        "formation": formation_names
    }
