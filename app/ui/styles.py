class AppStyles:

    MAIN_STYLE = """

/* =========================================================
   GLOBAL
   ========================================================= */

QWidget {

    background-color: #111315;
    color: #e7e9ec;

    font-family: "Segoe UI";
    font-size: 13px;

}


/* =========================================================
   MAIN AREA
   ========================================================= */

QWidget#mainArea {

    background-color: #151719;

}


/* =========================================================
   HEADER
   ========================================================= */

QWidget#header {

    background-color: #151719;

    border-bottom: 1px solid #292d32;

}


/* =========================================================
   SIDEBAR
   ========================================================= */

QWidget#sidebar {

    background-color: #101214;

    border-right: 1px solid #292d32;

}


/* =========================================================
   BUTTONS
   ========================================================= */

QPushButton {

    background-color: #1b1e22;

    color: #dfe3e8;

    border: 1px solid #292d32;

    border-radius: 8px;

    padding: 9px 12px;

    font-size: 13px;

}


QPushButton:hover {

    background-color: #24282d;

    border-color: #3a4047;

}


QPushButton:pressed {

    background-color: #191c20;

}


QPushButton:disabled {

    background-color: #181a1d;

    color: #686d74;

    border-color: #24272b;

}


/* =========================================================
   PRIMARY BUTTON
   ========================================================= */

QPushButton#sendButton {

    background-color: #3b82f6;

    color: white;

    border: none;

    border-radius: 8px;

    padding: 9px 16px;

    font-weight: 600;

}


QPushButton#sendButton:hover {

    background-color: #4b8ff7;

}


QPushButton#sendButton:pressed {

    background-color: #326fd1;

}


QPushButton#sendButton:disabled {

    background-color: #26354d;

    color: #7d8ca5;

}


/* =========================================================
   INPUT
   ========================================================= */

QLineEdit {

    background-color: #191c20;

    color: #e7e9ec;

    border: 1px solid #30353b;

    border-radius: 8px;

    padding: 10px 12px;

    selection-background-color: #3b82f6;

    selection-color: white;

}


QLineEdit:hover {

    border-color: #3a4149;

}


QLineEdit:focus {

    border-color: #3b82f6;

    background-color: #1b1e22;

}


QLineEdit:disabled {

    color: #686d74;

    background-color: #151719;

}


/* =========================================================
   MESSAGE COMPOSER
   ========================================================= */

QFrame#composer {

    background-color: #191c20;

    border: 1px solid #30353b;

    border-radius: 12px;

}


QFrame#composer QLineEdit {

    background-color: transparent;

    border: none;

    padding: 9px 10px;

}


QFrame#composer QLineEdit:focus {

    background-color: transparent;

    border: none;

}


/* =========================================================
   STATUS
   ========================================================= */

QLabel#statusLabel {

    color: #7f8791;

    font-size: 12px;

    padding-left: 4px;

}


/* =========================================================
   LABELS
   ========================================================= */

QLabel {

    color: #e7e9ec;

}


/* =========================================================
   LISTS
   ========================================================= */

QListWidget {

    background-color: #111315;

    color: #dfe3e8;

    border: none;

    outline: none;

}


QListWidget::item {

    background-color: transparent;

    border-radius: 7px;

    padding: 9px 10px;

    margin: 2px 4px;

}


QListWidget::item:hover {

    background-color: #1d2024;

}


QListWidget::item:selected {

    background-color: #24282d;

    color: white;

}


/* =========================================================
   SCROLL AREAS
   ========================================================= */

QScrollArea {

    background-color: transparent;

    border: none;

}


QScrollArea > QWidget > QWidget {

    background-color: transparent;

}


/* =========================================================
   SCROLLBAR
   ========================================================= */

QScrollBar:vertical {

    background: transparent;

    width: 8px;

    margin: 4px 0 4px 0;

}


QScrollBar::handle:vertical {

    background: #343a41;

    border-radius: 4px;

    min-height: 30px;

}


QScrollBar::handle:vertical:hover {

    background: #464d55;

}


QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {

    height: 0px;

}


QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {

    background: transparent;

}


/* =========================================================
   HORIZONTAL SCROLLBAR
   ========================================================= */

QScrollBar:horizontal {

    background: transparent;

    height: 8px;

}


QScrollBar::handle:horizontal {

    background: #343a41;

    border-radius: 4px;

    min-width: 30px;

}


QScrollBar::handle:horizontal:hover {

    background: #464d55;

}


QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {

    width: 0px;

}


QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {

    background: transparent;

}


/* =========================================================
   COMBO BOX
   ========================================================= */

QComboBox {

    background-color: #191c20;

    color: #e7e9ec;

    border: 1px solid #30353b;

    border-radius: 8px;

    padding: 8px 10px;

}


QComboBox:hover {

    border-color: #3a4149;

}


QComboBox:focus {

    border-color: #3b82f6;

}


QComboBox QAbstractItemView {

    background-color: #191c20;

    color: #e7e9ec;

    border: 1px solid #30353b;

    selection-background-color: #24282d;

    selection-color: white;

}


/* =========================================================
   TEXT EDIT
   ========================================================= */

QTextEdit {

    background-color: #191c20;

    color: #e7e9ec;

    border: 1px solid #30353b;

    border-radius: 8px;

    padding: 10px;

    selection-background-color: #3b82f6;

    selection-color: white;

}


QTextEdit:focus {

    border-color: #3b82f6;

}

"""