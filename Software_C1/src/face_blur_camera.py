"""
Software_C1 — 实时摄像头人脸模糊
=================================
河海大学智泽实验室 2026 招新考核
张杨亦航 (2524030231)

用法:
  python face_blur_camera.py

按 'q' 退出, 按 '+'/'-' 调整模糊强度
"""

import cv2
import sys

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    print(f"[ERROR] 无法加载 Haar Cascade: {CASCADE_PATH}")
    sys.exit(1)

# 摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] 无法打开摄像头")
    sys.exit(1)

blur_strength = 25  # 初始模糊强度 (奇数)
show_bbox = True

print("=" * 50)
print("  实时人脸模糊")
print("  q — 退出")
print("  +/- — 调整模糊强度")
print("  b — 切换检测框显示")
print("=" * 50)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 镜像翻转 (更自然)
    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    ksize = blur_strength if blur_strength % 2 == 1 else blur_strength + 1

    for (x, y, w, h) in faces:
        roi = frame[y:y+h, x:x+w]
        roi_blurred = cv2.GaussianBlur(roi, (ksize, ksize), sigmaX=0)
        frame[y:y+h, x:x+w] = roi_blurred

        if show_bbox:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # 状态栏
    cv2.putText(frame, f"Blur: {ksize} | Faces: {len(faces)} | Q=quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Face Blur (Real-time)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('+') or key == ord('='):
        blur_strength = min(99, blur_strength + 4)
    elif key == ord('-'):
        blur_strength = max(3, blur_strength - 4)
    elif key == ord('b'):
        show_bbox = not show_bbox

cap.release()
cv2.destroyAllWindows()
