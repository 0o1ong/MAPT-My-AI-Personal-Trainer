import cv2
import mediapipe as mp
import numpy as np

# Label
L = np.array([0,0,0,0,100,100,90,90,0,0])
S = np.array([60,100,100,60,0,0,0,0,0,0])
P = np.array([90,0,0,90,0,0,0,0,0,0,170,170])

#a_idx = ['왼쪽 팔', '왼쪽 어깨', '오른쪽 어깨', '오른쪽 팔', '오른쪽 골반', '왼쪽 골반', '오른쪽 다리', '왼쪽 다리', '오른쪽 발목', '왼쪽 발목', '오른쪽 몸', '왼쪽 몸']
landmark = ['left arm', 'left shoulder', 'right shoulder', 'right arm', 'right hip', 'left hip', 'right knee', 'left knee', 'right ankle', 'left ankle','right body','left body']
landmark_idx = [14, 12, 11, 13, 24, 23, 26, 25, 28, 27, 24, 23] #arm ~> elbow

# 운동마다 중요한 Joint
L_idx = [6, 7]
S_idx = [0, 1, 2, 3]
P_idx = [0, 3, 10, 11]

#counter and set
counter = 0
set_num = 0
pose_entered = False

def each_conf(a, b):
    error = abs(a - b)
    return 1 - (error / b)

def compare_motion (Label, data, classifier):
    global motion_conf
    motion_conf = 0
    result = []
    if classifier == "lunge": 
        joint_idx = L_idx
    elif classifier == "shoulderpress":
        joint_idx = S_idx
    else: #push up
        joint_idx = P_idx
  
    for i in range(len(joint_idx)):
        idx = joint_idx[i]
        conf = each_conf(data[idx], Label[idx])
        motion_conf += conf
        re = str(idx) + "," + landmark[idx] + ',' + str(conf)
        # re : [0] idx, [1] body text, [2] each confidence
        result.append(re)
    motion_conf /= len(joint_idx)
    return result

def counter_function(motion_conf):
    conf = motion_conf
    global counter, pose_entered
    if not pose_entered:
        pose_entered = conf > 0.9

    if pose_entered and (conf < 0.4):
        counter += 1
        pose_entered = False
    
    return counter

def reset(num):
    global counter, pose_entered, set_num
    counter = 0
    pose_entered = False
    if num == 1:
        set_num += 1

    else:
        set_num = 0

def output_motion(frame, classifier, countstopInPlus):
    global set_num
    int_count = 0
    
    if countstopInPlus > 0:
        reset(countstopInPlus)

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    # 좌우 반전
    frame = cv2.flip(frame, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
 
    if result.pose_landmarks is not None:
        res = result.pose_landmarks
        joint = np.zeros((33, 4))
        for j, lm in enumerate(res.landmark):
            joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

        # Compute angles between joints
        v1 = joint[[11, 13, 15, 15, 15, 11, 23, 25, 27, 27, 12, 12, 14, 16, 16, 16, 12, 24, 24, 26, 28, 28, 12, 11, 28, 27], :3] # Parent joint
        v2 = joint[[13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 11, 14, 16, 18, 20, 22, 24, 23, 26, 28, 30, 32, 24, 23, 24, 23], :3] # Child joint
        v = v2 - v1 
        # Normalize v
        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

        # Get angle using arcos of dot product
        angle = np.arccos(np.einsum('nt,nt->n',
            v[[0,0,11,11,17,17,18,6,19,7,22,23],:],
            v[[1,5,16,12,18,6,19,7,21,9,24,25],:])) 

        angle = np.degrees(angle) # Convert radian to degree
        d = np.array(angle)
        data = d.T

        mp_drawing.draw_landmarks(frame, res, mp_pose.POSE_CONNECTIONS)
        
        this_action = '?'
        
        if classifier == "lunge":
            label = L
        elif classifier == "shoulderpress":
            label = S
        else :
            label = P
        final = compare_motion(label, data, classifier)

        action = {'lunge': 'lunge','shoulderpress' : 'shoulder press','pushup':'push up'}

        if motion_conf > 0.90:
            this_action = action[classifier]
        
        #운동 이름
        name = action[classifier].upper()
        if name[0] == 'S':
            here = [430,450]
            
        else:
            here = [500,450]
        cv2.putText(frame, text = name, org=(here[0], here[1]),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(36,255,12), thickness=2)

        #count
        counter = counter_function(motion_conf)
        int_count = int(counter)
        cv2.putText(frame, text = "count: "+ str(counter), org=(20,40+30*(len(final)+1)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(36,255,12), thickness=2)
        #set
        cv2.putText(frame, text = "set: "+ str(set_num), org=(20,40+30*(len(final)+2)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(36,255,12), thickness=2)

        #코에 자세 이름 or ? 띄우기
        cv2.putText(frame, f'{this_action.upper()}', org=(int(res.landmark[0].x * frame.shape[1]), int(res.landmark[0].y * frame.shape[0] + 20)), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=(0, 0, 255), thickness=2)
        
        #각 부위별 위치, 정확도
        for i in range(len(final)):
            text_split = final[i].split(",")
            body_landmark_idx = landmark_idx[int(text_split[0])]
            body_text = text_split[1]
            acc = float(text_split[2]) * 100

            #몸에 숫자 출력
            cv2.putText(frame,text = str(i+1), 
                        org=((int(res.landmark[body_landmark_idx].x * frame.shape[1])), int(res.landmark[body_landmark_idx].y * frame.shape[0])),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
            
            #옆에 숫자와 함께 정확도 출력
            cv2.putText(frame, text = (str(i+1)+". "+body_text+" : "+str(round(acc,1))+"%"), org=(20,40+30*i),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(36,255,12), thickness=2)
            
            
    return frame, int_count
