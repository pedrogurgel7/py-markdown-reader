import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QPlainTextEdit, QFileDialog, QToolBar
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
import markdown

from pygments.formatters import HtmlFormatter

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Reader & PDF Export")
        self.resize(1200, 800)

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self.export_pdf_action = QAction("Export to PDF", self)
        self.export_pdf_action.triggered.connect(self.export_to_pdf)
        self.toolbar.addAction(self.export_pdf_action)

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Type regular Markdown here...")
        self.editor.textChanged.connect(self.schedule_update)
        self.splitter.addWidget(self.editor)

        # Preview
        self.preview = QWebEngineView()
        self.splitter.addWidget(self.preview)

        # Set initial splitter sizes (50/50)
        self.splitter.setSizes([600, 600])

        # Debounce timer for updating preview
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300)  # 300ms debounce
        self.update_timer.timeout.connect(self.update_preview)

        # Initial CSS
        pygment_css = HtmlFormatter(style='friendly').get_style_defs('.codehilite')
        self.css = f"""
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji"; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; color: #24292e; }}
            code {{ background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 85%; }}
            pre {{ background-color: #f6f8fa; padding: 16px; border-radius: 3px; overflow: auto; }}
            pre code {{ background-color: transparent; padding: 0; }}
            h1, h2, h3, h4, h5, h6 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }}
            h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            blockquote {{ border-left: 0.25em solid #dfe2e5; color: #6a737d; padding: 0 1em; margin: 0; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 0; margin-bottom: 16px; }}
            table th, table td {{ padding: 6px 13px; border: 1px solid #dfe2e5; }}
            table tr:nth-child(2n) {{ background-color: #f6f8fa; }}
            /* Pygments CSS */
            {pygment_css}
        </style>
        """

    def schedule_update(self):
        self.update_timer.start()

    def update_preview(self):
        text = self.editor.toPlainText()
        html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
        full_html = f"<!DOCTYPE html><html><head>{self.css}</head><body>{html_content}</body></html>"
        self.preview.setHtml(full_html)

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if file_path:
            # QWebEngineView's printToPdf requires a callback or works asynchronously
            self.preview.page().printToPdf(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.show()
    sys.exit(app.exec())
