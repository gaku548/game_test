extends Control

# Main.gd - Guild Master Pennant メインシーン

# UI要素
@onready var title_label = $VBoxContainer/TitleLabel
@onready var start_button = $VBoxContainer/StartButton
@onready var test_button = $VBoxContainer/TestButton
@onready var quit_button = $VBoxContainer/QuitButton
@onready var info_label = $VBoxContainer/InfoLabel

func _ready():
	print("=== Guild Master Pennant ===")
	print("パワプロペナント風ファンタジーRPGシミュレーション")

	# ボタンの接続
	if start_button:
		start_button.pressed.connect(_on_start_pressed)
	if test_button:
		test_button.pressed.connect(_on_test_pressed)
	if quit_button:
		quit_button.pressed.connect(_on_quit_pressed)

	_update_info()

func _update_info():
	if info_label:
		var info_text = """
システム準備完了:
✅ 5職業 (戦士/魔法使い/僧侶/盗賊/弓使い)
✅ 戦術自動戦闘
✅ 隊列システム (前列3/後列1)
✅ スキルシステム (11種類)
✅ ダンジョン踏破
"""
		info_label.text = info_text

func _on_start_pressed():
	print("ゲーム開始...")
	# TODO: ゲーム本編シーンへ移行
	get_tree().change_scene_to_file("res://scenes/TestBattle.tscn")

func _on_test_pressed():
	print("テスト戦闘開始...")
	get_tree().change_scene_to_file("res://scenes/TestBattle.tscn")

func _on_quit_pressed():
	print("終了します")
	get_tree().quit()
