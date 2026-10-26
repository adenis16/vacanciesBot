from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton
import sys
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Агент поиска вакансий")
        label1 = QLabel("Поиск вакансий")

        layout = QVBoxLayout()

        postion_input = QLineEdit()
        postion_input.text()
        
        search_button = QPushButton("Найти вакансии")

        label2 = QLabel("Профиль кандидата")
        label3 = QLabel("Настройки")

        layout.addWidget(label1)
        layout.addWidget(postion_input)
        layout.addWidget(search_button)
        layout.addWidget(label2)
        layout.addWidget(label3)
        

        self.setLayout(layout)


        



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()