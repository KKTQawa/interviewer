import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import ShortTermFeatures as sF
import os

class videoFeature:
    def __init__(self, silence_threshold=0.01):
        self.silence_threshold = silence_threshold  # 静音能量阈值

    def extract_features(self, audio_path):
        try:
            if not os.path.exists(audio_path):
                raise ValueError(f"音频文件不存在: {audio_path}")

            [Fs, x] = aIO.read_audio_file(audio_path)

            x = np.mean(x, axis=1) if len(x.shape) > 1 else x
            x = np.ascontiguousarray(x)

            frame_length = int(0.050 * Fs)
            frame_step = int(0.025 * Fs)

            F, f_names = sF.feature_extraction(x, Fs, frame_length, frame_step)
            #print(F)
            energy = F[0]  # 能量

            # 识别非静音帧
            non_silent_idx = np.where(energy > self.silence_threshold)[0]
            if len(non_silent_idx) == 0:
                return self._get_default_result()

            # 非静音帧的音高与能量
            energy_ns = energy[non_silent_idx]

            return {
                "energy_mean": float(np.mean(energy_ns)),
                "energy_variation": float(np.std(energy_ns)),
            }

        except Exception as e:
            print(f"音频特征提取失败: {str(e)}")
            return self._get_default_result()

    def _get_default_result(self):
        return {
            "energy_mean": 0.0,
            "energy_variation": 0.0
        }

if __name__ == "__main__":
    extractor = videoFeature()
    features = extractor.extract_features("talk.wav")
    print(features)
