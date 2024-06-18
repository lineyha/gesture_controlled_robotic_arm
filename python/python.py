import cv2
import mediapipe as mp
import math
import serial

import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
import mediapipe.python.solutions.drawing_styles as drawing_styles

from numpy import interp

debug = True
#ser = serial.Serial('COM11', 115200)

cap = cv2.VideoCapture(0)

cap.set(3, 4000)
cap.set(4, 4000)

mphand = mp.solutions.hands
hands = mphand.Hands()
mpdraw = mp.solutions.drawing_utils

x_min = 13
x_mid = 93
x_max = 173
# use angle between wrist and index finger to control x axis
palm_angle_min = -50
palm_angle_mid = 20

y_min = 70
y_mid = 110
y_max = 150

# use wrist y to control y axis
wrist_y_min = 0.3
wrist_y_max = 0.9

z_min = 113
z_mid = 146
z_max = 180
# use palm size to control z axis
plam_size_min = 0.1
plam_size_max = 0.3

claw_open_angle = 93
claw_close_angle = 170

servo_angle = [x_mid,y_mid,z_mid,claw_open_angle] # [x, y, z, claw]
prev_servo_angle = servo_angle
fist_threshold = 7



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles



clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
map_range = lambda x, in_min, in_max, out_min, out_max: abs((x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min)


def is_fist(hand_landmarks, palm_size):
    # calculate the distance between the wrist and the each finger tip
    distance_sum = 0
    WRIST = hand_landmarks.landmark[0]
    for i in [7,8,11,12,15,16,19,20]:
        distance_sum += ((WRIST.x - hand_landmarks.landmark[i].x)**2 + \
                         (WRIST.y - hand_landmarks.landmark[i].y)**2 + \
                         (WRIST.z - hand_landmarks.landmark[i].z)**2)**0.5
    
    return distance_sum/palm_size < fist_threshold






def landmark_to_servo_angle(hand_landmarks):
    servo_angle = [x_mid,y_mid,z_mid,claw_open_angle]
    WRIST = hand_landmarks.landmark[0]
    INDEX_FINGER_MCP = hand_landmarks.landmark[5]
    THUMB_TIP = hand_landmarks.landmark[4]
    # calculate the distance between the wrist and the index finger
    palm_size = ((WRIST.x - INDEX_FINGER_MCP.x)**2 + (WRIST.y - INDEX_FINGER_MCP.y)**2 + (WRIST.z - INDEX_FINGER_MCP.z)**2)**0.5
    
    thumb_distance = ((WRIST.x - THUMB_TIP.x)**2 + 
                          (WRIST.y - THUMB_TIP.y)**2 + 
                          (WRIST.z - THUMB_TIP.z)**2)**0.5
    
    
    #cv2.putText(img, "PALM SIZE "+str(palm_size), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
    

    if is_fist(hand_landmarks, palm_size):
        servo_angle[3] = claw_close_angle
        cv2.putText(img, "CLAW "+"CLOSED", (120, 400), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
        
    else:
        servo_angle[3] = claw_open_angle
        cv2.putText(img, "CLAW "+"OPEN", (120,400), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)

    # calculate x angle
    distance = thumb_distance
    angle = (WRIST.x - INDEX_FINGER_MCP.x) / distance  # calculate the radian between the wrist and the index finger
    angle = int(angle * 180 / 3.1415926)               # convert radian to degree
    
    
    
    
    #angle = clamp(angle, palm_angle_min, palm_angle_mid)
    servo_angle[0] = map_range(angle, palm_angle_min, palm_angle_mid, x_max, x_min)
    cv2.putText(img, " X  "+str(servo_angle[0]), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
    # cv2.putText(img, " D  "+str(distance), (500, 500), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
    # cv2.putText(img, " INTER  "+str(interp(angle,[13,170],[13,170])), (700, 400), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)

    # calculate y angle
    wrist_y = clamp(WRIST.y, wrist_y_min, wrist_y_max)
    servo_angle[1] = map_range(wrist_y, wrist_y_min, wrist_y_max, y_max, y_min)
    cv2.putText(img, " Y  "+str(servo_angle[1]), (100, 200), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)

    # calculate z angle
    palm_size = clamp(palm_size, plam_size_min, plam_size_max)
    servo_angle[2] = map_range(palm_size, plam_size_min, plam_size_max, z_max, z_min)
    cv2.putText(img, " Z  "+str(servo_angle[2]), (100, 300), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)

    # float to int
    servo_angle = [int(i) for i in servo_angle]

    return servo_angle


def log_scale(value):
    return (math.log(value)) * 100


while True:
    _, img = cap.read()
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(imgrgb)

    lmlist = []
    if results.multi_hand_landmarks:
        if len(results.multi_hand_landmarks) == 1:
                # print("One hand detected")
                #cv2.putText(img, "BİR EL", (100, 460), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
                hand_landmarks = results.multi_hand_landmarks[0]
                servo_angle = landmark_to_servo_angle(hand_landmarks)
                if servo_angle != prev_servo_angle:
                    print("Servo angle: ", servo_angle)
                    prev_servo_angle = servo_angle
                    #ser.write(bytearray(servo_angle))
                
        else:
            #cv2.putText(img, "İKİ EL", (100, 460), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 8)
            print(results.multi_hand_landmarks[1])
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
