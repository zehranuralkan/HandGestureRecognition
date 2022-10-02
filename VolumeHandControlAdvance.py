import time
from ctypes import cast, POINTER

import cv2
import cvzone
import numpy as np
import speech_recognition as sr
import vlc
from comtypes import CLSCTX_ALL
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm

################################
wCam, hCam = 640, 488
################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
segmantor = SelfiSegmentation()
detector = htm.handDetector(detectionCon=0.7, maxHands=2)

playVlc = vlc.MediaPlayer("Internet 101 _ National Geographic.mp4")
playVlc.play()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()


minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255,0,0)

while True:
    success, img = cap.read()
    #Find Hand El Bulma
    img = detector.findHand(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    r = sr.Recognizer()
    mic = sr.Microphone()
    if len(lmList) != 0:
        #Filter based on size Boyuta göre filtrele
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1]) // 100
        fingers = detector.fingersUp()
        if 250 < area < 800:
            # Find Distance between index and Thumb Başparmak ile index arasındaki meafeyi bulma
            length, img, lineInfo = detector.findDistance(4, 8, img)
            print(length)
            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])
            # Reduce Resolution to make it smoother çözünürlüğü azaltma
            smoothness = 10
            volPer = smoothness * round(volPer/smoothness)
            # if pinky is down set volume ses seviyesi ayarlama
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255,0,0)
        else:
            print(fingers)

            if fingers == [1, 1, 1, 1, 1] :
               cv2.putText(img, f'DUR:', (200, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)
               if(fingers != [0, 0, 0, 0, 0]):
                   playVlc.set_pause(1)

            elif fingers ==[0, 0, 0, 0, 0]:
                cv2.putText(img, f'DEVAM ET:', (200, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)
                playVlc.play()
            elif fingers == [0, 1, 0, 0, 0]:
                cv2.putText(img, f'ILERI :', (200, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)
                current_time = playVlc.get_time()
                playVlc.set_time(current_time + 150)
            elif fingers == [0,1,1,0,0]:
                cv2.putText(img, f'GERI :', (200, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)
                current_time = playVlc.get_time()
                playVlc.set_time(current_time - 150)
                # drawings



    cv2.rectangle(img, (50,150), (85,400), (255,0,0), 3)
    cv2.rectangle(img, (50,int(volBar)), (85,400), (8,255,0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)

    # frame rate
    cTime = time.time()
    fps = 1 / (cTime-pTime)
    pTime = cTime
    imgOut = segmantor.removeBG(img, (41, 193, 61), threshold=0.5)
    imgStacked = cvzone.stackImages([img, imgOut], 2, 1)
    cv2.putText(imgStacked,f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)

