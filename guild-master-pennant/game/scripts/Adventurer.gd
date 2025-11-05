# Adventurer.gd
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
	adventurer_name = name
	job_class = job
	_apply_job_stats()

# 職業別ステータスを適用
func _apply_job_stats() -> void:
	var stats = JobClass.get_base_stats(job_class)
	max_hp = stats["max_hp"]
	current_hp = max_hp
	attack = stats["attack"]
	defense = stats["defense"]
	magic = stats["magic"]
	speed = stats["speed"]

# 前列にいるか
func is_in_front_row() -> bool:
	return formation_position < 3

# 実効攻撃力（位置修正込み）
func get_effective_attack() -> int:
	var modifier = 1.1 if is_in_front_row() else 1.0
	return int(attack * modifier)

# 実効防御力（位置修正込み）
func get_effective_defense() -> int:
	var modifier = 1.0 if is_in_front_row() else 1.1
	return int(defense * modifier)

# 被弾率
func get_hit_rate() -> float:
	if is_in_front_row():
		return 0.6 / 3.0  # 前列3人で60%を分担
	else:
		return 0.1  # 後列は10%

# ダメージを受ける
func take_damage(damage: int) -> int:
	var actual_damage = max(1, damage - get_effective_defense())
	current_hp -= actual_damage

	if current_hp <= 0:
		current_hp = 0
		is_alive = false

	return actual_damage

# 回復
func heal(amount: int) -> int:
	if not is_alive:
		return 0

	var old_hp = current_hp
	current_hp = min(max_hp, current_hp + amount)
	return current_hp - old_hp

# HP割合を取得
func get_hp_percentage() -> float:
	if max_hp == 0:
		return 0.0
	return float(current_hp) / float(max_hp)

# 蘇生
func revive(hp_amount: int = -1) -> void:
	if hp_amount < 0:
		hp_amount = max_hp / 2
	current_hp = min(hp_amount, max_hp)
	is_alive = true

# ステータス表示用
func get_status_text() -> String:
	var status = "Name: %s (%s)\n" % [adventurer_name, JobClass.get_job_name(job_class)]
	status += "HP: %d/%d\n" % [current_hp, max_hp]
	status += "ATK: %d  DEF: %d\n" % [attack, defense]
	status += "MAG: %d  SPD: %d\n" % [magic, speed]
	status += "Position: %s" % ("Front" if is_in_front_row() else "Back")
	return status
