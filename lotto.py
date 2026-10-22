import random
import tkinter as tk
from datetime import datetime

SET_COUNT = 5
NUMBERS_PER_SET = 6
MAX_NUMBER = 45

# 번호대별 색상 (동행복권 방식)
COLOR_RANGES = [
    (10, "#FBC400", "black"),   # 1~10  노랑
    (20, "#69C8F2", "black"),   # 11~20 파랑
    (30, "#FF7272", "white"),   # 21~30 빨강
    (40, "#AAAAAA", "white"),   # 31~40 회색
    (45, "#B0D840", "black"),   # 41~45 초록
]

BALL_SIZE = 44


def ball_colors(number):
    for limit, bg, fg in COLOR_RANGES:
        if number <= limit:
            return bg, fg


def make_set():
    return sorted(random.sample(range(1, MAX_NUMBER + 1), NUMBERS_PER_SET))


class LottoApp:
    def __init__(self, root):
        self.root = root
        root.title("로또 번호 생성기")
        root.resizable(False, False)

        tk.Label(root, text="로또 번호 생성기", font=("Helvetica", 20, "bold")).pack(pady=(16, 4))
        self.date_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.date_label.pack()

        self.board = tk.Frame(root)
        self.board.pack(padx=20, pady=12)

        tk.Button(root, text="번호 생성", font=("Helvetica", 14, "bold"),
                  command=self.generate).pack(pady=(0, 8))

        self.draw_legend()
        self.generate()

    def draw_legend(self):
        legend = tk.Frame(self.root)
        legend.pack(pady=(0, 14))
        names = ["1~10", "11~20", "21~30", "31~40", "41~45"]
        for (_, bg, _), name in zip(COLOR_RANGES, names):
            tk.Label(legend, text="●", fg=bg, font=("Helvetica", 14)).pack(side="left")
            tk.Label(legend, text=name + "  ", font=("Helvetica", 10)).pack(side="left")

    def draw_ball(self, parent, number):
        canvas = tk.Canvas(parent, width=BALL_SIZE, height=BALL_SIZE, highlightthickness=0)
        bg, fg = ball_colors(number)
        canvas.create_oval(2, 2, BALL_SIZE - 2, BALL_SIZE - 2, fill=bg, outline="")
        canvas.create_text(BALL_SIZE / 2, BALL_SIZE / 2, text=str(number),
                           fill=fg, font=("Helvetica", 14, "bold"))
        canvas.pack(side="left", padx=3)

    def generate(self):
        self.date_label.config(text=datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"))
        for child in self.board.winfo_children():
            child.destroy()
        for i in range(SET_COUNT):
            row = tk.Frame(self.board)
            row.pack(pady=4)
            tk.Label(row, text=f"{chr(65 + i)}", width=2,
                     font=("Helvetica", 14, "bold")).pack(side="left", padx=(0, 6))
            for n in make_set():
                self.draw_ball(row, n)


if __name__ == "__main__":
    root = tk.Tk()
    LottoApp(root)
    root.mainloop()
