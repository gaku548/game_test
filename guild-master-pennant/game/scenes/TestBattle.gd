extends Control

# TestBattle.gd - テスト戦闘シーン
# class_nameで定義されたグローバルクラスは自動的に利用可能

# UI要素
@onready var log_text = $VBoxContainer/LogPanel/LogText
@onready var party_info = $VBoxContainer/PartyPanel/PartyInfo
@onready var enemy_info = $VBoxContainer/EnemyPanel/EnemyInfo
@onready var next_turn_button = $VBoxContainer/ButtonPanel/NextTurnButton
@onready var auto_button = $VBoxContainer/ButtonPanel/AutoButton
@onready var back_button = $VBoxContainer/ButtonPanel/BackButton

# ゲームシステム
var party_manager: PartyManager
var combat_manager: CombatManager
var party: Array = []
var enemies: Array = []
var combat_log: Array = []
var auto_mode: bool = false

func _ready():
	print("=== テスト戦闘シーン ===")

	# ボタン接続
	if next_turn_button:
		next_turn_button.pressed.connect(_on_next_turn_pressed)
	if auto_button:
		auto_button.pressed.connect(_on_auto_pressed)
	if back_button:
		back_button.pressed.connect(_on_back_pressed)

	# ゲーム初期化
	_initialize_game()

func _initialize_game():
	_log("戦闘システム初期化中...")

	# パーティ作成
	_log("\n=== パーティ編成 ===")
	party = [
		Adventurer.new("アーサー", "Warrior"),
		Adventurer.new("メルラン", "Mage"),
		Adventurer.new("エレナ", "Priest"),
		Adventurer.new("ロビン", "Archer")
	]

	# 隊列設定
	for i in range(party.size()):
		party[i].formation_position = i

	for member in party:
		_log("  %s (%s) - HP:%d 攻撃:%d" % [
			member.adventurer_name,
			member.job_class,
			member.max_hp,
			member.attack
		])

	# 敵生成
	_log("\n=== 敵出現 ===")
	enemies = [
		_create_enemy("ゴブリン", 50, 10, 5),
		_create_enemy("オーク", 80, 15, 10)
	]

	for enemy in enemies:
		_log("  %s - HP:%d 攻撃:%d" % [
			enemy.name,
			enemy.max_hp,
			enemy.attack
		])

	# 戦闘マネージャー初期化
	combat_manager = CombatManager.new()
	add_child(combat_manager)

	_log("\n戦闘開始！")
	_update_display()

func _create_enemy(enemy_name: String, hp: int, attack: int, defense: int) -> Node:
	"""簡易的な敵を作成"""
	var enemy = Node.new()
	enemy.name = enemy_name
	enemy.set_meta("adventurer_name", enemy_name)
	enemy.set_meta("max_hp", hp)
	enemy.set_meta("current_hp", hp)
	enemy.set_meta("attack", attack)
	enemy.set_meta("defense", defense)
	enemy.set_meta("speed", 8)
	enemy.set_meta("is_alive", true)

	# 敵用メソッドを追加
	enemy.set_script(load("res://scripts/EnemyBehavior.gd") if ResourceLoader.exists("res://scripts/EnemyBehavior.gd") else null)

	return enemy

func _on_next_turn_pressed():
	if not combat_manager:
		return

	_log("\n--- ターン %d ---" % (combat_manager.turn_number + 1))

	# 1ターン実行
	var results = _execute_simple_turn()

	for result in results:
		_log("  %s" % result)

	_update_display()

	# 勝敗判定
	if _check_battle_end():
		next_turn_button.disabled = true
		auto_button.disabled = true

func _execute_simple_turn() -> Array:
	"""簡易的なターン処理"""
	var results = []

	# 味方の攻撃
	for member in party:
		if not member.is_alive:
			continue

		var alive_enemies = enemies.filter(func(e): return e.get_meta("is_alive"))
		if alive_enemies.size() == 0:
			break

		var target = alive_enemies[0]
		var damage = max(1, member.get_effective_attack() - target.get_meta("defense"))

		var new_hp = target.get_meta("current_hp") - damage
		target.set_meta("current_hp", new_hp)

		if new_hp <= 0:
			target.set_meta("current_hp", 0)
			target.set_meta("is_alive", false)
			results.append("%s が %s に %d ダメージ！ %s は倒れた！" % [
				member.adventurer_name, target.name, damage, target.name
			])
		else:
			results.append("%s が %s に %d ダメージ！" % [
				member.adventurer_name, target.name, damage
			])

	# 敵の攻撃
	for enemy in enemies:
		if not enemy.get_meta("is_alive"):
			continue

		var alive_party = party.filter(func(m): return m.is_alive)
		if alive_party.size() == 0:
			break

		# 被弾率に基づいてターゲット選択
		var target = _select_target_by_hit_rate(alive_party)
		var damage = max(1, enemy.get_meta("attack") - target.get_effective_defense())

		target.current_hp -= damage
		if target.current_hp <= 0:
			target.current_hp = 0
			target.is_alive = false
			results.append("%s が %s に %d ダメージ！ %s は倒れた！" % [
				enemy.name, target.adventurer_name, damage, target.adventurer_name
			])
		else:
			results.append("%s が %s に %d ダメージ！" % [
				enemy.name, target.adventurer_name, damage
			])

	return results

func _select_target_by_hit_rate(targets: Array):
	"""被弾率に基づいてターゲットを選択"""
	var weights = []
	var total_weight = 0.0

	for target in targets:
		var hit_rate = target.get_hit_rate()
		weights.append(hit_rate)
		total_weight += hit_rate

	var rand_val = randf() * total_weight
	var cumulative = 0.0

	for i in range(targets.size()):
		cumulative += weights[i]
		if rand_val <= cumulative:
			return targets[i]

	return targets[0]

func _check_battle_end() -> bool:
	"""戦闘終了判定"""
	var alive_party = party.filter(func(m): return m.is_alive)
	var alive_enemies = enemies.filter(func(e): return e.get_meta("is_alive"))

	if alive_party.size() == 0:
		_log("\n=== 敗北... ===")
		return true

	if alive_enemies.size() == 0:
		_log("\n=== 勝利！ ===")
		return true

	return false

func _on_auto_pressed():
	auto_mode = !auto_mode
	if auto_button:
		auto_button.text = "停止" if auto_mode else "自動戦闘"

	if auto_mode:
		_auto_battle()

func _auto_battle():
	"""自動戦闘"""
	if not auto_mode:
		return

	_on_next_turn_pressed()

	if not _check_battle_end() and auto_mode:
		await get_tree().create_timer(1.0).timeout
		_auto_battle()

func _on_back_pressed():
	get_tree().change_scene_to_file("res://scenes/Main.tscn")

func _log(message: String):
	"""ログに追加"""
	combat_log.append(message)
	_update_log_display()

func _update_log_display():
	"""ログ表示を更新"""
	if log_text:
		# 最新20件のみ表示
		var recent_logs = combat_log.slice(max(0, combat_log.size() - 20), combat_log.size())
		log_text.text = "\n".join(recent_logs)

func _update_display():
	"""情報表示を更新"""
	_update_party_display()
	_update_enemy_display()

func _update_party_display():
	"""パーティ情報を更新"""
	if party_info:
		var text = "=== 味方パーティ ===\n"
		for member in party:
			var status = "生存" if member.is_alive else "戦闘不能"
			text += "%s (%s)\n  HP: %d/%d (%s)\n" % [
				member.adventurer_name,
				member.job_class,
				member.current_hp,
				member.max_hp,
				status
			]
		party_info.text = text

func _update_enemy_display():
	"""敵情報を更新"""
	if enemy_info:
		var text = "=== 敵 ===\n"
		for enemy in enemies:
			var status = "生存" if enemy.get_meta("is_alive") else "撃破"
			text += "%s\n  HP: %d/%d (%s)\n" % [
				enemy.name,
				enemy.get_meta("current_hp"),
				enemy.get_meta("max_hp"),
				status
			]
		enemy_info.text = text
