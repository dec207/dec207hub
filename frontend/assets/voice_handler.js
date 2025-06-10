/**
 * Dec207Hub - Voice Handler
 * TTS/STT 음성 처리 시스템
 */

class VoiceHandler {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.synthesis = null;
        this.init();
    }

    init() {
        this.setupTTS();
        this.setupVoiceButtons();
    }

    // ===== TTS (Text-to-Speech) 설정 =====
    setupTTS() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
            console.log('✅ TTS 지원됨');
        } else {
            console.log('❌ TTS 지원되지 않음');
        }
    }

    speak(text) {
        if (!this.synthesis) {
            console.log('TTS 사용 불가');
            return;
        }

        try {
            // 기존 음성 중단
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = DEC207_CONFIG.TTS_LANG;
            utterance.rate = DEC207_CONFIG.TTS_RATE;
            utterance.pitch = DEC207_CONFIG.TTS_PITCH;
            
            utterance.onstart = () => {
                console.log('🔊 TTS 시작');
            };
            
            utterance.onend = () => {
                console.log('🔊 TTS 완료');
            };
            
            utterance.onerror = (event) => {
                console.error('🔊 TTS 오류:', event.error);
            };
            
            this.synthesis.speak(utterance);
        } catch (error) {
            console.error('TTS 실행 오류:', error);
        }
    }

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }

    // ===== 음성 버튼 설정 =====
    setupVoiceButtons() {
        const speakerBtn = document.querySelector('.dec207-voice-btn.speaker');
        if (speakerBtn) {
            speakerBtn.classList.add('active');
            speakerBtn.textContent = '🔊';
            speakerBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleTTS();
            });
        }

        // STT 버튼 (미래 확장용)
        const micBtn = document.querySelector('.dec207-voice-btn.mic');
        if (micBtn) {
            micBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleSTT();
            });
        }
    }

    toggleTTS() {
        const speakerBtn = document.querySelector('.dec207-voice-btn.speaker');
        if (!speakerBtn) return;

        if (speakerBtn.classList.contains('active')) {
            speakerBtn.classList.remove('active');
            speakerBtn.textContent = '🔇';
            this.stopSpeaking();
            if (window.uiComponents) {
                window.uiComponents.showNotification('TTS 비활성화됨');
            }
        } else {
            speakerBtn.classList.add('active');
            speakerBtn.textContent = '🔊';
            if (window.uiComponents) {
                window.uiComponents.showNotification('TTS 활성화됨');
            }
        }
    }

    isTTSActive() {
        const speakerBtn = document.querySelector('.dec207-voice-btn.speaker');
        return speakerBtn && speakerBtn.classList.contains('active');
    }

    // ===== STT (Speech-to-Text) 설정 (미래 확장용) =====
    setupSTT() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = DEC207_CONFIG.TTS_LANG;
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleSTTResult(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('STT 오류:', event.error);
                this.isRecording = false;
                this.updateMicButton();
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
                this.updateMicButton();
            };
            
            console.log('✅ STT 지원됨');
        } else {
            console.log('❌ STT 지원되지 않음');
        }
    }

    toggleSTT() {
        if (!this.recognition) {
            if (window.uiComponents) {
                window.uiComponents.showNotification('음성 인식이 지원되지 않습니다.');
            }
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
            this.isRecording = false;
        } else {
            this.recognition.start();
            this.isRecording = true;
        }
        
        this.updateMicButton();
    }

    updateMicButton() {
        const micBtn = document.querySelector('.dec207-voice-btn.mic');
        if (micBtn) {
            micBtn.textContent = this.isRecording ? '🔴' : '🎤';
            micBtn.title = this.isRecording ? '음성 인식 중지' : '음성 인식 시작';
        }
    }

    handleSTTResult(transcript) {
        console.log('STT 결과:', transcript);
        
        // 채팅 입력 필드에 텍스트 입력
        const chatInput = document.querySelector('#chat-input-field');
        if (chatInput) {
            chatInput.value = transcript;
            chatInput.focus();
        }
        
        if (window.uiComponents) {
            window.uiComponents.showNotification(`음성 인식: ${transcript}`);
        }
    }

    // ===== 텍스트 정리 (TTS용) =====
    cleanTextForTTS(text) {
        return text
            .replace(/<[^>]*>/g, '')  // HTML 태그 제거
            .replace(/```[\s\S]*?```/g, '코드 블록')  // 코드 블록 대체
            .replace(/\*\*([^*]+)\*\*/g, '$1')  // 볼드 마크다운 제거
            .replace(/\*([^*]+)\*/g, '$1')  // 이탤릭 마크다운 제거
            .replace(/#{1,6}\s*/g, '')  // 헤더 마크다운 제거
            .replace(/[-*]\s/g, '')  // 리스트 마커 제거
            .replace(/\n+/g, '. ')  // 줄바꿈을 마침표로 대체
            .trim();
    }
}

// 전역 인스턴스 생성
window.voiceHandler = new VoiceHandler();
