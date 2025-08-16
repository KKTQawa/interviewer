import numpy as np
from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import ShortTermFeatures as sF
import os

class AudioFeatureExtractor:
    def __init__(self):
        """
        初始化音频特征提取器
        """
        pass

    def extract_features(self, audio_path):
        """
        从WAV音频文件中提取音频特征

        参数:
            audio_path: WAV音频文件路径

        返回:
            包含音频特征的字典，包括:
            - pitch_variation: 音高变化(标准差)
            - pitch_mean: 平均音高
            - energy_mean: 平均能量
            - energy_variation: 能量变化(标准差)
            - volume: 平均音量
        """
        try:
            if not os.path.exists(audio_path):
                raise ValueError(f"音频文件不存在: {audio_path}")

            # 读取音频文件
            [Fs, x] = aIO.read_audio_file(audio_path)

            # 如果是立体声，转换为单声道
            # 确保音频数据是连续的
            x = np.mean(x, axis=1) if len(x.shape) > 1 else x
            x = np.ascontiguousarray(x)

            # 计算帧长和步长（以样本数为单位）
            frame_length = int(0.050 * Fs)  # 50ms
            frame_step = int(0.025 * Fs)  # 25ms

            # 特征提取
            F, f_names = sF.feature_extraction(x, Fs, frame_length, frame_step)

            # 确保特征向量有足够的数据
            if F.shape[1] < 10:  # 如果帧数太少
                F = np.pad(F, ((0, 0), (0, 10 - F.shape[1])), mode='constant')

            # 计算音频特征
            pitch_stats = self._calc_pitch_stats(F[1] if F.shape[0] > 1 else np.zeros(F.shape[1]))
            energy_stats = self._calc_energy_stats(F[0] if F.shape[0] > 0 else np.zeros(F.shape[1]))

            return {
                "pitch_variation": float(pitch_stats["std"]),
                "pitch_mean": float(pitch_stats["mean"]),
                "energy_mean": float(energy_stats["mean"]),
                "energy_variation": float(energy_stats["std"]),
                "volume": float(np.mean(np.abs(x))) if len(x) > 0 else 0.0
            }

        except Exception as e:
            print(f"音频特征提取失败: {str(e)}")
            return self._get_default_result()

    def _get_default_result(self):
        """返回默认的特征提取结果"""
        return {
            "pitch_variation": 0.0,
            "pitch_mean": 0.0,
            "energy_mean": 0.0,
            "energy_variation": 0.0,
            "volume": 0.0
        }

    def _calc_pitch_stats(self, pitch_vector):
        """计算音高统计特征"""
        try:
            if len(pitch_vector) == 0:
                return {"mean": 0.0, "std": 0.0}

            return {
                "mean": float(np.mean(pitch_vector)),
                "std": float(np.std(pitch_vector))
            }
        except Exception as e:
            print(f"音高统计计算错误: {str(e)}")
            return {"mean": 0.0, "std": 0.0}

    def _calc_energy_stats(self, energy_vector):
        """计算能量统计特征"""
        try:
            if len(energy_vector) == 0:
                return {"mean": 0.0, "std": 0.0}

            return {
                "mean": float(np.mean(energy_vector)),
                "std": float(np.std(energy_vector))
            }
        except Exception as e:
            print(f"能量统计计算错误: {str(e)}")
            return {"mean": 0.0, "std": 0.0}

if __name__ == "__main__":
    extractor = AudioFeatureExtractor()
    features = extractor.extract_features("talk.wav")
    print(features)