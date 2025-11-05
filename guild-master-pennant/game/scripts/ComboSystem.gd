# ComboSystem.gd
# スキル連鎖コンボシステム

extends Node
class_name ComboSystem

signal combo_triggered(combo_name: String, multiplier: float)
signal combo_ended(total_damage: int)

# コンボ状態
var active_combo: String = ""
var combo_count: int = 0
var combo_chain: Array[String] = []
var combo_multiplier: float = 1.0
var combo_timer: float = 0.0
const COMBO_TIMEOUT: float = 3.0  # 3秒以内に次の行動

# コンボ定義
var combo_definitions: Dictionary = {}

func _ready():
	_initialize_combos()

# コンボ定義を初期化
func _initialize_combos() -> void:
	# 火炎コンボ
	combo_definitions["fire_chain"] = {
		"name": "Fire Chain",
		"sequence": ["Fire", "Fire", "Fire"],
		"multiplier": 1.5,
		"effect": "Area damage to all enemies",
		"description": "3連続火魔法で全体攻撃"
	}

	# 戦士コンボ
	combo_definitions["warrior_rush"] = {
		"name": "Warrior Rush",
		"sequence": ["Strong Attack", "Strong Attack", "Critical Strike"],
		"multiplier": 2.0,
		"effect": "Massive single target damage",
		"description": "強攻撃→強攻撃→必殺技"
	}

	# 盗賊コンボ
	combo_definitions["assassin_strike"] = {
		"name": "Assassin Strike",
		"sequence": ["Attack", "Attack", "Critical Strike"],
		"multiplier": 2.5,
		"effect": "Instant kill chance",
		"description": "素早い連撃から必殺技"
	}

	# 回復コンボ
	combo_definitions["divine_blessing"] = {
		"name": "Divine Blessing",
		"sequence": ["Heal", "Heal", "Mass Heal"],
		"multiplier": 1.8,
		"effect": "Full party restoration",
		"description": "単体回復→単体回復→全体回復"
	}

	# 魔法戦士コンボ
	combo_definitions["magic_blade"] = {
		"name": "Magic Blade",
		"sequence": ["Fire", "Strong Attack"],
		"multiplier": 1.7,
		"effect": "Magic infused physical attack",
		"description": "魔法で武器を強化して攻撃"
	}

	# サポートコンボ
	combo_definitions["tactical_advantage"] = {
		"name": "Tactical Advantage",
		"sequence": ["Power Up", "Defense Up", "Attack"],
		"multiplier": 1.6,
		"effect": "Buffed attack with extra damage",
		"description": "バフを重ねてから攻撃"
	}

	print("Combo system initialized with %d combos" % combo_definitions.size())

# 行動を記録してコンボをチェック
func register_action(action_name: String) -> Dictionary:
	var result = {
		"combo_active": false,
		"combo_name": "",
		"multiplier": 1.0,
		"combo_count": combo_count
	}

	# タイムアウトチェック
	if combo_timer > COMBO_TIMEOUT:
		_reset_combo()

	# チェーンに追加
	combo_chain.append(action_name)
	combo_count += 1
	combo_timer = 0.0

	# コンボをチェック
	var matched_combo = _check_for_combo()
	if matched_combo != "":
		active_combo = matched_combo
		var combo_data = combo_definitions[matched_combo]
		combo_multiplier = combo_data["multiplier"]

		result["combo_active"] = true
		result["combo_name"] = combo_data["name"]
		result["multiplier"] = combo_multiplier
		result["combo_count"] = combo_count

		combo_triggered.emit(combo_data["name"], combo_multiplier)
		print("🔥 COMBO: %s (x%.1f)" % [combo_data["name"], combo_multiplier])

		# コンボ達成後はリセット
		_reset_combo()

	return result

# コンボをチェック
func _check_for_combo() -> String:
	for combo_id in combo_definitions:
		var combo_data = combo_definitions[combo_id]
		var sequence = combo_data["sequence"]

		# チェーンが十分長いか
		if combo_chain.size() < sequence.size():
			continue

		# 最後のN個のアクションをチェック
		var recent_actions = combo_chain.slice(combo_chain.size() - sequence.size(), combo_chain.size())

		# シーケンスと一致するか
		var matches = true
		for i in range(sequence.size()):
			if recent_actions[i] != sequence[i]:
				matches = false
				break

		if matches:
			return combo_id

	return ""

# コンボをリセット
func _reset_combo() -> void:
	if combo_count > 0:
		combo_ended.emit(combo_count)

	active_combo = ""
	combo_count = 0
	combo_chain.clear()
	combo_multiplier = 1.0

# タイマーを更新（毎フレーム呼ぶ）
func _process(delta: float) -> void:
	if combo_count > 0:
		combo_timer += delta

		# タイムアウト
		if combo_timer > COMBO_TIMEOUT:
			_reset_combo()

# 現在のコンボ状態を取得
func get_combo_status() -> Dictionary:
	return {
		"active": combo_count > 0,
		"count": combo_count,
		"chain": combo_chain.duplicate(),
		"multiplier": combo_multiplier,
		"time_remaining": max(0.0, COMBO_TIMEOUT - combo_timer)
	}

# コンボ一覧を取得
func list_all_combos() -> String:
	var list = "=== Available Combos ===\n"
	for combo_id in combo_definitions:
		var combo = combo_definitions[combo_id]
		list += "\n【%s】 (x%.1f)\n" % [combo["name"], combo["multiplier"]]
		list += "  Sequence: %s\n" % " → ".join(combo["sequence"])
		list += "  Effect: %s\n" % combo["effect"]
		list += "  %s\n" % combo["description"]
	return list

# 特定のコンボ情報を取得
func get_combo_info(combo_id: String) -> Dictionary:
	if combo_definitions.has(combo_id):
		return combo_definitions[combo_id]
	return {}

# 現在のチェーンから可能なコンボを提案
func suggest_next_action() -> Array[String]:
	var suggestions: Array[String] = []

	if combo_chain.size() == 0:
		# 最初のアクション - すべてのコンボの最初の行動を提案
		for combo_id in combo_definitions:
			var sequence = combo_definitions[combo_id]["sequence"]
			if not suggestions.has(sequence[0]):
				suggestions.append(sequence[0])
	else:
		# 現在のチェーンから続くコンボを探す
		for combo_id in combo_definitions:
			var sequence = combo_definitions[combo_id]["sequence"]
			var chain_len = combo_chain.size()

			# チェーンがシーケンスの一部と一致するか
			if chain_len < sequence.size():
				var matches = true
				for i in range(chain_len):
					if combo_chain[i] != sequence[i]:
						matches = false
						break

				if matches:
					suggestions.append(sequence[chain_len])

	return suggestions

# カスタムコンボを追加
func add_custom_combo(combo_id: String, name: String, sequence: Array[String], multiplier: float, effect: String = "", description: String = "") -> void:
	combo_definitions[combo_id] = {
		"name": name,
		"sequence": sequence,
		"multiplier": multiplier,
		"effect": effect,
		"description": description
	}
	print("Custom combo added: %s" % name)

# コンボシステムを手動でリセット
func manual_reset() -> void:
	_reset_combo()
	print("Combo system reset")
