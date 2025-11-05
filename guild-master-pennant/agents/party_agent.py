"""
PartyAgent - パーティ管理システムの設計と実装を担当

PartyManager.gd を生成する
"""

from .base_agent import BaseAgent


class PartyAgent(BaseAgent):
    """
    パーティ管理を担当するエージェント

    責務:
    - 4人パーティ編成システム
    - 隊列管理（前列3人・後列1人）
    - パーティバランス調整
    """

    def __init__(self, blackboard):
        super().__init__("PartyAgent", blackboard, "Party Management Designer")

    def think(self) -> None:
        """パーティ管理システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_party_manager_script()

        # 完了を通知
        self.broadcast("パーティ管理システムのGDScriptを生成しました")
        self.update_task("party_system", "completed", "PartyManager.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing PartyAgent...")

        self.record_decision(
            "パーティ管理システムの設計",
            "4人パーティ編成。前列3人（被弾率60%）、後列1人（被弾率10%）の隊列システム。"
        )

        self.update_task("party_system", "in_progress", "Designing party formation")
        self._initialized = True

    def _generate_party_manager_script(self) -> None:
        """PartyManager.gd を生成"""
        script = '''# PartyManager.gd
# パーティ管理システム - 4人編成と隊列管理

extends Node
class_name PartyManager

const MAX_PARTY_SIZE = 4
const FRONT_ROW_SIZE = 3
const BACK_ROW_SIZE = 1

var party_members: Array[Adventurer] = []
var formation: Array[int] = []  # 隊列位置のインデックス

signal party_changed
signal member_defeated(member: Adventurer)
signal party_wiped_out

# パーティを初期化
func initialize_party(members: Array[Adventurer]) -> void:
\tif members.size() > MAX_PARTY_SIZE:
\t\tpush_error("Party size cannot exceed %d" % MAX_PARTY_SIZE)
\t\tmembers = members.slice(0, MAX_PARTY_SIZE)
\t
\tparty_members = members
\t_setup_default_formation()
\tparty_changed.emit()
\t
\tprint("Party initialized with %d members" % party_members.size())

# デフォルト隊列を設定
func _setup_default_formation() -> void:
\tformation.clear()
\t
\tfor i in range(party_members.size()):
\t\tvar member = party_members[i]
\t\t
\t\t# 前列3人、後列1人
\t\tif i < FRONT_ROW_SIZE:
\t\t\tmember.formation_position = i  # 0, 1, 2 (前列)
\t\telse:
\t\t\tmember.formation_position = i  # 3 (後列)
\t\t
\t\tformation.append(i)
\t
\tprint("Formation: Front [0, 1, 2], Back [3]")

# メンバーを追加
func add_member(member: Adventurer) -> bool:
\tif party_members.size() >= MAX_PARTY_SIZE:
\t\tprint("Party is full")
\t\treturn false
\t
\tparty_members.append(member)
\tmember.formation_position = party_members.size() - 1
\tformation.append(party_members.size() - 1)
\tparty_changed.emit()
\treturn true

# メンバーを削除
func remove_member(index: int) -> bool:
\tif index < 0 or index >= party_members.size():
\t\treturn false
\t
\tparty_members.remove_at(index)
\t_setup_default_formation()
\tparty_changed.emit()
\treturn true

# 隊列を変更
func change_formation(new_formation: Array[int]) -> bool:
\tif new_formation.size() != party_members.size():
\t\treturn false
\t
\t# 有効な配置かチェック
\tfor i in range(party_members.size()):
\t\tif not new_formation.has(i):
\t\t\treturn false
\t
\tformation = new_formation.duplicate()
\t
\t# メンバーの位置を更新
\tfor i in range(formation.size()):
\t\tvar member_idx = formation[i]
\t\tparty_members[member_idx].formation_position = i
\t
\tparty_changed.emit()
\tprint("Formation changed")
\treturn true

# 前列のメンバーを取得
func get_front_row() -> Array[Adventurer]:
\tvar front: Array[Adventurer] = []
\tfor member in party_members:
\t\tif member.is_in_front_row():
\t\t\tfront.append(member)
\treturn front

# 後列のメンバーを取得
func get_back_row() -> Array[Adventurer]:
\tvar back: Array[Adventurer] = []
\tfor member in party_members:
\t\tif not member.is_in_front_row():
\t\t\tback.append(member)
\treturn back

# 生存しているメンバーを取得
func get_alive_members() -> Array[Adventurer]:
\tvar alive: Array[Adventurer] = []
\tfor member in party_members:
\t\tif member.is_alive:
\t\t\talive.append(member)
\treturn alive

# 戦闘不能のメンバーを取得
func get_defeated_members() -> Array[Adventurer]:
\tvar defeated: Array[Adventurer] = []
\tfor member in party_members:
\t\tif not member.is_alive:
\t\t\tdefeated.append(member)
\treturn defeated

# 全滅しているか
func is_party_wiped_out() -> bool:
\treturn get_alive_members().size() == 0

# パーティの平均レベル（将来実装用）
func get_average_level() -> float:
\tif party_members.size() == 0:
\t\treturn 0.0
\t# TODO: レベルシステム実装後に対応
\treturn 1.0

# パーティの総合戦闘力
func get_total_combat_power() -> int:
\tvar total_power = 0
\tfor member in party_members:
\t\tif member.is_alive:
\t\t\ttotal_power += member.attack + member.defense + member.magic
\treturn total_power

# HP全回復
func full_heal_party() -> void:
\tfor member in party_members:
\t\tmember.current_hp = member.max_hp
\t\tmember.is_alive = true
\tprint("Party fully healed")

# パーティステータス表示
func get_party_status() -> String:
\tvar status = "=== Party Status ===\\n"
\tstatus += "Members: %d/%d\\n\\n" % [party_members.size(), MAX_PARTY_SIZE]
\t
\tfor i in range(party_members.size()):
\t\tvar member = party_members[i]
\t\tvar position = "Front" if member.is_in_front_row() else "Back"
\t\tvar alive_status = "Alive" if member.is_alive else "Defeated"
\t\t
\t\tstatus += "[%d] %s (%s) - %s\\n" % [i, member.adventurer_name, position, alive_status]
\t\tstatus += "    HP: %d/%d\\n" % [member.current_hp, member.max_hp]
\t
\treturn status

# メンバーが戦闘不能になった時の処理
func on_member_defeated(member: Adventurer) -> void:
\tmember_defeated.emit(member)
\t
\tif is_party_wiped_out():
\t\tparty_wiped_out.emit()
\t\tprint("Party wiped out!")

# 職業構成を取得
func get_job_composition() -> Dictionary:
\tvar composition = {}
\tfor member in party_members:
\t\tvar job_name = JobClass.get_job_name(member.job_class)
\t\tif not composition.has(job_name):
\t\t\tcomposition[job_name] = 0
\t\tcomposition[job_name] += 1
\treturn composition

# パーティバランスをチェック
func check_party_balance() -> String:
\tvar composition = get_job_composition()
\tvar warnings: Array[String] = []
\t
\t# 回復役チェック
\tif not composition.has("Priest"):
\t\twarnings.append("Warning: No healer in party")
\t
\t# 前列チェック
\tvar front_row = get_front_row()
\tif front_row.size() < 2:
\t\twarnings.append("Warning: Front row is weak")
\t
\t# 同職業だらけのチェック
\tfor job_name in composition:
\t\tif composition[job_name] >= 3:
\t\t\twarnings.append("Warning: Too many %ss" % job_name)
\t
\tif warnings.size() == 0:
\t\treturn "Party balance: Good"
\telse:
\t\treturn "\\n".join(warnings)
'''

        self.save_gdscript(
            "game/scripts/PartyManager.gd",
            script,
            "Party management with 4-member formation and balance checking"
        )
