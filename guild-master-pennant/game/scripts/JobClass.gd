# JobClass.gd
# 冒険者の職業クラス定義

extends Resource
class_name JobClass

enum Type {
	WARRIOR,   # 戦士 - 高HP/攻撃
	MAGE,      # 魔法使い - 魔力特化
	PRIEST,    # 僧侶 - 回復
	THIEF,     # 盗賊 - 速度
	ARCHER     # 弓使い - バランス
}

# 職業名
static func get_job_name(job_type: Type) -> String:
	match job_type:
		Type.WARRIOR:
			return "Warrior"
		Type.MAGE:
			return "Mage"
		Type.PRIEST:
			return "Priest"
		Type.THIEF:
			return "Thief"
		Type.ARCHER:
			return "Archer"
		_:
			return "Unknown"

# 職業別基礎ステータス
static func get_base_stats(job_type: Type) -> Dictionary:
	match job_type:
		Type.WARRIOR:
			return {
				"max_hp": 100,
				"attack": 15,
				"defense": 12,
				"magic": 3,
				"speed": 8
			}
		Type.MAGE:
			return {
				"max_hp": 60,
				"attack": 5,
				"defense": 5,
				"magic": 20,
				"speed": 10
			}
		Type.PRIEST:
			return {
				"max_hp": 70,
				"attack": 7,
				"defense": 8,
				"magic": 15,
				"speed": 9
			}
		Type.THIEF:
			return {
				"max_hp": 75,
				"attack": 12,
				"defense": 7,
				"magic": 5,
				"speed": 18
			}
		Type.ARCHER:
			return {
				"max_hp": 80,
				"attack": 13,
				"defense": 8,
				"magic": 6,
				"speed": 12
			}
		_:
			return {
				"max_hp": 50,
				"attack": 10,
				"defense": 10,
				"magic": 10,
				"speed": 10
			}

# 職業の特徴説明
static func get_description(job_type: Type) -> String:
	match job_type:
		Type.WARRIOR:
			return "高いHPと攻撃力を持つ前衛職"
		Type.MAGE:
			return "強力な魔法攻撃を操る魔術師"
		Type.PRIEST:
			return "味方を回復できるサポート職"
		Type.THIEF:
			return "素早い動きで先制攻撃を狙う"
		Type.ARCHER:
			return "バランスの取れた遠距離攻撃職"
		_:
			return ""
