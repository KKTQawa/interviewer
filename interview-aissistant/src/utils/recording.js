import Recorder from 'recorder-js';

let audioContext = null;
let recorder = null;
let mediaStream = null;
let stopflag=false;

export async function startRecord() {
stopflag=false;
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    //额外创建音频流，独立性强
    recorder = new Recorder(audioContext, {
        // 可设定录制参数
        type: 'audio/wav',
    });

    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder.init(mediaStream);
    recorder.start();
    return true;
}

export async function stopRecord() {
    if (!recorder||stopflag) return null;
    stopflag=true;
    try {
        const { blob } = await recorder.stop();
        return blob;
    } catch (error) {
        console.warn('Stop recording failed:', error);
        return null;
    } finally {
        mediaStream.getTracks().forEach(track => track.stop());
        if (audioContext && audioContext.state !== 'closed') {
    await audioContext.close();
}
    }
}
