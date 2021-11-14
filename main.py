from cv2 import COLOR_BGR2GRAY, THRESH_BINARY_INV, VideoCapture, bitwise_or, cvtColor, flip, threshold, waitKey, imshow, imread, IMREAD_UNCHANGED, resize, INTER_AREA, line, circle, FILLED
from cv2 import cvtColor, bitwise_or, bitwise_and, COLOR_GRAY2BGR, THRESH_BINARY_INV, COLOR_GRAY2BGR, threshold, namedWindow, WINDOW_NORMAL
from cvzone import HandTrackingModule, overlayPNG
import numpy as np


root = np.zeros((720, 1280, 3), np.uint8)



cap = VideoCapture(0)
#cap.set(3, 1280)
#cap.set(4, 720)

detector = HandTrackingModule.HandDetector(maxHands=1, detectionCon=0.5)


home = imread("img/play.png", IMREAD_UNCHANGED)
game = imread("img/game.png", IMREAD_UNCHANGED)
lose = imread("img/lose.png", IMREAD_UNCHANGED)
win = imread("img/win.png", IMREAD_UNCHANGED)



sqrW, sqrH = 318, 318
pox, poy = int(sqrW / 2), 60 # position of your image/sqr_img
b, g, r = 255, 255, 255


prevX, prevY = 0, 0
finishX, finishY = 0, 0

isStarted = False
gameOver = False

smoothX, smoothY = 0, 0

# Draw Canvas to test
canvas = np.zeros((720, 1280, 3), np.uint8)

smoothing = 3

corners = [0, 0, 0, 0]

# mistakes
mistakes = 0

page = home

centerWidth = round((1280-640)/2)
centerHight = round((720-480)/2)

while True:
    _, img = cap.read()
    img = flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    # 1280 / 2 = 640, 720 / 2 = 360 720-480=240

    root[centerHight:centerHight+480, centerWidth:centerWidth+640] = img
    root = overlayPNG(root, page, [0, 0])


    if hands:
        lmList = hands[0]['lmList']

        cursor = lmList[8]
        smoothX = int(prevX + (cursor[0] - prevX + centerWidth) / smoothing)
        smoothY = int(prevY + (cursor[1] - prevY + centerHight) / smoothing)

        if detector.fingersUp(hands[0]) == [0, 0, 0, 0, 0]:
            page = game
            root = overlayPNG(root, page, [0, 0])


        
        if detector.fingersUp(hands[0]) == [0, 1, 0, 0, 0]:
            # check if inside image
            #if pox < smoothX < pox + w and poy < smoothY < poy + h:
            cb, cg, cr = root[smoothY, smoothX, 0], root[smoothY, smoothX, 1], root[smoothY, smoothX, 2]
            if cb == b and cg == g and cr == r: # check if insied the cutter line
                isStarted = True

                if prevX != cursor[0] and prevY != cursor[1]:
                    if prevX == 0 and prevY == 0:
                        prevX, prevY = cursor[0]+centerWidth, cursor[1]+centerHight
                    if finishX == 0 and finishY == 0:
                        finishX, finishY = cursor[0]+centerWidth, cursor[1]+centerHight

                        
                    line(canvas, (prevX, prevY), (smoothX, smoothY), (255, 255, 0), thickness=9) # Draw Line if he is inside

                    if (smoothX-15 <= finishX <= smoothX+15 and smoothY-15 <= finishY <= smoothY+15):
                        if corners == [1, 1, 1, 1]: # Winner
                            isStarted = False
                            page = win
                            root = overlayPNG(root, page, [0, 0])
                            corners = [0, 0, 0, 0]
                            # remove green lines
                            canvas = np.zeros((720, 1280, 3), np.uint8)
                            finishX, finishY = 0, 0
                            prevX, prevY = 0, 0
                            c = 0
                            mistakes = 0


            elif cb == 250 and cg == g and cr == r:
                corners[0] = 1
                line(canvas, (prevX, prevY), (smoothX, smoothY), (255, 255, 0), thickness=9)

            elif cb == 251 and cg == g and cr == r:
                corners[1] = 1
                line(canvas, (prevX, prevY), (smoothX, smoothY), (255, 255, 0), thickness=9)

            elif cb == 252 and cg == g and cr == r:
                corners[2] = 1
                line(canvas, (prevX, prevY), (smoothX, smoothY), (255, 255, 0), thickness=9)

            elif cb == 253 and cg == g and cr == r:
                corners[3] = 1
                line(canvas, (prevX, prevY), (smoothX, smoothY), (255, 255, 0), thickness=9)



            elif isStarted: # LOSE
                mistakes += 1
                if mistakes == 10:
                    page = lose
                    isStarted =False
                    root = overlayPNG(root, page, [0, 0])
                    corners = [0, 0, 0, 0]
                    canvas = np.zeros((720, 1280, 3), np.uint8) # remove green lines
                    finishX, finishY = 0, 0
                    prevX, prevY = 0, 0
                    c = 0
                    mistakes = 0
                    gameOver = True
            circle(img, (smoothX, smoothY), 5, (255, 255, 0), FILLED)
            circle(root, (smoothX, smoothY), 5, (255, 255, 0), FILLED)


        else:
            prevX, prevY = 0, 0
            circle(img, (smoothX, smoothY), 5, (255, 255, 0), FILLED)
            circle(root, (smoothX, smoothY), 5, (255, 255, 0), FILLED)


      

        prevX, prevY = smoothX, smoothY

        



    imgGray = cvtColor(canvas, COLOR_BGR2GRAY)
    _, imgInv = threshold(imgGray, 50, 255, THRESH_BINARY_INV)
    imgInv = cvtColor(imgInv, COLOR_GRAY2BGR)
    root = bitwise_and(root, imgInv)
    root = bitwise_or(root, canvas)

    imshow('Image', img)
    imshow('Root', root)
    #imshow('Canvas', canvas)
    waitKey(1)
