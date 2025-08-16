// utils/audioWorkletNode.js
export const audioProcessorCode = `
class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.port.onmessage = (e) => {
      // 只接收音频数据，不处理recognizer对象
      if (e.data.sampleRate) {
        this.sampleRate = e.data.sampleRate;
      }
    };
  }

  process(inputs) {
    const input = inputs[0]?.[0];
    if (input) {
      this.port.postMessage({
        type: 'audio',
        buffer: input,
        sampleRate: this.sampleRate || 16000
      }, [input.buffer]); // 转移ArrayBuffer所有权
    }
    return true;
  }
}
registerProcessor('audio-processor', AudioProcessor);
`;

export async function createAudioWorkletNode(audioContext, stream) {
  try {
    const blob = new Blob([audioProcessorCode], { type: 'application/javascript' });
    const url = URL.createObjectURL(blob);
    await audioContext.audioWorklet.addModule(url);
    
    const workletNode = new AudioWorkletNode(audioContext, 'audio-processor');
    
    // 只传递必要的基本数据类型
    workletNode.port.postMessage({ 
      sampleRate: audioContext.sampleRate 
    });

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(workletNode);
    workletNode.connect(audioContext.destination);
    
    return workletNode;
  } catch (err) {
    console.error('AudioWorklet初始化失败:', err);
    throw err;
  }
}