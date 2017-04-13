import sys
from PyQt5.QtWidgets import QApplication, QFrame, QPushButton, QLabel,\
    QLineEdit, QVBoxLayout, QStackedLayout, QWidget, QTableWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QIntValidator
from PyQt5.QtCore import Qt, QRect
from game import Game


class Window(QFrame):
    def __init__(self):
        super().__init__()

        self.move(350, 100)
        self.setFixedSize(500, 380)

        self.game = Game(15, '')
        self.in_game = False
        self.is_game_finished = False
        self.is_result_saved = False
        self.player = ''
        self.chosen_cubes = set()
        self.setWindowTitle('Cubes')

        self.main_menu = QWidget(self)
        self.game_widget = QWidget(self)
        self.game_widget.setMouseTracking(True)
        self.game_widget.mouseMoveEvent = self.mouse_move_event
        self.records = QWidget(self)
        self.settings = QWidget()

        self.painter = QPainter()

        self.stacked = QStackedLayout(self)
        self.set_table_layout()
        self.set_game_layout()
        self.set_customization_layout()
        self.set_main_menu_layout()
        self.stacked.setCurrentWidget(self.main_menu)

        self.show()

    def mouse_move_event(self, event):
        if self.is_game_finished:
            return

        x_coord, y_coord = self.get_cell_from_event(event)
        self.chosen_cubes = set()

        if not self.is_in_cubes_field(x_coord, y_coord):
            self.repaint()
            return

        cube = self.game.get(x_coord, y_coord)
        if cube:
            the_same = self.game.field.get_the_same(cube)
            if len(the_same) > 1:
                self.chosen_cubes = the_same
        self.repaint()

    def is_in_cubes_field(self, x_coord, y_coord):
        return x_coord < self.game.size and \
               y_coord < self.game.size

    def get_cell_from_event(self, event):
        x_coord = event.x() // self.cube_size
        y_coord = event.y() // self.cube_size
        return x_coord, y_coord

    def mousePressEvent(self, event):
        if self.is_game_finished or not self.in_game:
            return

        x_coord, y_coord = self.get_cell_from_event(event)
        self.chosen_cubes = set()

        if not self.is_in_cubes_field(x_coord, y_coord):
            return

        cube = self.game.get(x_coord, y_coord)
        if cube:
            self.game.try_delete_block(cube)
        self.repaint()

    def closeEvent(self, event):
        self.game.save_record_table()
        event.accept()

    def customize_game(self):
        self.player = self.nick_edit.text()
        if not self.player:
            return

        self.change_current_widget(self.settings)

    def start(self):
        game_size = int(self.game_size_edit.text())

        if not self.has_acceptable_inputs():
            return

        colors_count = int(self.count_edit.text())
        multiple_colors = int(self.multiple_edit.text())
        multicube_count = int(self.multicube_edit.text())

        settings = {
            'colors_count': colors_count,
            'multiple_colors': multiple_colors,
            'multicube_count': multicube_count
        }

        self.game = Game(game_size, self.player, settings)
        self.game.player = self.player
        self.cube_size = int(self.height() / self.game.size)
        self.reset()
        self.change_current_widget(self.game_widget)

    def restart(self):
        self.game = self.game.replicate()
        self.reset()
        self.repaint()

    def reset(self):
        self.is_result_saved = False
        self.is_game_finished = False

    def has_acceptable_inputs(self):
        return (self.game_size_edit.hasAcceptableInput() and
                self.count_edit.hasAcceptableInput() and
                self.multiple_edit.hasAcceptableInput() and
                self.multicube_edit.hasAcceptableInput())

    def autocomplete(self):
        while not self.game.is_finished:
            self.game.autocomplete()
            self.repaint()
        self.save_result()

    def go_to_main_menu(self):
        self.change_current_widget(self.main_menu)
        self.nick_edit.clear()

    def save_result(self):
        if not self.is_result_saved:
            self.game.insert_result()
            self.refresh_record_table()
            self.is_result_saved = True

    def change_current_widget(self, widget):
        self.in_game = widget == self.game_widget
        self.stacked.setCurrentWidget(widget)
        self.update()

    def change_validator(self):
        if not self.game_size_edit.text():
            return

        border = int(self.game_size_edit.text()) * 2
        self.multicube_edit.setPlaceholderText('from 0 to %s' % border)
        self.multicube_edit.setValidator(QIntValidator(0, border))

    def create_record_table(self):
        table = QTableWidget(len(self.game.record_table),
                             len(self.game.record_table[0]),
                             self.records)

        table.setHorizontalHeaderLabels(['Name', 'Score'])
        for row in range(10):
            for column in range(2):
                label = QLabel(self.game.record_table[row][column])
                label.setAlignment(Qt.AlignCenter)
                table.setCellWidget(row, column, label)
        return table

    def refresh_record_table(self):
        for row in range(self.record_table.rowCount()):
            for column in range(self.record_table.columnCount()):
                item = self.record_table.cellWidget(row, column)
                item.setText(self.game.record_table[row][column])

    def set_table_layout(self):
        self.records = QWidget(self)
        vbox = QVBoxLayout(self.records)
        vbox.setAlignment(Qt.AlignTop)

        table_label = QLabel('Record table')
        table_label.setFont(QFont('Arial', 20))
        vbox.addWidget(table_label, alignment=Qt.AlignCenter)

        self.record_table = self.create_record_table()
        vbox.addWidget(self.record_table, alignment=Qt.AlignJustify)

        self.add_button('Main menu',
                        lambda: self.change_current_widget(self.main_menu),
                        vbox, Qt.AlignBottom)

        self.stacked.addWidget(self.records)

    def set_game_layout(self):
        vbox = QVBoxLayout(self.game_widget)
        vbox.setAlignment(Qt.AlignRight)
        vbox.addStretch()

        self.add_button('Go to Main Menu', self.go_to_main_menu, vbox)
        self.add_button('Restart', self.restart, vbox)
        self.add_button('Autocomplete', self.autocomplete, vbox)

        self.stacked.addWidget(self.game_widget)

    def set_main_menu_layout(self):
        vbox = QVBoxLayout(self.main_menu)

        self.nick_edit = self.add_line_edit('Pick a nickname', vbox)

        self.add_button('Start', self.customize_game, vbox)
        self.add_button('Record table',
                        lambda: self.change_current_widget(self.records), vbox)

        vbox.setAlignment(Qt.AlignCenter)
        self.stacked.addWidget(self.main_menu)

    def set_customization_layout(self):
        vbox = QVBoxLayout(self.settings)
        vbox.setAlignment(Qt.AlignCenter)

        size_label = QLabel('Game size')
        vbox.addWidget(size_label, alignment=Qt.AlignCenter)
        self.game_size_edit = self.add_line_edit('Should be from 3 to 30',
                                                 vbox, 15,
                                                 QIntValidator(3, 30))

        self.game_size_edit.textChanged.connect(self.change_validator)

        count_label = QLabel('Colors count')
        vbox.addWidget(count_label, alignment=Qt.AlignCenter)
        self.count_edit = self.add_line_edit('Should be from 3 to 7',
                                             vbox, 5, QIntValidator(3, 7))

        multiple_colors_label = QLabel('Colors count of multicolor cubes')
        vbox.addWidget(multiple_colors_label, alignment=Qt.AlignCenter)
        self.multiple_edit = self.add_line_edit('2 or 3', vbox, 2,
                                                QIntValidator(2, 3))

        multicube_label = QLabel('Count of multicolor cubes')
        self.settings.layout().addWidget(multicube_label,
                                         alignment=Qt.AlignCenter)
        self.multicube_edit = self.add_line_edit('', self.settings.layout(), 0)

        self.add_button('Go', self.start, vbox)

        self.stacked.addWidget(self.settings)

    def paintEvent(self, event):
        if self.in_game:
            self.painter.begin(self)
            self.draw()
            self.painter.end()

    def draw(self):
        if self.is_game_finished:
            return

        self.painter.setRenderHint(self.painter.Antialiasing)
        info_x = self.game.size * self.cube_size + 10
        info_y = 20
        self.painter.drawRect(0, 0, self.game.size * self.cube_size,
                              self.game.size * self.cube_size)
        for x_coord in range(0, self.game.size):
            for y_coord in range(0, self.game.size):
                cube = self.game.get(x_coord, y_coord)
                if cube:
                    is_enlighten = cube in self.chosen_cubes
                    self.draw_cube(x_coord * self.cube_size,
                                   y_coord * self.cube_size,
                                   cube.colors, is_enlighten)

        self.painter.setFont(QFont('Arial', 10))
        points = str(self.game.score)
        self.painter.drawText(info_x, info_y, 'Points: %s' % points)
        info_y += 20

        block_points = str(self.game.get_points(len(self.chosen_cubes)))
        self.painter.drawText(info_x, info_y,
                              'Block points: %s' % block_points)
        info_y += 30

        for color in self.game.field.cubes:
            self.draw_cube(info_x, info_y, (color,), size=25)
            self.painter.drawText(info_x + 30,
                                  info_y + 20,
                                  str(self.game.field.cubes[color]))
            info_y += 30

        if self.game.is_finished:
            self.is_game_finished = True
            self.painter.setFont(QFont('Arial', 30))
            self.painter.drawText(self.game.size * self.cube_size / 4,
                                  self.game.size * self.cube_size / 2,
                                  'GAME OVER')
            self.save_result()
            return

    def draw_cube(self, x_coord, y_coord, color, enlighten=False, size=None):
        if not size:
            size = self.cube_size
        rect = QRect(x_coord, y_coord, size, size)
        divisor = len(color)
        self.painter.drawRect(rect)
        for i in range(divisor):
            q_color = QColor(color[i])
            if enlighten:
                q_color.setAlpha(160)
            new_rect = QRect(int(x_coord + size / divisor * i), y_coord,
                             int(size / divisor), size)
            self.painter.fillRect(new_rect, q_color)

    @staticmethod
    def add_button(text, callback, layout, alignment=Qt.AlignCenter):
        button = QPushButton(text)
        button.clicked.connect(callback)
        layout.addWidget(button, alignment=alignment)
        return button

    @staticmethod
    def add_line_edit(text, layout, value='', validator=None,
                      alignment=Qt.AlignCenter):
        edit = QLineEdit(str(value))
        edit.setPlaceholderText(text)
        if validator:
            edit.setValidator(validator)
        layout.addWidget(edit, alignment=alignment)
        return edit


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    WINDOW = Window()
    APP.exec_()
