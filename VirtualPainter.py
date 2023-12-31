import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm


folderPath = "Header"
myList = os.listdir(folderPath)
print(myList)
overlayList = []

# importing images
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
print(len(overlayList))

header = overlayList[0]

drawColor = (255,0,255)
brushThickness = 15
eraserThickness = 80

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector()
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    # importing image
    success, img = cap.read()
    # mirror camera
    img = cv2.flip(img, 1)

    # finding hand landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # location of tip of index & middle finger
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # identifying fingers for selection and drawing
        fingers = detector.fingersUp()

    # selection mode (2 fingers up)
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            print("selection mode")

            # overlay colour selection
            if y1 < 125:
                # colour red select
                if 300 < x1 < 450:
                    header = overlayList[0]
                    drawColor = (255, 0, 255)
                # colour blue select
                elif 560 < x1 < 720:
                    header = overlayList[1]
                    drawColor = (255, 0, 0)
                # colour green select
                elif 847 < x1 < 995:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                # eraser select
                elif 1107 < x1 < 1220:
                    header = overlayList[3]
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1,y1-25), (x2,y2+25), drawColor, cv2.FILLED)

        # drawing mode on canvas
        if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1,y1), 10, drawColor, cv2.FILLED)
            print("drawing mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)

            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1

    # merging overlay and drawing canvas
    # converting to gray img
    # convert to binary img
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    # combine inverse and img overlay for drawing
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)


    # setting header image
    img[0:125, 0:1280] = header
    img = cv2.addWeighted(img, 1, imgCanvas, 1, 0)
    cv2.imshow("Image", img)
    cv2.waitKey(1)