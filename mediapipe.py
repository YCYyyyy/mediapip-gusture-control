import cv2
import mediapipe as mp

import math

#导入键鼠控制包 https://blog.csdn.net/weixin_34379710/article/details/112176809
import pyautogui
#避免由鼠标移动到屏幕角落触发的PyAutoGUI安全故障
pyautogui.FAILSAFE = False

#蜂鸣器 测试用
import winsound


#鼠标位置参数
mX = 0
mY = 0

#鼠标是否已被点击过
mouseUnclicked = True

#手掌是否已张开过
handOpened = False

#保存最近3个位置
cursor_positions = [(0,0)]*3

#设置pyautogui刷新时间
pyautogui.PAUSE = 0.0001

#初始化mediapipe库中的手部跟踪器
mp_hands = mp.solutions.hands

#初始化opencv库中的视频捕捉器
cap = cv2.VideoCapture(0)

#求两关键点间距
def pointsDistance(p1,p2):
    square=(hand_landmarks.landmark[p1].x-hand_landmarks.landmark[p2].x)**2+(hand_landmarks.landmark[p1].y-hand_landmarks.landmark[p2].y)**2
    distance=math.sqrt(square)
    return distance

#求解二维向量的角度
def vector_2d_angle(v1,v2):
    v1_x=v1[0]
    v1_y=v1[1]
    v2_x=v2[0]
    v2_y=v2[1]
    try:
        angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
    except:
        angle_ =65535.
    if angle_ > 180.:
        angle_ = 65535.
    return angle_

#计算手指角度
def hand_angle(hand_):
    '''
        获取对应手相关向量的二维角度,根据角度确定手势
    '''
    angle_list = []
    #---------------------------- thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
        ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
        )
    angle_list.append(angle_)
    #---------------------------- index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
        ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
        )
    angle_list.append(angle_)
    #---------------------------- middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
        ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
        )
    angle_list.append(angle_)
    #---------------------------- ring 无名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
        ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
        )
    angle_list.append(angle_)
    #---------------------------- pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
        ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
        )
    angle_list.append(angle_)
    return angle_list

#控制鼠标
def controlFunctions():
    # 在指定镜头区域内获取部分关键点坐标
    mX = round((hand_landmarks.landmark[1].x
                +hand_landmarks.landmark[0].x
                +hand_landmarks.landmark[10].x
                +hand_landmarks.landmark[14].x
                +hand_landmarks.landmark[18].x
                +hand_landmarks.landmark[2].x
                +hand_landmarks.landmark[9].x
                +hand_landmarks.landmark[17].x)/8 * 2 - 0.5, 5) * 1920
    mY = round((hand_landmarks.landmark[1].y
                +hand_landmarks.landmark[0].y
                +hand_landmarks.landmark[10].y
                +hand_landmarks.landmark[14].y
                +hand_landmarks.landmark[18].y
                +hand_landmarks.landmark[2].y
                +hand_landmarks.landmark[9].y
                +hand_landmarks.landmark[17].y)/8 * 2 - 0.5, 5) * 1080
    # 基于前几帧的坐标取平均值以消除抖动，会导致一定延迟
    # 将当前坐标加入到列表中
    cursor_positions.append((mX, mY))
    # 移除最旧的坐标
    cursor_positions.pop(0)
    # 计算坐标的平均值
    avg_position = tuple(map(lambda x: sum(x) / len(x), zip(*cursor_positions)))
    # 控制鼠标移动到坐标
    if results.multi_hand_landmarks:
        pyautogui.moveTo(avg_position[0], avg_position[1])

#初始化手部跟踪器
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    #持续捕捉视频帧
    while cap.isOpened():

        #读取视频帧
        success, image = cap.read()
        if not success:
            print("无法读取视频流")
            continue

        #将帧裁剪为16：9比例
        height, width, _ = image.shape
        new_height = int(width / 16 * 9)
        crop = int((height - new_height) / 2)
        image = image[crop:crop + new_height, :]

        #将图像转换为RGB格式以进行手部跟踪
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        #进行手部跟踪
        results = hands.process(image)

        # 转换回BGR格式
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        #如果检测到手部
        if results.multi_hand_landmarks:
            #提取手指关键点并打印坐标
            for hand_landmarks in results.multi_hand_landmarks:
                #打印出每个关键点坐标
                for id, landmark in enumerate(hand_landmarks.landmark):
                    print(f"Point {id} coordinates: ({'%.5f' % landmark.x}, {'%.5f' % landmark.y}, {'%.5f' % landmark.z})")

            #显示手部关键点及连线
            mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            #提取手指关键点并计算手指角度并打印角度
            hand_local = []
            for i in range(21):
                x = hand_landmarks.landmark[i].x * image.shape[1]
                y = hand_landmarks.landmark[i].y * image.shape[0]
                hand_local.append((x, y))
            if hand_local:
                angle_list = hand_angle(hand_local)
            print(f"从拇指到小拇指角度:{'%.2f' % angle_list[0]}|{'%.2f' % angle_list[1]}|{'%.2f' % angle_list[2]}|{'%.2f' % angle_list[3]}|{'%.2f' % angle_list[4]}")

            # 中指无名指小拇指收拢，食指伸出
            if (angle_list[2] > 80) and (angle_list[3] > 80) and (angle_list[4] > 80) and pointsDistance(8,12)>pointsDistance(12,20):
                # 食指弯曲，按下鼠标，鼠标已被点击
                if angle_list[1] > 80 and mouseUnclicked:
                    winsound.Beep(900, 100)
                    # 按下鼠标
                    pyautogui.click()
                    # 鼠标已被点击
                    mouseUnclicked = False
                # 若食指伸直，鼠标未被点击
                if angle_list[1] < 60 and not mouseUnclicked:
                    # 鼠标未被点击
                    mouseUnclicked = True
                # 使控制鼠标
                controlFunctions()

            # 手掌张开
            if angle_list[0] < 40 and angle_list[1] < 20 and angle_list[2] < 20 and angle_list[3] < 20 and angle_list[4] < 20\
                    and pointsDistance(4,20)>pointsDistance(0,5):
                # 手掌张开过
                handOpened = True

            # 若手掌张开过并现在指尖合拢
            if handOpened and (pointsDistance(4,8)+pointsDistance(8,12)+pointsDistance(12,16)+pointsDistance(16,20))<pointsDistance(0,5):
                # 手掌未张开过
                handOpened = False
                winsound.Beep(500, 100)
                #查看任务视图
                pyautogui.hotkey('win', 'tab')

        #显示图像并等待按esc键退出
        cv2.imshow("Hand Tracking", image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

# 关闭捕捉器和窗口
cap.release()
cv2.destroyAllWindows()