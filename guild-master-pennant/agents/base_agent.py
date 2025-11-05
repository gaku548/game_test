"""
Base Agent - エージェントの基底クラス

すべての専門エージェントが継承する基底クラス。
自律的な思考とBlackboardとの連携機能を提供。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import time


class BaseAgent(ABC):
    """
    エージェントの基底クラス

    各エージェントは自律的に think() メソッドを実行し、
    Blackboard を通じて他のエージェントと協調する。
    """

    def __init__(self, name: str, blackboard, role: str = ""):
        """
        Args:
            name: エージェント名
            blackboard: Blackboardインスタンス
            role: エージェントの役割説明
        """
        self.name = name
        self.blackboard = blackboard
        self.role = role
        self.logger = logging.getLogger(f"Agent.{name}")
        self._last_message_id = -1
        self._is_active = False
        self._thinking_interval = 1.0  # think()の実行間隔（秒）

        # Blackboardにメッセージ通知を登録
        self.blackboard.subscribe(self.name, self._on_message_received)

        self.logger.info(f"Agent '{name}' initialized - Role: {role}")

    def _on_message_received(self, message: Dict) -> None:
        """
        メッセージ受信時のコールバック

        Args:
            message: 受信したメッセージ
        """
        self.logger.debug(f"Received message from {message['sender']}: {message['content'][:50]}...")

    def send_message(self, recipient: str, content: str,
                    message_type: str = "info", metadata: Optional[Dict] = None) -> None:
        """
        他のエージェントにメッセージを送信

        Args:
            recipient: 受信者のエージェント名 ("all" で全員に送信)
            content: メッセージ内容
            message_type: メッセージタイプ (info, request, response, error)
            metadata: 追加のメタデータ
        """
        self.blackboard.post_message(
            sender=self.name,
            recipient=recipient,
            content=content,
            message_type=message_type,
            metadata=metadata
        )
        self.logger.debug(f"Sent message to {recipient}: {content[:50]}...")

    def get_new_messages(self) -> List[Dict]:
        """
        未読メッセージを取得

        Returns:
            新しいメッセージのリスト
        """
        messages = self.blackboard.get_messages(
            recipient=self.name,
            since_id=self._last_message_id
        )

        if messages:
            self._last_message_id = max(m["id"] for m in messages)

        return messages

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
        self.logger.info(f"Decision: {decision}")

    def generate_file(self, filepath: str, content: str, description: str = "") -> None:
        """
        ファイルを生成してBlackboardに記録

        Args:
            filepath: ファイルパス
            content: ファイル内容
            description: ファイルの説明
        """
        # 実際にファイルを書き込む
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Blackboardに記録
            self.blackboard.add_generated_file(
                filepath=filepath,
                content=content,
                agent=self.name,
                description=description
            )
            self.logger.info(f"Generated file: {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to generate file {filepath}: {e}")
            raise

    def update_task_status(self, task_name: str, status: str, details: str = "") -> None:
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
        self.logger.info(f"Task '{task_name}' status: {status}")

    @abstractmethod
    def think(self) -> None:
        """
        エージェントの自律的な思考と行動

        このメソッドは定期的に呼ばれ、エージェントが:
        1. 新しいメッセージをチェック
        2. 現在のタスクを確認
        3. 必要な作業を実行
        4. 他のエージェントと協調
        する。

        各専門エージェントで実装する。
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        エージェントの現在の状態を取得

        Returns:
            状態情報の辞書
        """
        pass

    def start(self) -> None:
        """
        エージェントを起動
        """
        self._is_active = True
        self.logger.info(f"Agent '{self.name}' started")

    def stop(self) -> None:
        """
        エージェントを停止
        """
        self._is_active = False
        self.logger.info(f"Agent '{self.name}' stopped")

    def is_active(self) -> bool:
        """
        エージェントがアクティブかどうか

        Returns:
            True if active
        """
        return self._is_active

    def run_once(self) -> None:
        """
        think()を1回実行（デバッグ用）
        """
        if not self._is_active:
            self.logger.warning(f"Agent '{self.name}' is not active")
            return

        try:
            self.think()
        except Exception as e:
            self.logger.error(f"Error in think(): {e}", exc_info=True)

    def run_loop(self, duration: Optional[float] = None) -> None:
        """
        エージェントのメインループを実行

        Args:
            duration: 実行時間（秒）。Noneの場合は無限ループ
        """
        start_time = time.time()
        self.start()

        try:
            while self._is_active:
                self.run_once()
                time.sleep(self._thinking_interval)

                if duration is not None and (time.time() - start_time) >= duration:
                    break

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.stop()
