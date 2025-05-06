"""
作业题：成语接龙

题目：

编写一个Python程序，实现成语接龙的功能。

参考：https://www.4399.com/flash/166492_4.htm

具体要求：

参考案例说明：

首页、登录页不用做。

时间记时、得分不用做。

只需呈现 第几题、题目内容、提交（判断对错，到下一题）。见参考图。
基本规则：

下一个成语的首字必须与上一个成语的尾字相同（不考虑声调）。

不允许连续使用相同的成语。

用户答错，提示错误，并清空重做
代码要求：

代码结构清晰，有必要的注释。

使用函数来组织代码，提高代码复用性。
UI要求：

采用：pyqt

视觉上无具体要求，简单即可"""
import sys
import csv
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QGridLayout, QMessageBox, QHBoxLayout, QVBoxLayout)
from collections import defaultdict


class IdiomGame(QWidget):
    def __init__(self):
        super().__init__()
        self.used_idioms = set()
        self.current_end = ""
        self.char_pool = []
        self.selected_chars = []
        self.idiom_dict = defaultdict(list)
        self.completed_count = 0

        self.init_ui()
        self.load_idioms("idioms.csv")
        self.start_new_round()

    def init_ui(self):
        self.setWindowTitle('成语接龙')
        self.setFixedSize(600, 400)

        # 状态显示
        status_layout = QHBoxLayout()
        self.lbl_completed = QLabel("当前得分：0分", self)
        self.lbl_round = QLabel("第1题", self)
        self.lbl_status = QLabel("当前尾字：无", self)
        self.lbl_selected = QLabel("已选汉字：", self)
        status_layout.addWidget(self.lbl_completed)
        status_layout.addWidget(self.lbl_round)
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()

        # 汉字按钮网格
        grid_layout = QGridLayout()
        self.btn_chars = []
        for i in range(20):
            btn = QPushButton("", self)
            btn.setFixedSize(50, 50)
            btn.clicked.connect(self.on_char_clicked)
            self.btn_chars.append(btn)
            grid_layout.addWidget(btn, i // 5, i % 5)

        # 功能按钮
        btn_submit = QPushButton("提交", self)
        btn_submit.clicked.connect(self.check_answer)
        btn_clear = QPushButton("清空", self)
        btn_clear.clicked.connect(self.clear_selection)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.lbl_selected)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(btn_submit)
        main_layout.addWidget(btn_clear)
        self.setLayout(main_layout)

    def load_idioms(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"')
                for row in reader:
                    if len(row) < 2: continue
                    idiom = row[1].strip()
                    if len(idiom) == 4:
                        self.idiom_dict[idiom[0]].append(idiom)
        except FileNotFoundError:
            QMessageBox.critical(self, "错误", "成语库文件不存在！")

    def start_new_round(self):
        """生成首个成语并初始化"""
        if not self.idiom_dict:
            QMessageBox.critical(self, "错误", "成语库为空！")
            return

        # 随机选择初始成语[1,5](@ref)
        first_idiom = random.choice([i for v in self.idiom_dict.values() for i in v])
        self.used_idioms.add(first_idiom)
        self.current_end = first_idiom[-1]
        self.lbl_status.setText(f"起始成语：{first_idiom}\n当前尾字：{self.current_end}")
        self.generate_char_pool()

    def generate_char_pool(self):
        """智能生成字堆（确保包含接续字）"""
        # 收集候选字符
        candidates = []

        # 强制包含当前尾字的后续成语字符
        if self.current_end:
            # 获取所有以当前尾字开头的成语
            next_idioms = self.idiom_dict.get(self.current_end, [])
            for idiom in next_idioms:
                # 拆解成语字符加入候选池
                candidates += list(idiom) * 1  # 每个字符重复2次,确保有字，设置为2可提高字出现频率

            # 确保当前尾字至少3次出现
            candidates += [self.current_end] * max(3, 4 - candidates.count(self.current_end))

        # 补充高频字符
        all_chars = [c for idioms in self.idiom_dict.values() for c in "".join(idioms)]
        freq_chars = [c for c, _ in sorted(
            {char: all_chars.count(char) for char in set(all_chars)}.items(),
            key=lambda x: x[1], reverse=True
        )[:5]]
        candidates += freq_chars * 3

        # 动态补足字堆
        while len(candidates) < 20:
            candidates.append(random.choice(all_chars))

        # 随机选取并确保当前尾字存在
        random.shuffle(candidates)
        self.char_pool = candidates[:20]
        if self.current_end and self.current_end not in self.char_pool:
            self.char_pool[-1] = self.current_end

        # 更新按钮显示
        for i, btn in enumerate(self.btn_chars):
            btn.setText(self.char_pool[i] if i < 20 else "")
            btn.setEnabled(True)

    def on_char_clicked(self):
        if len(self.selected_chars) >= 4:
            return

        btn = self.sender()
        self.selected_chars.append(btn.text())
        self.lbl_selected.setText("已选汉字：" + "".join(self.selected_chars))
        btn.setEnabled(False)

    def validate_idiom(self, idiom):
        """五重验证机制"""
        # 字符必须全部在字堆中
        for char in idiom:
            if char not in self.char_pool:
                return False, f"『{char}』不在当前字堆中"

        # 标准验证条件
        if len(idiom) != 4:
            return False, "需要四字成语"
        if idiom in self.used_idioms:
            return False, "成语已使用"
        if self.current_end and idiom[0] != self.current_end:
            return False, f"需要以『{self.current_end}』开头"
        if idiom not in self.idiom_dict.get(idiom[0], []):
            return False, "非标准成语"
        return True, ""

    def clear_selection(self):
        self.selected_chars.clear()
        self.lbl_selected.setText("已选汉字：")
        for btn in self.btn_chars:
            btn.setEnabled(True)

    def check_answer(self):
        if len(self.selected_chars) != 4:
            QMessageBox.warning(self, "错误", "请选择4个汉字")
            return

        user_input = "".join(self.selected_chars)
        is_valid, msg = self.validate_idiom(user_input)

        if not is_valid:
            QMessageBox.warning(self, "错误", msg)
            self.clear_selection()
            return

        # 更新游戏状态
        self.completed_count += 1
        self.lbl_completed.setText(f"已得分：{self.completed_count}分")
        self.used_idioms.add(user_input)
        self.current_end = user_input[-1]
        self.lbl_round.setText(f"第{len(self.used_idioms) + 1}题")
        self.lbl_status.setText(f"当前尾字：{self.current_end}")

        # 生成新字堆并检查可用性
        self.generate_char_pool()
        self.clear_selection()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = IdiomGame()
    game.show()
    sys.exit(app.exec_())
