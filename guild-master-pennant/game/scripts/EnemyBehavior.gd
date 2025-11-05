extends Node

# EnemyBehavior.gd - 敵の基本的な振る舞い

# このスクリプトは敵Nodeにアタッチされて使用されます

func take_damage(damage: int) -> int:
	"""ダメージを受ける"""
	var defense = get_meta("defense") if has_meta("defense") else 0
	var actual_damage = max(1, damage - defense)

	var current_hp = get_meta("current_hp")
	current_hp -= actual_damage

	if current_hp <= 0:
		current_hp = 0
		set_meta("is_alive", false)

	set_meta("current_hp", current_hp)
	return actual_damage

func get_attack() -> int:
	"""攻撃力を取得"""
	return get_meta("attack") if has_meta("attack") else 10

func get_defense() -> int:
	"""防御力を取得"""
	return get_meta("defense") if has_meta("defense") else 5

func is_enemy_alive() -> bool:
	"""生存しているか"""
	return get_meta("is_alive") if has_meta("is_alive") else true
