"""마우스로 숫자를 그리면 학습된 모델이 어떤 숫자인지 인식해주는 GUI 프로그램."""
import os
import sys
import tkinter as tk
from tkinter import messagebox

import joblib
import numpy as np
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

CANVAS_SIZE = 280  # 28 * 10, 확대해서 그리기 편하게
BRUSH_SIZE = 16


class DigitRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("숫자 인식 프로그램")
        self.root.resizable(False, False)

        if not os.path.exists(MODEL_PATH):
            messagebox.showerror(
                "모델 없음",
                "model.pkl 파일을 찾을 수 없습니다.\n"
                "먼저 train_model.py를 실행해서 모델을 학습시켜 주세요.",
            )
            sys.exit(1)

        self.model = joblib.load(MODEL_PATH)

        # 실제 그림은 내부적으로 흰 배경(0)에 검은 선(255)으로 그려서
        # 나중에 MNIST 형식(흰 글씨/검은 배경)으로 반전 처리한다.
        self.image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), color=0)
        self.draw = ImageDraw.Draw(self.image)

        self._build_ui()
        self.last_x = None
        self.last_y = None

    def _build_ui(self):
        title = tk.Label(self.root, text="숫자를 마우스로 그려주세요", font=("맑은 고딕", 14))
        title.pack(pady=(10, 0))

        self.canvas = tk.Canvas(
            self.root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black", cursor="cross"
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=(0, 10))

        recognize_btn = tk.Button(
            btn_frame, text="인식하기", width=12, command=self.recognize, bg="#4CAF50", fg="white"
        )
        recognize_btn.grid(row=0, column=0, padx=5)

        clear_btn = tk.Button(btn_frame, text="지우기", width=12, command=self.clear_canvas)
        clear_btn.grid(row=0, column=1, padx=5)

        self.result_label = tk.Label(
            self.root, text="결과: -", font=("맑은 고딕", 20, "bold"), fg="#333"
        )
        self.result_label.pack(pady=(0, 5))

        self.confidence_label = tk.Label(self.root, text="", font=("맑은 고딕", 11), fg="#666")
        self.confidence_label.pack(pady=(0, 10))

    def on_mouse_down(self, event):
        self.last_x, self.last_y = event.x, event.y

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        if self.last_x is not None:
            self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=BRUSH_SIZE, fill="white", capstyle=tk.ROUND, smooth=True,
            )
            self.draw.line(
                [self.last_x, self.last_y, x, y],
                fill=255, width=BRUSH_SIZE, joint="curve",
            )
        self.last_x, self.last_y = x, y

    def on_mouse_up(self, event):
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="결과: -")
        self.confidence_label.config(text="")

    def recognize(self):
        bbox = self.image.getbbox()
        if bbox is None:
            messagebox.showinfo("알림", "먼저 숫자를 그려주세요.")
            return

        # 그린 부분만 잘라내고 여백을 둔 뒤 28x28로 축소 (MNIST 전처리와 유사하게)
        cropped = self.image.crop(bbox)
        size = max(cropped.size)
        padded = Image.new("L", (size, size), color=0)
        padded.paste(cropped, ((size - cropped.width) // 2, (size - cropped.height) // 2))

        margin = size // 5
        padded_with_margin = Image.new("L", (size + margin * 2, size + margin * 2), color=0)
        padded_with_margin.paste(padded, (margin, margin))

        small = padded_with_margin.resize((28, 28), Image.LANCZOS)

        arr = np.array(small, dtype=np.float32) / 255.0
        flat = arr.reshape(1, -1)

        pred = self.model.predict(flat)[0]
        proba = None
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(flat)[0]
            confidence = proba[pred] * 100
            self.confidence_label.config(text=f"신뢰도: {confidence:.1f}%")
        else:
            self.confidence_label.config(text="")

        self.result_label.config(text=f"결과: {pred}")


def main():
    root = tk.Tk()
    app = DigitRecognizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
