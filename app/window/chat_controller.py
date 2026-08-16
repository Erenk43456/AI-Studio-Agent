from PySide6.QtCore import QTimer

from app.worker import AIWorker

from app.chat_widget import (
    MessageBubble,
    AIThinkingBubble
)


class ChatController:

    @staticmethod
    def connect(window):

        window.input.returnPressed.connect(
            window.send_message
        )

        window.button.clicked.connect(
            window.send_message
        )

    # =========================================================
    # MESSAGE
    # =========================================================

    @staticmethod
    def add_message(
        window,
        text,
        user
    ):

        bubble = MessageBubble(
            text,
            user
        )

        window.chat_layout.addWidget(
            bubble
        )

        ChatController.scroll_to_bottom(
            window
        )

    # =========================================================
    # AI THINKING
    # =========================================================

    @staticmethod
    def show_thinking(window):

        ChatController.hide_thinking(
            window
        )

        window.thinking_bubble = (
            AIThinkingBubble()
        )

        window.chat_layout.addWidget(
            window.thinking_bubble
        )

        ChatController.scroll_to_bottom(
            window
        )

    @staticmethod
    def update_thinking_stage(
        window,
        stage
    ):

        bubble = getattr(
            window,
            "thinking_bubble",
            None
        )

        if not bubble:

            return

        bubble.update_stage(
            stage
        )

        ChatController.scroll_to_bottom(
            window
        )

    @staticmethod
    def hide_thinking(window):

        bubble = getattr(
            window,
            "thinking_bubble",
            None
        )

        if bubble:

            bubble.deleteLater()

            window.thinking_bubble = None

    # =========================================================
    # SCROLL
    # =========================================================

    @staticmethod
    def scroll_to_bottom(window):

        QTimer.singleShot(
            30,
            lambda:
            window.scroll.verticalScrollBar().setValue(
                window.scroll.verticalScrollBar().maximum()
            )
        )

    # =========================================================
    # SEND MESSAGE
    # =========================================================

    @staticmethod
    def send_message(window):

        if window.busy:

            return

        message = (
            window.input
            .text()
            .strip()
        )

        if not message:

            return

        chat = (
            window.chat_manager.get_chat(
                window.current_chat
            )
        )

        if not chat:

            return

        # =====================================================
        # AUTO RENAME
        # =====================================================

        if (
            chat.title == "New Chat"
            or chat.title.startswith("Chat")
        ):

            chat.rename(
                message
            )

            window.chat_manager.save()

            from app.window.sidebar_controller import (
                SidebarController
            )

            SidebarController.refresh_chat_list(
                window
            )

        # =====================================================
        # STATE
        # =====================================================

        window.last_user_message = message

        window.busy = True

        window.button.setEnabled(
            False
        )

        window.input.setEnabled(
            False
        )

        # =====================================================
        # USER MESSAGE
        # =====================================================

        ChatController.add_message(
            window,
            message,
            True
        )

        window.input.clear()

        # =====================================================
        # AI PIPELINE
        # =====================================================

        window.status.setText(
            "● AI Working"
        )

        ChatController.show_thinking(
            window
        )

        # Preparing
        ChatController.update_thinking_stage(
            window,
            0
        )

        # =====================================================
        # WORKER
        # =====================================================

        window.worker = AIWorker(
            window.main_orchestrator,
            chat.conversation,
            message
        )

        window.worker.finished.connect(
            lambda response:
            ChatController.show_response(
                window,
                response
            )
        )

        window.worker.finished.connect(
            window.worker.deleteLater
        )

        # Worker gerçekten başlamadan önce
        # pipeline'ı Thinking aşamasına geçiriyoruz.
        ChatController.update_thinking_stage(
            window,
            1
        )

        window.worker.start()

    # =========================================================
    # RESPONSE
    # =========================================================

    @staticmethod
    def show_response(
        window,
        response
    ):

        # Worker cevap verdiğine göre
        # artık response generation tamamlanıyor.
        ChatController.update_thinking_stage(
            window,
            2
        )

        QTimer.singleShot(
            150,
            lambda:
            ChatController.complete_response(
                window,
                response
            )
        )

    # =========================================================
    # COMPLETE
    # =========================================================

    @staticmethod
    def complete_response(
        window,
        response
    ):

        ChatController.update_thinking_stage(
            window,
            3
        )

        QTimer.singleShot(
            200,
            lambda:
            ChatController.finish_response(
                window,
                response
            )
        )

    # =========================================================
    # FINISH
    # =========================================================

    @staticmethod
    def finish_response(
        window,
        response
    ):

        ChatController.hide_thinking(
            window
        )

        chat = (
            window.chat_manager.get_chat(
                window.current_chat
            )
        )

        if chat:

            chat.conversation.add(
                window.last_user_message,
                response
            )

        # =====================================================
        # AI RESPONSE
        # =====================================================

        ChatController.add_message(
            window,
            response,
            False
        )

        # =====================================================
        # STATE
        # =====================================================

        window.status.setText(
            "● Ready"
        )

        window.busy = False

        window.button.setEnabled(
            True
        )

        window.input.setEnabled(
            True
        )

        window.input.setFocus()

        ChatController.scroll_to_bottom(
            window
        )