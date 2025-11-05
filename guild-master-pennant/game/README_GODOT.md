# Guild Master Pennant - Godot プロジェクト

**Godot Engine 4.2+ で動作するファンタジーRPGシミュレーションゲーム**

---

## 🚀 クイックスタート

### 1. Godot Engineのインストール

[Godot Engine 4.2以降](https://godotengine.org/download) をダウンロードしてインストールしてください。

### 2. プロジェクトを開く

1. Godot Engineを起動
2. 「インポート」ボタンをクリック
3. このフォルダ（`game/`）内の `project.godot` を選択
4. 「インポートして編集」をクリック

### 3. ゲームを実行

- **F5キー** または 画面右上の「▶」ボタンでゲームを実行
- タイトル画面が表示されます

---

## 🎮 操作方法

### タイトル画面

- **ゲーム開始**: テスト戦闘に進む（現在はテスト戦闘のみ実装）
- **テスト戦闘**: 戦闘システムのテスト
- **終了**: ゲームを終了

### テスト戦闘画面

- **次のターン**: 1ターン進める
- **自動戦闘**: 自動で戦闘を進める（勝敗がつくまで）
- **タイトルに戻る**: タイトル画面に戻る

---

## 📁 プロジェクト構造

```
game/
├── project.godot          # Godotプロジェクト設定
├── icon.svg               # プロジェクトアイコン
├── scenes/                # シーンファイル
│   ├── Main.tscn          # タイトル画面
│   ├── Main.gd
│   ├── TestBattle.tscn    # テスト戦闘画面
│   └── TestBattle.gd
└── scripts/               # GDScriptファイル
    ├── Adventurer.gd      # 冒険者クラス
    ├── JobClass.gd        # 職業定義
    ├── CombatManager.gd   # 戦闘管理
    ├── CombatAction.gd    # 戦闘アクション
    ├── TacticsSystem.gd   # 戦術システム
    ├── TacticsCondition.gd
    ├── PartyManager.gd    # パーティ管理
    ├── SkillSystem.gd     # スキルシステム
    ├── Skill.gd
    ├── DungeonManager.gd  # ダンジョン管理
    ├── EnemyGenerator.gd  # 敵生成
    └── EnemyBehavior.gd   # 敵の振る舞い
```

---

## 🎯 実装されている機能

### ✅ 完成しているシステム

1. **冒険者システム**
   - 5つの職業（戦士、魔法使い、僧侶、盗賊、弓使い）
   - 能力値（HP、攻撃、防御、魔力、速度）
   - 隊列システム（前列3人・後列1人）

2. **戦闘システム**
   - ターン制自動戦闘
   - 速度順行動
   - ダメージ計算
   - 被弾率に基づくターゲット選択

3. **テスト戦闘**
   - 4人パーティ vs 2体の敵
   - リアルタイム戦闘ログ
   - パーティ・敵の状態表示
   - 自動戦闘モード

### 🚧 今後実装予定

- **戦術システムの統合**: 条件分岐行動
- **スキルシステムの統合**: パワプロ特能風スキル
- **ダンジョン踏破モード**: 連続戦闘と階層管理
- **パーティ編成画面**: 職業選択とカスタマイズ
- **ペナント要素**: ドラフト、スカウト、トレード

---

## 🔧 開発者向け情報

### GDScriptの編集

すべてのゲームロジックは `scripts/` ディレクトリ内のGDScriptファイルに実装されています。

- **Godotエディタ内で編集**: 各ファイルをダブルクリックで開く
- **外部エディタで編集**: VS CodeなどでGDScriptを編集可能

### 新しいシーンの追加

1. Godotエディタで「シーン」→「新しいシーン」
2. ルートノードを選択（Control, Node2D, Node3Dなど）
3. スクリプトをアタッチ
4. UIノードを配置
5. シーンを保存（`.tscn`ファイル）

### デバッグ

- **F6キー**: 現在のシーンを実行
- **Ctrl+B**: スクリプトエラーのチェック
- `print()` 関数でログ出力（下部の「出力」タブに表示）

---

## 🐛 トラブルシューティング

### エラー: "Failed to load resource"

→ ファイルパスが正しいか確認してください。Godotでは `res://` から始まる相対パスを使用します。

### エラー: "Parse error"

→ GDScriptの構文エラーです。エディタ下部の「エラー」タブで詳細を確認してください。

### シーンが表示されない

→ `project.godot` の `run/main_scene` が正しく設定されているか確認してください。

---

## 📝 ゲームシステム詳細

### 職業データ

| 職業 | HP | 攻撃 | 防御 | 魔力 | 速度 |
|------|-----|------|------|------|------|
| 戦士 | 100 | 15 | 12 | 3 | 8 |
| 魔法使い | 60 | 5 | 5 | 20 | 10 |
| 僧侶 | 70 | 7 | 8 | 15 | 9 |
| 盗賊 | 75 | 12 | 7 | 5 | 18 |
| 弓使い | 80 | 13 | 8 | 6 | 12 |

### 隊列システム

```
前列: [1] [2] [3]  ← 被弾率 20% ずつ、攻撃力 +10%
後列:     [4]      ← 被弾率 10%、防御力 +10%
```

### ダメージ計算

```
ダメージ = 攻撃力 - (防御力 / 2)
ランダム要素: 90% ~ 110%
最低ダメージ: 1
```

---

## 🎨 カスタマイズ

### 色の変更

`scenes/Main.tscn` や `scenes/TestBattle.tscn` の ColorRect ノードの色を変更できます。

### フォントサイズの変更

各Labelノードの `theme_override_font_sizes/font_size` プロパティで調整できます。

### ウィンドウサイズの変更

`project.godot` の `[display]` セクションで変更できます：

```
window/size/viewport_width=1280
window/size/viewport_height=720
```

---

## 📚 参考リンク

- [Godot Engine 公式ドキュメント](https://docs.godotengine.org/)
- [GDScript 入門](https://docs.godotengine.org/ja/stable/tutorials/scripting/gdscript/gdscript_basics.html)
- [Guild Master Pennant GitHub](https://github.com/gaku548/AgentDev/tree/main/guild-master-pennant)

---

**Developed by Multi-Agent Autonomous System**

このゲームは6つの専門エージェントが協調して自律的に開発しました。
