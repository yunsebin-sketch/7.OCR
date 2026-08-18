"""MNIST 손글씨 숫자 데이터로 분류 모델을 학습하고 model.pkl로 저장한다."""
import time

import joblib
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

MODEL_PATH = "model.pkl"


def main():
    print("MNIST 데이터셋 다운로드 중... (최초 1회, 시간이 걸릴 수 있습니다)")
    mnist = fetch_openml("mnist_784", version=1, as_frame=False, parser="auto")
    X = mnist.data.astype(np.float32) / 255.0
    y = mnist.target.astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=10000, random_state=42, stratify=y
    )

    print(f"학습 데이터: {X_train.shape[0]}개, 테스트 데이터: {X_test.shape[0]}개")
    print("모델 학습 중...")
    start = time.time()
    clf = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=256,
        max_iter=30,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=3,
        verbose=True,
    )
    clf.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"학습 완료 ({elapsed:.1f}초)")

    acc = clf.score(X_test, y_test)
    print(f"테스트 정확도: {acc * 100:.2f}%")

    joblib.dump(clf, MODEL_PATH)
    print(f"모델 저장 완료: {MODEL_PATH}")


if __name__ == "__main__":
    main()
