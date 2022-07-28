from mediapipe_code import output_motion
from youtube import youtube_search
from get_routine import get_routine
from flask import Flask, Response, url_for, redirect, render_template, request
import cv2
import numpy as np
import mediapipe as mp
import threading

outputFrame = None
lock = threading.Lock()

total_routine_num = 0 #전체 운동 수
routine_info = None #루틴 정보
routine_idx = 1 #현재 루틴 인덱스

countStop = -1
setNumber = 0

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Home.html')

# 사용자 설정 루틴
@app.route('/select')
def exercise_select():
    return render_template('exercise_selection.html')

# 도움말
@app.route('/help')
def help():
    return render_template('help.html')
    
# js 데이터 받아오기
@app.route('/select/dataloading', methods = ['POST'])
def get_post_js_data():
    global routine_info, total_routine_num
    exercise = request.form["exercise_name"]
    exercise_num = request.form["num"]
    set_num = request.form["set_num"]
    routine_info = get_routine([exercise, exercise_num, set_num])
    total_routine_num = len(routine_info)
    return "\^o^/"

# webcam
@app.route('/exercise/<classifier>')
def open_webcam(classifier):
    global routine_info, routine_idx
    t = threading.Thread(target=detect_motion, args=(classifier,))
    t.daemon = True
    t.start()
    return render_template('webcam.html', routine_info = routine_info, routine_idx = routine_idx)

# 오운완
@app.route('/exercise/done')
def exercise_done():
    global routine_info
    return render_template('exercise_done.html', routine_info = routine_info)

# 유튜브 영상 추천 검색
@app.route('/search', methods=['POST'])
def search_keyword():
    keyword = request.form['keyword']
    result = youtube_search(keyword)
    return render_template('youtube.html', title1=result[0][0], link1=result[1][0], thumbnail1=result[2][0],
                        title2=result[0][1], link2=result[1][1], thumbnail2=result[2][1],
                        link3=result[1][2], title3=result[0][2], thumbnail3=result[2][2])

@app.route('/reload')
def calculate_count(counter):
    global routine_idx, total_routine_num, countStop, setNumber
    curr_exercise = routine_info[routine_idx-1]
    input_count = curr_exercise[1]
    input_set = curr_exercise[2]

    if setNumber == input_set : # set 수 달성 | 카운터와 상관없이 종료
        countStop = 2
        setNumber = 0
        if total_routine_num != routine_idx: # 모든 루틴이 끝난게 아니면?
            routine_idx += 1
        return False

    if input_count != 0 and counter >= input_count : # counter 달성
        countStop = 1
        setNumber += 1
    return True

def detect_motion(classifier):
    global outputFrame, lock, countStop
    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    if not video.isOpened():
        video=cv2.VideoCapture(0)
    if not video.isOpened():
        raise IOError("Cannot open webcame") 

    while video.isOpened():
        hasFrame, frame = video.read()
        if not hasFrame:
            cv2.waitKey()
            break
        else:
            outputFrame, counter = output_motion(frame, classifier, countStop)
            countStop = -1
            if not calculate_count(counter):
                break
            with lock:
                outputFrame = outputFrame.copy()

def gen():
    global outputFrame, lock
    # Traverse the frames of the output video stream
    while True:
      # Wait until the thread lock is acquired
        with lock:
         # Check whether there is content in the output. If there is no content, skip this process
            if outputFrame is None:
                continue

         # Compress the output to jpeg format
        (flag, jpeg) = cv2.imencode(".jpg", outputFrame)
        frame=jpeg.tobytes()
         # Make sure the output is compressed correctly
        if not flag:
            continue

        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        

@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, threaded=True)
    
