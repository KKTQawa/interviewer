from deepface import DeepFace
from PIL import Image
import time
def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size
def assert_single_face(image_path, detector_backend='retinaface'):
    # 检测图中所有人脸
    faces = DeepFace.extract_faces(img_path=image_path, detector_backend=detector_backend, enforce_detection=True)
    if len(faces) != 1:
        print(f"图片中检测到 {len(faces)} 张人脸，必须只有一张人脸。")
        raise RuntimeError(f"请确保只有一张人脸。")
    else:
        print("✅ 图片验证通过，仅有一张人脸。")

    #识别人脸大小有约1秒延迟
    img_w, img_h = get_image_size(image_path)
    w = faces[0]['facial_area']['w']
    h = faces[0]['facial_area']['h']
    face_area_ratio= max(w / img_w, h / img_h)
    print("face_area:",face_area_ratio)
    min_ratio=0.3
    max_ratio=0.55
    if face_area_ratio < min_ratio:
        raise RuntimeError("❌ 距离屏幕太远")
    elif face_area_ratio > max_ratio:
        raise RuntimeError("❌ 距离屏幕太近")
    else:
        print("✅ 人脸大小合规")
def video2_run(img_path):
    suggest=[]
    start_time = time.time()  # 记录开始时间
    try:
        assert_single_face(img_path)

        # 如果通过了，再进行分析
        result = DeepFace.analyze(img_path=img_path, actions=['gender', 'emotion'])
        print("人物性别:", result[0]['dominant_gender'])
        emo=result[0]['dominant_emotion']
        print("人物表情:", emo)

        if emo=="sad":
            suggest.append("请打起精神")
        if emo=="disguest" or emo=="angry":
            suggest.append("请注意场合")


    except RuntimeError as e:
        print(img_path, "验证失败", "❌ 错误：", e)
        raise RuntimeError(e)
    except ValueError as e:
        print(img_path, "验证失败", "❌ 错误：", e)
        raise RuntimeError("请专注！")
    end_time = time.time()  # 记录结束时间
    elapsed = end_time - start_time
    print(f"处理 {img_path} 用时：{elapsed:.3f} 秒\n")
    return suggest

if __name__ == '__main__':
    # 示例使用
    for i in range(1, 5):
        img_path = f"{i}.jpg"
        print("验证图片：", img_path)
        start_time = time.time()  # 记录开始时间
        try:
            assert_single_face(img_path)

            # 如果通过了，再进行分析
            result = DeepFace.analyze(img_path=img_path, actions=['gender', 'emotion'])
            print("人物性别:",result[0]['dominant_gender'])
            print("人物表情:",result[0]['dominant_emotion'])
        except ValueError as e:
            print(img_path,"验证失败","❌ 错误：", e)
        end_time = time.time()  # 记录结束时间
        elapsed = end_time - start_time
        print(f"处理 {img_path} 用时：{elapsed:.3f} 秒\n")
    example_result="[{'gender': {'Woman': 35.22948622703552, 'Man': 64.77051377296448}, 'dominant_gender': 'Man', 'region': {'x': 124, 'y': 260, 'w': 430, 'h': 430, 'left_eye': (500, 312), 'right_eye': (349, 537)}, 'face_confidence': 0.93, 'emotion': {'angry': 2.6346505571059052e-05, 'disgust': 3.888438890743774e-21, 'fear': 99.76969955978987, 'happy': 0.003955769952195023, 'sad': 0.0006349392530058857, 'surprise': 0.224790176736723, 'neutral': 0.0008882407730304724}, 'dominant_emotion': 'fear'}]"

