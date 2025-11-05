# EnemyBehavior.gd
# 敵の行動AIシステム - 高度な行動パターンを実装

extends Resource
class_name EnemyBehavior

enum BehaviorType {
	AGGRESSIVE,    # 攻撃的 - 常に攻撃
	DEFENSIVE,     # 防御的 - HP低下時防御
	TACTICAL,      # 戦術的 - 状況に応じて行動変更
	SUPPORT,       # 補助型 - 仲間を強化
	BERSERKER      # 狂戦士 - HP低いほど攻撃力上昇
}

var behavior_type: BehaviorType = BehaviorType.AGGRESSIVE
var aggression: float = 1.0  # 攻撃性 (0.0 - 2.0)
var intelligence: float = 0.5  # 知性 (0.0 - 1.0)

func _init(type: BehaviorType = BehaviorType.AGGRESSIVE):
	behavior_type = type
	_set_behavior_stats()

# 行動タイプに応じた統計を設定
func _set_behavior_stats() -> void:
	match behavior_type:
		BehaviorType.AGGRESSIVE:
			aggression = 1.5
			intelligence = 0.3
		BehaviorType.DEFENSIVE:
			aggression = 0.7
			intelligence = 0.6
		BehaviorType.TACTICAL:
			aggression = 1.0
			intelligence = 0.8
		BehaviorType.SUPPORT:
			aggression = 0.5
			intelligence = 0.7
		BehaviorType.BERSERKER:
			aggression = 2.0
			intelligence = 0.2

# 行動を決定
func decide_action(enemy: Resource, allies: Array, enemies: Array) -> CombatAction:
	match behavior_type:
		BehaviorType.AGGRESSIVE:
			return _aggressive_behavior(enemy, enemies)
		BehaviorType.DEFENSIVE:
			return _defensive_behavior(enemy, enemies)
		BehaviorType.TACTICAL:
			return _tactical_behavior(enemy, enemies)
		BehaviorType.SUPPORT:
			return _support_behavior(enemy, allies)
		BehaviorType.BERSERKER:
			return _berserker_behavior(enemy, enemies)
		_:
			return _aggressive_behavior(enemy, enemies)

# 攻撃的な行動
func _aggressive_behavior(enemy: Resource, targets: Array) -> CombatAction:
	var action = CombatAction.new(CombatAction.ActionType.ATTACK)
	action.actor = enemy

	# 生存している敵を取得
	var alive_targets = targets.filter(func(t): return t.is_alive)
	if alive_targets.size() > 0:
		# HPが最も低いターゲットを狙う
		alive_targets.sort_custom(func(a, b): return a.current_hp < b.current_hp)
		action.target = alive_targets[0]

	return action

# 防御的な行動
func _defensive_behavior(enemy: Resource, targets: Array) -> CombatAction:
	var hp_percentage = enemy.get_hp_percentage()

	# HPが50%以下なら防御
	if hp_percentage < 0.5:
		var action = CombatAction.new(CombatAction.ActionType.DEFEND)
		action.actor = enemy
		return action

	# それ以外は攻撃
	return _aggressive_behavior(enemy, targets)

# 戦術的な行動
func _tactical_behavior(enemy: Resource, targets: Array) -> CombatAction:
	var hp_percentage = enemy.get_hp_percentage()
	var alive_targets = targets.filter(func(t): return t.is_alive)

	if alive_targets.size() == 0:
		var action = CombatAction.new(CombatAction.ActionType.WAIT)
		action.actor = enemy
		return action

	# HPが30%以下なら防御
	if hp_percentage < 0.3:
		var action = CombatAction.new(CombatAction.ActionType.DEFEND)
		action.actor = enemy
		return action

	# 魔力が高ければ後列を優先的に攻撃
	if "magic" in enemy and enemy.magic > 10:
		var back_row_targets = alive_targets.filter(func(t): return not t.is_in_front_row())
		if back_row_targets.size() > 0:
			var action = CombatAction.new(CombatAction.ActionType.ATTACK)
			action.actor = enemy
			action.target = back_row_targets[0]
			return action

	# 前列の脅威度が高いターゲットを狙う
	alive_targets.sort_custom(func(a, b): return a.attack > b.attack)
	var action = CombatAction.new(CombatAction.ActionType.ATTACK)
	action.actor = enemy
	action.target = alive_targets[0]
	return action

# 補助的な行動
func _support_behavior(enemy: Resource, allies: Array) -> CombatAction:
	var alive_allies = allies.filter(func(a): return a.is_alive)

	# 味方のHPが低ければ回復（将来実装）
	for ally in alive_allies:
		if ally.get_hp_percentage() < 0.4:
			# TODO: 回復スキル実装
			pass

	# デフォルトは待機
	var action = CombatAction.new(CombatAction.ActionType.WAIT)
	action.actor = enemy
	return action

# 狂戦士的な行動
func _berserker_behavior(enemy: Resource, targets: Array) -> CombatAction:
	var hp_percentage = enemy.get_hp_percentage()

	# HPが低いほど攻撃力が上がる（演出）
	var action = CombatAction.new(CombatAction.ActionType.ATTACK)
	action.actor = enemy

	var alive_targets = targets.filter(func(t): return t.is_alive)
	if alive_targets.size() > 0:
		# ランダムなターゲットを攻撃
		action.target = alive_targets[randi() % alive_targets.size()]

	return action

# ターゲット優先度を計算
func calculate_threat_level(target: Resource) -> float:
	var threat = 0.0

	if "attack" in target:
		threat += target.attack * 1.5
	if "magic" in target:
		threat += target.magic * 1.2
	if "speed" in target:
		threat += target.speed * 0.5

	# HPが低いほど脅威度が低い
	var hp_factor = target.get_hp_percentage()
	threat *= hp_factor

	return threat

# 行動の説明を取得
func get_behavior_description() -> String:
	match behavior_type:
		BehaviorType.AGGRESSIVE:
			return "Aggressive: Always attacks the weakest enemy"
		BehaviorType.DEFENSIVE:
			return "Defensive: Defends when HP is low"
		BehaviorType.TACTICAL:
			return "Tactical: Makes smart decisions based on situation"
		BehaviorType.SUPPORT:
			return "Support: Focuses on helping allies"
		BehaviorType.BERSERKER:
			return "Berserker: Becomes stronger as HP decreases"
		_:
			return "Unknown behavior"
