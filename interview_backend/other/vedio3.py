import cv2
import mediapipe as mp
import numpy as np
import glob
import os
class VideoAnalyzer:
    def __init__(self):
        """初始化视频分析器"""
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.pose = mp.solutions.pose.Pose()
        self.drawing = mp.solutions.drawing_utils

    def analyze(self, image_dir: str = "tmp/"):
        """分析 tmp 目录下的所有帧图像（JPEG）"""
        try:
            # 收集所有 jpeg 文件并排序（按文件名顺序）
            image_paths = sorted(glob.glob(os.path.join(image_dir, "*.jpg")) +
                                 glob.glob(os.path.join(image_dir, "*.jpeg")))

            if not image_paths:
                raise ValueError(f"目录中没有找到图像: {image_dir}")

            video_results = []
            total_frames = len(image_paths)

            for frame_count, image_path in enumerate(image_paths, start=1):
                frame = cv2.imread(image_path)
                if frame is None:
                    print(f"无法读取图像: {image_path}")
                    continue

                # 分析图像帧
                result = self.analyze_frame(frame)
                video_results.append(result)

            # 汇总结果
            return self.aggregate_results(video_results)

        except Exception as e:
            print(f"图像分析错误: {str(e)}")
            return {
                "details": {
                    "posture_stability": 0.0,
                    "hand_movement": 0.0
                }
            }

    def analyze_frame(self, frame):
        """分析单帧图像"""
        if frame is None:
            return {
                "posture_stability": 0.0,
                "hand_movement": 0.0
            }

        try:
            # 转换颜色空间
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 微表情分析
            face_results = self.face_mesh.process(rgb_frame)

            # 肢体语言分析
            pose_results = self.pose.process(rgb_frame)
            posture_score = self._calc_posture(pose_results)
            hand_movement = self._detect_hand_gestures(pose_results)

            # 确保所有值都是浮点数
            return {
                "posture_stability": float(posture_score),
                "hand_movement": float(hand_movement)
            }
        except Exception as e:
            print(f"帧分析错误: {str(e)}")
            return {
                "eyebrow_raise": 0.0,
                "posture_stability": 0.0,
                "hand_movement": 0.0
            }

    def aggregate_results(self, results):
        """汇总分析结果"""
        if not results:
            return {
                "details": {
                    "posture_stability": 0.0,
                    "hand_movement": 0.0
                }
            }

        try:
            # 过滤掉无效的结果
            valid_results = [r for r in results if r is not None]

            if not valid_results:
                return {
                    "details": {
                        "posture_stability": 0.0,
                        "hand_movement": 0.0
                    }
                }

            # 计算各指标的平均值
            posture_stabilities = [float(r.get("posture_stability", 0.0)) for r in valid_results]
            hand_movements = [float(r.get("hand_movement", 0.0)) for r in valid_results]

            # 使用 numpy 的 nan_to_num 来处理可能的 NaN 值
            details = {
                "posture_stability": float(np.nan_to_num(np.mean(posture_stabilities))),
                "hand_movement": float(np.nan_to_num(np.mean(hand_movements)))
            }

            return {
                "details": details
            }

        except Exception as e:
            print(f"汇总结果错误: {str(e)}")
            return {
                "details": {
                    "posture_stability": 0.0,
                    "hand_movement": 0.0
                }
            }
    def _calc_posture(self, results):
        if not results or not results.pose_landmarks:
            return 0.0
        try:
            landmarks = results.pose_landmarks.landmark
            # 计算肩膀倾斜度
            shoulder_slope = abs(landmarks[11].y - landmarks[12].y)
            # 计算头部稳定性
            head_stability = abs(landmarks[0].y - (landmarks[11].y + landmarks[12].y) / 2)

            return float(1.0 - (shoulder_slope + head_stability) / 2)
        except Exception as e:
            print(f"姿势分析错误: {str(e)}")
            return 0.0

    def _detect_hand_gestures(self, results):
        if not results or not results.pose_landmarks:
            return 0.0
        try:
            landmarks = results.pose_landmarks.landmark
            # 计算手部移动幅度
            left_hand = np.array([landmarks[19].x, landmarks[19].y, landmarks[19].z])
            right_hand = np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z])

            # 计算手部移动的标准差作为手势频率指标
            movement = np.std(np.concatenate([left_hand, right_hand]))
            return float(movement)
        except Exception as e:
            print(f"手势分析错误: {str(e)}")
            return 0.0

if __name__ == "__main__":
    vv=VideoAnalyzer()
    print(vv.analyze())