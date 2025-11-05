"""
EquipmentAgent - 装備システムの設計と実装を担当

Equipment.gd と EquipmentManager.gd を生成する
"""

from .base_agent import BaseAgent


class EquipmentAgent(BaseAgent):
    """
    装備システムを担当するエージェント

    責務:
    - 装備アイテムの設計
    - 装備スロット管理
    - 装備効果の計算
    """

    def __init__(self, blackboard):
        super().__init__("EquipmentAgent", blackboard, "Equipment System Designer")

    def think(self) -> None:
        """装備システムの設計と実装"""
        if self._gdscript_generated:
            return

        if not self._initialized:
            self._initialize()

        # GDScriptを生成
        self._generate_equipment_script()
        self._generate_equipment_manager_script()

        # 完了を通知
        self.broadcast("装備システムのGDScriptを生成しました")
        self.update_task("equipment_system", "completed", "Equipment.gd and EquipmentManager.gd generated")

    def _initialize(self) -> None:
        """初期化処理"""
        self.logger.info("Initializing EquipmentAgent...")

        self.record_decision(
            "装備システムの設計",
            "武器・防具・アクセサリーの3スロット制。"
            "装備による能力値ボーナスと特殊効果を実装。"
        )

        self.update_task("equipment_system", "in_progress", "Designing equipment system")
        self._initialized = True

    def _generate_equipment_script(self) -> None:
        """Equipment.gd を生成"""
        script = '''# Equipment.gd
# 装備アイテムクラス

extends Resource
class_name Equipment

enum EquipmentType {
\tWEAPON,      # 武器
\tARMOR,       # 防具
\tACCESSORY    # アクセサリー
}

enum Rarity {
\tCOMMON,      # コモン
\tUNCOMMON,    # アンコモン
\tRARE,        # レア
\tEPIC,        # エピック
\tLEGENDARY    # レジェンダリー
}

var equipment_name: String = ""
var equipment_type: EquipmentType = EquipmentType.WEAPON
var rarity: Rarity = Rarity.COMMON

# ステータスボーナス
var bonus_hp: int = 0
var bonus_attack: int = 0
var bonus_defense: int = 0
var bonus_magic: int = 0
var bonus_speed: int = 0

# 特殊効果
var special_effects: Array[String] = []
var description: String = ""

func _init(name: String = "Equipment", type: EquipmentType = EquipmentType.WEAPON):
\tequipment_name = name
\tequipment_type = type

# レアリティによる倍率を取得
func get_rarity_multiplier() -> float:
\tmatch rarity:
\t\tRarity.COMMON:
\t\t\treturn 1.0
\t\tRarity.UNCOMMON:
\t\t\treturn 1.2
\t\tRarity.RARE:
\t\t\treturn 1.5
\t\tRarity.EPIC:
\t\t\treturn 2.0
\t\tRarity.LEGENDARY:
\t\t\treturn 3.0
\t\t_:
\t\t\treturn 1.0

# レアリティ名を取得
func get_rarity_name() -> String:
\tmatch rarity:
\t\tRarity.COMMON:
\t\t\treturn "Common"
\t\tRarity.UNCOMMON:
\t\t\treturn "Uncommon"
\t\tRarity.RARE:
\t\t\treturn "Rare"
\t\tRarity.EPIC:
\t\t\treturn "Epic"
\t\tRarity.LEGENDARY:
\t\t\treturn "Legendary"
\t\t_:
\t\t\treturn "Unknown"

# 装備タイプ名を取得
func get_type_name() -> String:
\tmatch equipment_type:
\t\tEquipmentType.WEAPON:
\t\t\treturn "Weapon"
\t\tEquipmentType.ARMOR:
\t\t\treturn "Armor"
\t\tEquipmentType.ACCESSORY:
\t\t\treturn "Accessory"
\t\t_:
\t\t\treturn "Unknown"

# 装備の総合パワーを計算
func get_total_power() -> int:
\tvar power = bonus_hp + bonus_attack * 2 + bonus_defense + bonus_magic + bonus_speed
\tpower = int(power * get_rarity_multiplier())
\treturn power

# 装備情報を取得
func get_info() -> String:
\tvar info = "【%s】 [%s]\\n" % [equipment_name, get_rarity_name()]
\tinfo += "Type: %s\\n" % get_type_name()
\tinfo += "\\nBonus Stats:\\n"
\t
\tif bonus_hp > 0:
\t\tinfo += "  HP: +%d\\n" % bonus_hp
\tif bonus_attack > 0:
\t\tinfo += "  ATK: +%d\\n" % bonus_attack
\tif bonus_defense > 0:
\t\tinfo += "  DEF: +%d\\n" % bonus_defense
\tif bonus_magic > 0:
\t\tinfo += "  MAG: +%d\\n" % bonus_magic
\tif bonus_speed > 0:
\t\tinfo += "  SPD: +%d\\n" % bonus_speed
\t
\tif special_effects.size() > 0:
\t\tinfo += "\\nSpecial Effects:\\n"
\t\tfor effect in special_effects:
\t\t\tinfo += "  - %s\\n" % effect
\t
\tif description != "":
\t\tinfo += "\\n%s" % description
\t
\treturn info

# 特殊効果を持っているか
func has_effect(effect_name: String) -> bool:
\treturn special_effects.has(effect_name)

# 特殊効果を追加
func add_effect(effect_name: String) -> void:
\tif not has_effect(effect_name):
\t\tspecial_effects.append(effect_name)
'''

        self.save_gdscript(
            "game/scripts/Equipment.gd",
            script,
            "Equipment item class with stats bonuses and special effects"
        )

    def _generate_equipment_manager_script(self) -> None:
        """EquipmentManager.gd を生成"""
        script = '''# EquipmentManager.gd
# 装備管理システム

extends Node
class_name EquipmentManager

# プリセット装備データベース
var equipment_database: Dictionary = {}

func _ready():
\t_initialize_equipment()

# 装備データベースを初期化
func _initialize_equipment() -> void:
\t# === 武器 ===
\t
\t# コモン武器
\tvar iron_sword = Equipment.new("Iron Sword", Equipment.EquipmentType.WEAPON)
\tiron_sword.rarity = Equipment.Rarity.COMMON
\tiron_sword.bonus_attack = 5
\tiron_sword.description = "基本的な鉄剣"
\tequipment_database["iron_sword"] = iron_sword
\t
\tvar wooden_staff = Equipment.new("Wooden Staff", Equipment.EquipmentType.WEAPON)
\twooden_staff.rarity = Equipment.Rarity.COMMON
\twooden_staff.bonus_magic = 5
\twooden_staff.description = "魔法使い用の杖"
\tequipment_database["wooden_staff"] = wooden_staff
\t
\t# レア武器
\tvar steel_blade = Equipment.new("Steel Blade", Equipment.EquipmentType.WEAPON)
\tsteel_blade.rarity = Equipment.Rarity.RARE
\tsteel_blade.bonus_attack = 12
\tsteel_blade.bonus_speed = 3
\tsteel_blade.add_effect("Critical +10%")
\tsteel_blade.description = "鋭い鋼の刃"
\tequipment_database["steel_blade"] = steel_blade
\t
\tvar fire_staff = Equipment.new("Fire Staff", Equipment.EquipmentType.WEAPON)
\tfire_staff.rarity = Equipment.Rarity.RARE
\tfire_staff.bonus_magic = 15
\tfire_staff.bonus_attack = 3
\tfire_staff.add_effect("Fire Damage +20%")
\tfire_staff.description = "炎の魔力を宿した杖"
\tequipment_database["fire_staff"] = fire_staff
\t
\t# レジェンダリー武器
\tvar excalibur = Equipment.new("Excalibur", Equipment.EquipmentType.WEAPON)
\texcalibur.rarity = Equipment.Rarity.LEGENDARY
\texcalibur.bonus_attack = 25
\texcalibur.bonus_defense = 10
\texcalibur.bonus_speed = 5
\texcalibur.add_effect("Holy Damage")
\texcalibur.add_effect("Auto-Regeneration")
\texcalibur.description = "伝説の聖剣"
\tequipment_database["excalibur"] = excalibur
\t
\t# === 防具 ===
\t
\t# コモン防具
\tvar leather_armor = Equipment.new("Leather Armor", Equipment.EquipmentType.ARMOR)
\tleather_armor.rarity = Equipment.Rarity.COMMON
\tleather_armor.bonus_defense = 5
\tleather_armor.bonus_hp = 10
\tleather_armor.description = "基本的な革鎧"
\tequipment_database["leather_armor"] = leather_armor
\t
\t# レア防具
\tvar plate_armor = Equipment.new("Plate Armor", Equipment.EquipmentType.ARMOR)
\tplate_armor.rarity = Equipment.Rarity.RARE
\tplate_armor.bonus_defense = 15
\tplate_armor.bonus_hp = 30
\tplate_armor.add_effect("Physical Resistance +10%")
\tplate_armor.description = "頑丈な板金鎧"
\tequipment_database["plate_armor"] = plate_armor
\t
\tvar mystic_robe = Equipment.new("Mystic Robe", Equipment.EquipmentType.ARMOR)
\tmystic_robe.rarity = Equipment.Rarity.RARE
\tmystic_robe.bonus_defense = 8
\tmystic_robe.bonus_magic = 10
\tmystic_robe.bonus_hp = 15
\tmystic_robe.add_effect("Magic Resistance +15%")
\tmystic_robe.description = "魔力を纏ったローブ"
\tequipment_database["mystic_robe"] = mystic_robe
\t
\t# === アクセサリー ===
\t
\t# コモンアクセサリー
\tvar bronze_ring = Equipment.new("Bronze Ring", Equipment.EquipmentType.ACCESSORY)
\tbronze_ring.rarity = Equipment.Rarity.COMMON
\tbronze_ring.bonus_hp = 5
\tbronze_ring.description = "シンプルな銅の指輪"
\tequipment_database["bronze_ring"] = bronze_ring
\t
\t# レアアクセサリー
\tvar speed_boots = Equipment.new("Speed Boots", Equipment.EquipmentType.ACCESSORY)
\tspeed_boots.rarity = Equipment.Rarity.RARE
\tspeed_boots.bonus_speed = 10
\tspeed_boots.add_effect("First Strike")
\tspeed_boots.description = "素早く動ける靴"
\tequipment_database["speed_boots"] = speed_boots
\t
\tvar power_gauntlet = Equipment.new("Power Gauntlet", Equipment.EquipmentType.ACCESSORY)
\tpower_gauntlet.rarity = Equipment.Rarity.RARE
\tpower_gauntlet.bonus_attack = 8
\tpower_gauntlet.bonus_defense = 5
\tpower_gauntlet.add_effect("Knockback")
\tpower_gauntlet.description = "力を増幅する篭手"
\tequipment_database["power_gauntlet"] = power_gauntlet
\t
\tprint("Equipment database initialized with %d items" % equipment_database.size())

# 装備を取得
func get_equipment(equipment_id: String) -> Equipment:
\tif equipment_database.has(equipment_id):
\t\treturn equipment_database[equipment_id]
\treturn null

# 冒険者に装備を装着
func equip_to_adventurer(adventurer: Adventurer, equipment: Equipment) -> bool:
\tif equipment == null:
\t\treturn false
\t
\t# 装備ボーナスを適用
\tadventurer.max_hp += equipment.bonus_hp
\tadventurer.current_hp += equipment.bonus_hp
\tadventurer.attack += equipment.bonus_attack
\tadventurer.defense += equipment.bonus_defense
\tadventurer.magic += equipment.bonus_magic
\tadventurer.speed += equipment.bonus_speed
\t
\tprint("%s equipped %s" % [adventurer.adventurer_name, equipment.equipment_name])
\treturn true

# 職業に推奨される装備を取得
func get_recommended_equipment(job_type: JobClass.Type) -> Dictionary:
\tvar recommended = {
\t\t"weapon": null,
\t\t"armor": null,
\t\t"accessory": null
\t}
\t
\tmatch job_type:
\t\tJobClass.Type.WARRIOR:
\t\t\trecommended["weapon"] = get_equipment("steel_blade")
\t\t\trecommended["armor"] = get_equipment("plate_armor")
\t\t\trecommended["accessory"] = get_equipment("power_gauntlet")
\t\t
\t\tJobClass.Type.MAGE:
\t\t\trecommended["weapon"] = get_equipment("fire_staff")
\t\t\trecommended["armor"] = get_equipment("mystic_robe")
\t\t\trecommended["accessory"] = get_equipment("bronze_ring")
\t\t
\t\tJobClass.Type.PRIEST:
\t\t\trecommended["weapon"] = get_equipment("wooden_staff")
\t\t\trecommended["armor"] = get_equipment("mystic_robe")
\t\t\trecommended["accessory"] = get_equipment("bronze_ring")
\t\t
\t\tJobClass.Type.THIEF:
\t\t\trecommended["weapon"] = get_equipment("steel_blade")
\t\t\trecommended["armor"] = get_equipment("leather_armor")
\t\t\trecommended["accessory"] = get_equipment("speed_boots")
\t\t
\t\tJobClass.Type.ARCHER:
\t\t\trecommended["weapon"] = get_equipment("iron_sword")
\t\t\trecommended["armor"] = get_equipment("leather_armor")
\t\t\trecommended["accessory"] = get_equipment("speed_boots")
\t
\treturn recommended

# レアリティでフィルタ
func get_equipment_by_rarity(rarity: Equipment.Rarity) -> Array[Equipment]:
\tvar filtered: Array[Equipment] = []
\tfor equipment_id in equipment_database:
\t\tvar equipment = equipment_database[equipment_id]
\t\tif equipment.rarity == rarity:
\t\t\tfiltered.append(equipment)
\treturn filtered

# タイプでフィルタ
func get_equipment_by_type(equipment_type: Equipment.EquipmentType) -> Array[Equipment]:
\tvar filtered: Array[Equipment] = []
\tfor equipment_id in equipment_database:
\t\tvar equipment = equipment_database[equipment_id]
\t\tif equipment.equipment_type == equipment_type:
\t\t\tfiltered.append(equipment)
\treturn filtered

# 装備一覧を表示
func list_all_equipment() -> String:
\tvar list = "=== Equipment Database ===\\n"
\tfor equipment_id in equipment_database:
\t\tvar equipment = equipment_database[equipment_id]
\t\tlist += "- %s [%s] (%s)\\n" % [equipment.equipment_name, equipment.get_rarity_name(), equipment.get_type_name()]
\treturn list
'''

        self.save_gdscript(
            "game/scripts/EquipmentManager.gd",
            script,
            "Equipment management system with item database and equip functionality"
        )
