# TrainingSystem.gd
# 冒険者育成システム - レベルアップと能力成長

extends Node
class_name TrainingSystem

signal level_up(adventurer: Adventurer, new_level: int)
signal stat_improved(adventurer: Adventurer, stat_name: String, amount: int)
signal skill_learned(adventurer: Adventurer, skill: Skill)

# 経験値とレベル管理
var adventurer_exp: Dictionary = {}  # {adventurer: exp}
var adventurer_levels: Dictionary = {}  # {adventurer: level}

# レベルアップに必要な経験値（レベル×100）
const EXP_PER_LEVEL: int = 100

# 成長率（職業別）
const GROWTH_RATES = {
	JobClass.Type.WARRIOR: {
		"hp": 8,
		"attack": 3,
		"defense": 2,
		"magic": 1,
		"speed": 1
	},
	JobClass.Type.MAGE: {
		"hp": 4,
		"attack": 1,
		"defense": 1,
		"magic": 4,
		"speed": 2
	},
	JobClass.Type.PRIEST: {
		"hp": 5,
		"attack": 1,
		"defense": 2,
		"magic": 3,
		"speed": 2
	},
	JobClass.Type.THIEF: {
		"hp": 6,
		"attack": 2,
		"defense": 1,
		"magic": 1,
		"speed": 4
	},
	JobClass.Type.ARCHER: {
		"hp": 6,
		"attack": 3,
		"defense": 2,
		"magic": 1,
		"speed": 3
	}
}

# 冒険者を登録
func register_adventurer(adventurer: Adventurer) -> void:
	if not adventurer_exp.has(adventurer):
		adventurer_exp[adventurer] = 0
		adventurer_levels[adventurer] = 1
		print("%s registered in training system" % adventurer.adventurer_name)

# 経験値を獲得
func gain_exp(adventurer: Adventurer, exp_amount: int) -> void:
	if not adventurer_exp.has(adventurer):
		register_adventurer(adventurer)

	adventurer_exp[adventurer] += exp_amount
	print("%s gained %d EXP" % [adventurer.adventurer_name, exp_amount])

	# レベルアップチェック
	_check_level_up(adventurer)

# レベルアップをチェック
func _check_level_up(adventurer: Adventurer) -> void:
	var current_level = adventurer_levels[adventurer]
	var current_exp = adventurer_exp[adventurer]
	var required_exp = _get_required_exp(current_level)

	while current_exp >= required_exp:
		# レベルアップ！
		current_level += 1
		adventurer_exp[adventurer] -= required_exp
		adventurer_levels[adventurer] = current_level

		_apply_level_up(adventurer, current_level)

		# 次のレベルの必要経験値
		required_exp = _get_required_exp(current_level)
		current_exp = adventurer_exp[adventurer]

# レベルアップに必要な経験値を計算
func _get_required_exp(level: int) -> int:
	return level * EXP_PER_LEVEL

# レベルアップを適用
func _apply_level_up(adventurer: Adventurer, new_level: int) -> void:
	print("🎉 LEVEL UP! %s reached level %d" % [adventurer.adventurer_name, new_level])

	# 成長率に基づいてステータスを上昇
	var growth = GROWTH_RATES[adventurer.job_class]

	# HP上昇
	var hp_gain = growth["hp"] + _random_variance()
	adventurer.max_hp += hp_gain
	adventurer.current_hp += hp_gain
	stat_improved.emit(adventurer, "HP", hp_gain)

	# 攻撃力上昇
	var attack_gain = growth["attack"] + _random_variance()
	adventurer.attack += attack_gain
	stat_improved.emit(adventurer, "Attack", attack_gain)

	# 防御力上昇
	var defense_gain = growth["defense"] + _random_variance()
	adventurer.defense += defense_gain
	stat_improved.emit(adventurer, "Defense", defense_gain)

	# 魔力上昇
	var magic_gain = growth["magic"] + _random_variance()
	adventurer.magic += magic_gain
	stat_improved.emit(adventurer, "Magic", magic_gain)

	# 速度上昇
	var speed_gain = growth["speed"] + _random_variance()
	adventurer.speed += speed_gain
	stat_improved.emit(adventurer, "Speed", speed_gain)

	level_up.emit(adventurer, new_level)

	# 特定レベルでスキル習得
	_check_skill_learning(adventurer, new_level)

# ランダムな成長のばらつき (-1, 0, +1)
func _random_variance() -> int:
	return randi() % 3 - 1

# スキル習得をチェック
func _check_skill_learning(adventurer: Adventurer, level: int) -> void:
	# レベル5, 10, 15, 20でスキル習得
	if level % 5 == 0:
		var skill = _get_skill_for_level(adventurer.job_class, level)
		if skill != null:
			adventurer.equipped_skills.append(skill)
			skill_learned.emit(adventurer, skill)
			print("📖 %s learned %s!" % [adventurer.adventurer_name, skill.skill_name])

# レベルに応じたスキルを取得
func _get_skill_for_level(job_type: JobClass.Type, level: int) -> Skill:
	# TODO: SkillSystemと統合
	match job_type:
		JobClass.Type.WARRIOR:
			if level == 5:
				var skill = Skill.new("Shield Bash", Skill.SkillType.ATTACK)
				skill.power_multiplier = 1.3
				return skill
			elif level == 10:
				var skill = Skill.new("Berserk", Skill.SkillType.BUFF)
				skill.power_multiplier = 1.5
				return skill
		JobClass.Type.MAGE:
			if level == 5:
				var skill = Skill.new("Ice Bolt", Skill.SkillType.ATTACK)
				skill.power_multiplier = 2.2
				return skill
			elif level == 10:
				var skill = Skill.new("Meteor", Skill.SkillType.ATTACK)
				skill.power_multiplier = 3.0
				return skill
		JobClass.Type.PRIEST:
			if level == 5:
				var skill = Skill.new("Revive", Skill.SkillType.HEAL)
				skill.power_multiplier = 1.0
				return skill
			elif level == 10:
				var skill = Skill.new("Holy Light", Skill.SkillType.ATTACK)
				skill.power_multiplier = 2.0
				return skill

	return null

# 特訓でステータス強化
func train_stat(adventurer: Adventurer, stat_name: String, training_points: int) -> bool:
	if not adventurer_levels.has(adventurer):
		register_adventurer(adventurer)

	# トレーニングポイントを消費してステータス強化
	var gain = training_points

	match stat_name.to_lower():
		"hp":
			adventurer.max_hp += gain * 5
			adventurer.current_hp += gain * 5
			stat_improved.emit(adventurer, "HP", gain * 5)
		"attack":
			adventurer.attack += gain
			stat_improved.emit(adventurer, "Attack", gain)
		"defense":
			adventurer.defense += gain
			stat_improved.emit(adventurer, "Defense", gain)
		"magic":
			adventurer.magic += gain
			stat_improved.emit(adventurer, "Magic", gain)
		"speed":
			adventurer.speed += gain
			stat_improved.emit(adventurer, "Speed", gain)
		_:
			print("Invalid stat name: %s" % stat_name)
			return false

	print("%s trained %s (+%d)" % [adventurer.adventurer_name, stat_name, gain])
	return true

# 現在のステータスを取得
func get_adventurer_status(adventurer: Adventurer) -> Dictionary:
	if not adventurer_levels.has(adventurer):
		register_adventurer(adventurer)

	var level = adventurer_levels[adventurer]
	var exp = adventurer_exp[adventurer]
	var required_exp = _get_required_exp(level)

	return {
		"level": level,
		"exp": exp,
		"required_exp": required_exp,
		"exp_percentage": float(exp) / float(required_exp) * 100.0
	}

# 戦闘後の経験値を計算
func calculate_battle_exp(enemy_power: int, victory: bool) -> int:
	var base_exp = enemy_power / 10

	if victory:
		return base_exp
	else:
		# 敗北しても少し経験値
		return base_exp / 4

# パーティ全体に経験値を分配
func distribute_exp_to_party(party: Array[Adventurer], total_exp: int) -> void:
	var alive_count = 0
	for member in party:
		if member.is_alive:
			alive_count += 1

	if alive_count == 0:
		return

	# 生存者で分配
	var exp_per_member = total_exp / alive_count

	for member in party:
		if member.is_alive:
			gain_exp(member, exp_per_member)

# レベル差による経験値補正
func get_exp_multiplier(adventurer_level: int, enemy_level: int) -> float:
	var level_diff = enemy_level - adventurer_level

	if level_diff >= 5:
		return 1.5  # 格上の敵から多く学ぶ
	elif level_diff >= 0:
		return 1.0
	elif level_diff >= -5:
		return 0.7  # 格下の敵からは少し
	else:
		return 0.3  # 格下すぎる敵からはほとんど学べない

# 育成サマリーを表示
func get_training_summary(adventurer: Adventurer) -> String:
	var status = get_adventurer_status(adventurer)

	var summary = "=== %s Training Status ===\n" % adventurer.adventurer_name
	summary += "Level: %d\n" % status["level"]
	summary += "EXP: %d / %d (%.1f%%)\n" % [status["exp"], status["required_exp"], status["exp_percentage"]]
	summary += "\nCurrent Stats:\n"
	summary += "  HP: %d\n" % adventurer.max_hp
	summary += "  ATK: %d\n" % adventurer.attack
	summary += "  DEF: %d\n" % adventurer.defense
	summary += "  MAG: %d\n" % adventurer.magic
	summary += "  SPD: %d\n" % adventurer.speed
	summary += "\nLearned Skills: %d\n" % adventurer.equipped_skills.size()

	return summary

# 育成システムをリセット
func reset() -> void:
	adventurer_exp.clear()
	adventurer_levels.clear()
	print("Training system reset")
