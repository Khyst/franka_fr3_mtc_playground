import cv2
import sys
import os
import numpy as np
import json
import time
import torch
import signal
import threading
import base64
from scipy.spatial.transform import Rotation as R

# ROS 2 관련 임포트
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Pose
from std_msgs.msg import String

# 기존 AI/Vision 클래스 임포트 (기존 경로 유지 가정)
from classes import dinov2, megapose, mmdet_sam, k4a_camera
from utils.choose import validate_preds
from utils.convert import Convert_YCB
from generate import generate_ycb
from openai import OpenAI
import speech_recognition as sr

class ObjectVisionNode(Node):

    def __init__(self):
        super().__init__('object_vision_node')
        
        # 1. Publisher 설정
        self.pose_pub = self.create_publisher(Pose, '/object/pose', 10)
        self.name_pub = self.create_publisher(String, '/object/name', 10)
        
        # 2. 상태 변수 초기화
        self.object_pose = Pose()
        self.object_pose.orientation.w = 1.0
        self.object_name = String()
        self.object_name.data = "none"
        
        # 3. 100Hz 발행 타이머 (ROS 1의 vision_thread 대체)
        # ROS 2에서는 별도 스레드 대신 타이머 콜백을 권장합니다.
        self.timer_period = 0.01  # 100Hz
        self.timer = self.create_timer(self.timer_period, self.publish_callback)
        
        # 4. 모델 및 장치 초기화 (메인 로직용)
        self.device = 'cuda:0'
        self.init_models()
        
        # 5. 메인 추론 루프를 위한 스레드 생성
        # 음성 인식과 GPT 호출은 블로킹 작업이므로 별도 스레드가 필요합니다.
        self.main_thread = threading.Thread(target=self.main_loop)
        self.main_thread.daemon = True
        self.main_thread.start()

    def init_models(self):
        self.get_logger().info("Initializing AI Models...")
        self.convert_YCB = Convert_YCB()
        self.MMDet_SAM = mmdet_sam.MMDet_SAM(self.device)
        self.K4A_Camera = k4a_camera.K4A_Camera()
        self.Megapose = megapose.Megapose(self.device)
        self.DINOv2 = dinov2.DINOv2(self.device)
        self.client = OpenAI(api_key="your_openai_api_key")

    def publish_callback(self):
        """데이터를 /object/pose 토픽으로 지속적으로 발행"""
        self.pose_pub.publish(self.object_pose)
        self.name_pub.publish(self.object_name)

    def main_loop(self):
        """음성 인식 및 포즈 추론 메인 루프"""
        system_command = "You are an AI assistant... (기존 프롬프트 유지)"
        
        while rclpy.ok():
            # 1. 음성 인식 및 GPT 호출
            gpt_response = self.recognize_speech_and_gpt(system_command)
            
            # 2. Vision Stream (MegaPose 추론)
            pose_result = self.run_pose_estimation(str(gpt_response))
            
            if pose_result is not None:
                # 안전하게 공유 변수 업데이트
                self.update_shared_data(pose_result, str(gpt_response))

    def update_shared_data(self, pose_array, name):
        self.object_pose.position.x = pose_array[0]
        self.object_pose.position.y = pose_array[1]
        self.object_pose.position.z = pose_array[2]
        self.object_pose.orientation.x = pose_array[3]
        self.object_pose.orientation.y = pose_array[4]
        self.object_pose.orientation.z = pose_array[5]
        self.object_pose.orientation.w = pose_array[6]
        self.object_name.data = name
        self.get_logger().info(f"Updated Pose for: {name}")

    def gpt4_api_call(self, system_message, text_message, image_message=None):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": [
                    {"type": "text", "text": system_message}
                ]},
                {"role": "user", "content": [
                    {"type": "text", "text": text_message},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_message}"}
                    }
                ]}
            ],
            model="gpt-4o",
            temperature=1.0,
        )
        return chat_completion.choices[0].message.content

    def stream(self, desc_name: str):
        pose_estimation = None
        try_count = 0

        while pose_estimation is None and try_count < 3:
            ret_color, color, ret_depth, depth = K4A_Camera.get_capture()
            if not ret_color or not ret_depth:
                continue
            else:
                color = cv2.cvtColor(color, cv2.COLOR_BGRA2RGB)
                depth = np.array(depth, dtype=np.float32) / 1000
                print("Estimating {} pose...".format(desc_name))
                # first time estimation
                # run mmdet_sam to get bbox and mask
                pred = MMDet_SAM.run_detector(color.copy(), desc_name)
                if len(pred['labels']) > 0:
                    # run fbdinov2 to get the best prediction
                    best_pred = validate_preds(color, pred, DINOv2)

                    mask = pred['masks'][best_pred].cpu().numpy().astype(np.uint8)
                    mask = np.transpose(mask, (1, 2, 0))

                    color = np.array(color, dtype=np.uint8)
                    color_masked = color * mask
                    mask = mask.squeeze(axis=-1)
                    depth_masked = depth * mask

                    bbox = np.round(pred['boxes'][best_pred].cpu().numpy()).astype(int)
                    ycb_name = convert_YCB.convert_name(pred['labels'][best_pred])

                    # run megapose
                    pose_estimation = Megapose.inference(color_masked, depth_masked, ycb_name, bbox)
                    del mask, color_masked, depth_masked

                if pose_estimation is None:
                    try_count += 1
                    print("No pose estimation found")
                    continue
                else:
                    pose_matrix = pose_estimation.poses.cpu().numpy()
                    rotation = R.from_matrix(pose_matrix[0, :3, :3]).as_quat()
                    translation = pose_matrix[0, :3, 3]
                    print(f'Pose estimated for {ycb_name} is translation: {translation} and rotation: {rotation}')
                    contour_image, mesh_image = Megapose.get_output_image(color, pose_estimation, ycb_name)
                    mesh_image = cv2.cvtColor(mesh_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(f'{str(os.path.abspath(os.path.dirname(__file__)))}/Pose estimation result {ycb_name}.jpg', mesh_image)
                    cv2.imshow('Pose estimation result', mesh_image)
                    # Wait for a key press indefinitely or for a specified amount of time in milliseconds
                    cv2.waitKey(0)
                    # Destroy all the windows created by OpenCV
                    cv2.destroyAllWindows()
                    return np.hstack([translation, rotation])
        return None

def main(args=None):
    rclpy.init(args=args)
    node = ObjectVisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()