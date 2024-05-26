import cv2
import numpy as np
import math
#import so

def nothing(x):
    pass

# Inicialização da captura de vídeo
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a câmera")
    exit()

cv2.namedWindow('frame')

# Criação de barras de controle para ajuste fino dos valores de cor da pele
cv2.createTrackbar('LH', 'frame', 0, 255, nothing)
cv2.createTrackbar('LS', 'frame', 0, 255, nothing)
cv2.createTrackbar('LV', 'frame', 0, 255, nothing)
cv2.createTrackbar('UH', 'frame', 255, 255, nothing)
cv2.createTrackbar('US', 'frame', 255, 255, nothing)
cv2.createTrackbar('UV', 'frame', 255, 255, nothing)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar imagem")
            cap.release()
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Erro ao reabrir a câmera")
                break
            continue

        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        # Defina a região de interesse (ROI)
        roi = frame[100:300, 100:300]
        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Obtém valores das barras de controle
        lh = cv2.getTrackbarPos('LH', 'frame')
        ls = cv2.getTrackbarPos('LS', 'frame')
        lv = cv2.getTrackbarPos('LV', 'frame')
        uh = cv2.getTrackbarPos('UH', 'frame')
        us = cv2.getTrackbarPos('US', 'frame')
        uv = cv2.getTrackbarPos('UV', 'frame')

        lower_skin = np.array([lh, ls, lv], dtype=np.uint8)
        upper_skin = np.array([uh, us, uv], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        mask = cv2.dilate(mask, kernel, iterations=4)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            cnt = max(contours, key=cv2.contourArea)
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            hull = cv2.convexHull(cnt)
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)
            arearatio = ((areahull - areacnt) / areacnt) * 100

            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)

            l = 0
            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(approx[s][0])
                    end = tuple(approx[e][0])
                    far = tuple(approx[f][0])

                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

                    # Verificar se os lados formam um triângulo válido
                    if a + b > c and a + c > b and b + c > a:
                        s = (a + b + c) / 2
                        ar = math.sqrt(s * (s - a) * (s - b) * (s - c))
                        d = (2 * ar) / a
                        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                        if angle <= 90 and d > 30:
                            l += 1
                            cv2.circle(roi, far, 3, [255, 0, 0], -1)
                        cv2.line(roi, start, end, [0, 255, 0], 2)
                l += 1

            font = cv2.FONT_HERSHEY_SIMPLEX
            if l == 1:
                if areacnt < 2000:
                    cv2.putText(frame, 'Esperando dados', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    if arearatio < 12:
                        cv2.putText(frame, '0 = Navegador', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        # os.system("xdg-open https://www.google.com")
                    elif arearatio < 17.5:
                        cv2.putText(frame, '1 = Gedit', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        # os.system("gedit")
                    else:
                        cv2.putText(frame, '1 = Gedit', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        # os.system("gedit")
            elif l == 2:
                cv2.putText(frame, '2 = Calculator', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                # os.system("gnome-calculator")
            elif l == 3:
                if arearatio < 27:
                    cv2.putText(frame, '3 = LibreOffice Impress', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    # os.system("libreoffice --impress")
                else:
                    cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 4:
                cv2.putText(frame, '4 = Firefox', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                # os.system("firefox")
            elif l == 5:
                cv2.putText(frame, '5 = Spyder', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                # os.system("spyder")
            elif l == 6:
                cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
except KeyboardInterrupt:
    print("Interrompido pelo usuário")
finally:
    cv2.destroyAllWindows()
    cap.release()
