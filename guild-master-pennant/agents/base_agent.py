"""
BaseAgent - すべてのエージェントの基底クラス

自律的に動作し、Blackboardを通じて他のエージェントと協調する
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAgent(ABC):
    """
    エージェントの基底クラス

    すべてのエージェントはこのクラスを継承し、think()メソッドを実装する
    """

    def __init__(self, name: str, blackboard, role: str = ""):
        self.name = name
        self.blackboard = blackboard
        self.role = role
        self.logger = logging.getLogger(name)

        self._active = False
        self._should_stop = False
        self._last_message_id = -1
        self._initialized = False
        self._gdscript_generated = False

        # エージェント固有の状態
        self._state: Dict[str, Any] = {}

    def start(self) -> None:
        """エージェントを起動"""
        if self._active:
            self.logger.warning(f"{self.name} is already active")
            return

        self._active = True
        self._should_stop = False
        self.logger.info(f"{self.name} started")

    def stop(self) -> None:
        """エージェントを停止"""
        self._should_stop = True
        self._active = False
        self.logger.info(f"{self.name} stopped")

    def is_active(self) -> bool:
        """エージェントがアクティブか"""
        return self._active

    def run_once(self) -> None:
        """think()を1回だけ実行"""
        if not self._active:
            self.start()

        try:
            self.think()
        except Exception as e:
            self.logger.error(f"Error in think(): {e}", exc_info=True)

    def run_loop(self, duration: Optional[float] = None) -> None:
        """
        エージェントのメインループ

        Args:
            duration: 実行時間（秒）。Noneの場合は停止されるまで実行
        """
        start_time = time.time()

        while not self._should_stop:
            try:
                # メッセージを処理
                self._process_messages()

                # 思考ロジックを実行
                self.think()

                # 期間指定がある場合はチェック
                if duration is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= duration:
                        self.logger.info(f"{self.name} reached duration limit")
                        break

                # 短い休止
                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in run_loop: {e}", exc_info=True)
                time.sleep(1.0)

        self._active = False
        self.logger.info(f"{self.name} loop ended")

    def _process_messages(self) -> None:
        """Blackboardから新しいメッセージを取得して処理"""
        messages = self.blackboard.get_messages(
            recipient=self.name,
            since_id=self._last_message_id
        )

        for msg in messages:
            if msg["id"] > self._last_message_id:
                self._last_message_id = msg["id"]
                self.on_message(msg)

    def on_message(self, message: Dict) -> None:
        """
        メッセージ受信時のハンドラ

        サブクラスでオーバーライドして独自の処理を追加可能
        """
        self.logger.debug(f"Received message from {message['sender']}: {message['content'][:50]}")

    @abstractmethod
    def think(self) -> None:
        """
        エージェントの思考ロジック

        サブクラスで必ず実装する必要がある
        """
        pass

    def send_message(self, recipient: str, content: str,
                    message_type: str = "info", metadata: Optional[Dict] = None) -> None:
        """
        他のエージェントにメッセージを送信

        Args:
            recipient: 受信者のエージェント名
            content: メッセージ内容
            message_type: メッセージタイプ
            metadata: 追加のメタデータ
        """
        self.blackboard.post_message(
            sender=self.name,
            recipient=recipient,
            content=content,
            message_type=message_type,
            metadata=metadata
        )

    def broadcast(self, content: str, message_type: str = "info") -> None:
        """全エージェントにブロードキャスト"""
        self.send_message("all", content, message_type)

    def set_state(self, key: str, value: Any) -> None:
        """エージェント固有の状態を設定"""
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """エージェント固有の状態を取得"""
        return self._state.get(key, default)

    def save_gdscript(self, filepath: str, content: str, description: str = "") -> None:
        """
        生成したGDScriptをBlackboardに保存

        Args:
            filepath: ファイルパス
            content: GDScriptの内容
            description: ファイルの説明
        """
        self.blackboard.add_generated_file(
            filepath=filepath,
            content=content,
            agent=self.name,
            description=description
        )
        self._gdscript_generated = True
        self.logger.info(f"Generated GDScript: {filepath}")

    def record_decision(self, decision: str, rationale: str) -> None:
        """
        設計決定を記録

        Args:
            decision: 決定内容
            rationale: 決定理由
        """
        self.blackboard.add_decision(
            agent=self.name,
            decision=decision,
            rationale=rationale
        )

    def update_task(self, task_name: str, status: str, details: str = "") -> None:
        """
        タスクのステータスを更新

        Args:
            task_name: タスク名
            status: ステータス (pending, in_progress, completed, failed)
            details: 詳細情報
        """
        self.blackboard.set_task_status(
            task_name=task_name,
            status=status,
            agent=self.name,
            details=details
        )

    def get_status(self) -> Dict[str, Any]:
        """
        エージェントの状態を取得

        Returns:
            状態情報の辞書
        """
        return {
            "name": self.name,
            "role": self.role,
            "active": self._active,
            "initialized": self._initialized,
            "gdscript_generated": self._gdscript_generated,
            "state": dict(self._state)
        }
