/**
 * Dec207Hub - Retro Mac JavaScript Framework v2.0 (Fixed)
 * AI 채팅 허브를 위한 레트로 Mac OS 스타일 웹 컴포넌트 라이브러리
 * Created by dec207
 */

class Dec207Hub {
    constructor() {
        this.conversationHistory = [];
        this.maxHistoryLength = 20;
        this.isConnected = false;
        this.isRecording = false;
        this.recognition = null;
        this.synthesis = null;
        this.websocket = null;
        this.websocketAttempted = false; // WebSocket 연결 시도 플래그
        this.websocketErrorShown = false; // 오류 메시지 표시 플래그
        
        // 메시지 처리 상태 관리
        this.isProcessingMessage = false;
        this.demoResponseTimer = null;
        
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupAll();
            });
        } else {
            this.setupAll();
        }
    }

    setupAll() {
        this.setupMenus();
        this.setupButtons();
        this.setupChat();
        this.setupVoice();
        this.setupWebSocket();
        this.showWelcomeMessage();
        this.setupMobileViewport();
    }

    // 모바일 뷰포트 설정
    setupMobileViewport() {
        const setViewportHeight = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        window.addEventListener('orientationchange', () => {
            setTimeout(setViewportHeight, 100);
        });
    }

    // ===== CHAT SYSTEM =====
    setupChat() {
        const chatInput = document.querySelector('#chat-input-field');
        const sendBtn = document.querySelector('.dec207-btn.primary');
        const chatForm = document.querySelector('.dec207-chat-form');
        
        console.log('채팅 설정:', { chatInput: !!chatInput, sendBtn: !!sendBtn, chatForm: !!chatForm });
        
        // Form submit 이벤트 처리 (강화된 안전장치)
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.sendMessage();
                return false;
            });
        }
        
        // 엔터 키 처리 (keydown으로 변경하여 더 안정적)
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.sendMessage();
                    return false;
                }
            });
        }
        
        // 전송 버튼 클릭
        if (sendBtn) {
            sendBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.sendMessage();
                return false;
            });
        }
    }

    sendMessage() {
        console.log('sendMessage 호출됨');
        
        const chatInput = document.querySelector('#chat-input-field');
        const message = chatInput?.value.trim();
        
        console.log('메시지 확인:', { message, isProcessing: this.isProcessingMessage });
        
        if (!message) {
            console.log('빈 메시지로 인한 전송 취소');
            return;
        }
        
        if (this.isProcessingMessage) {
            console.log('이미 처리 중인 메시지로 인한 전송 취소');
            return;
        }
        
        // 처리 상태 설정
        this.isProcessingMessage = true;
        
        // Clear input
        chatInput.value = '';
        
        try {
            console.log('메시지 전송 시작:', message);
            
            // Add user message to chat
            this.addMessageToChat(message, 'user');
            
            // Show typing indicator
            this.showTypingIndicator();
            
            // Send to AI (WebSocket or API)
            this.sendToAI(message);
        } catch (error) {
            console.error('메시지 전송 오류:', error);
            this.isProcessingMessage = false;
        }
    }

    addMessageToChat(message, sender) {
        console.log('메시지 추가:', { message: message.substring(0, 50), sender });
        
        const chatMessages = document.querySelector('.dec207-chat-messages');
        if (!chatMessages) {
            console.error('채팅 메시지 컨테이너를 찾을 수 없음');
            return;
        }
        
        const messageEl = document.createElement('div');
        messageEl.className = `dec207-message ${sender}`;
        
        if (sender === 'system') {
            messageEl.innerHTML = `<strong>[SYSTEM]</strong> ${message}`;
        } else if (sender === 'ai') {
            const formattedMessage = this.formatAIMessage(message);
            messageEl.innerHTML = formattedMessage;
        } else {
            messageEl.textContent = message;
        }
        
        // 메시지 추가 및 스크롤
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        if (sender !== 'system') {
            this.addToConversationHistory(sender, message);
        }
        
        // 가벼운 애니메이션 (리플로우 최소화)
        messageEl.style.opacity = '0.8';
        setTimeout(() => {
            messageEl.style.transition = 'opacity 0.2s ease';
            messageEl.style.opacity = '1';
        }, 10);
    }

    formatAIMessage(message) {
        let formatted = message.trim();
        formatted = this.filterSpecialCharacters(formatted);
        formatted = this.formatInlineCode(formatted);
        formatted = this.formatLists(formatted);
        formatted = this.formatEmphasis(formatted);
        formatted = this.formatParagraphs(formatted);
        return formatted;
    }

    filterSpecialCharacters(text) {
        return text
            .replace(/[*]{3,}/g, '**')
            .replace(/[#]{4,}/g, '###')
            .replace(/[-]{4,}/g, '---')
            .replace(/[=]{4,}/g, '===')
            .replace(/\n{4,}/g, '\n\n\n')
            .replace(/\s{3,}/g, '  ');
    }

    formatInlineCode(text) {
        return text.replace(/`([^`]+)`/g, '<span class="inline-code">$1</span>');
    }

    formatLists(text) {
        text = text.replace(/(^|\n)([-*] .+(?:\n[-*] .+)*)/gm, (match, prefix, list) => {
            const items = list.split('\n').map(item => {
                const content = item.replace(/^[-*] /, '').trim();
                return `<li>${content}</li>`;
            }).join('');
            return `${prefix}<ul>${items}</ul>`;
        });

        text = text.replace(/(^|\n)(\d+\. .+(?:\n\d+\. .+)*)/gm, (match, prefix, list) => {
            const items = list.split('\n').map(item => {
                const content = item.replace(/^\d+\. /, '').trim();
                return `<li>${content}</li>`;
            }).join('');
            return `${prefix}<ol>${items}</ol>`;
        });

        return text;
    }

    formatEmphasis(text) {
        text = text.replace(/\*\*([^*]+)\*\*/g, '<span class="bold">$1</span>');
        text = text.replace(/__([^_]+)__/g, '<span class="bold">$1</span>');
        text = text.replace(/\*([^*]+)\*/g, '<span class="italic">$1</span>');
        text = text.replace(/_([^_]+)_/g, '<span class="italic">$1</span>');
        return text;
    }

    formatParagraphs(text) {
        const paragraphs = text.split(/\n\s*\n/);
        if (paragraphs.length > 1) {
            return paragraphs
                .map(p => p.trim())
                .filter(p => p.length > 0)
                .map(p => `<div class="paragraph">${p}</div>`)
                .join('');
        }
        return text;
    }

    showTypingIndicator() {
        const chatMessages = document.querySelector('.dec207-chat-messages');
        if (!chatMessages) return;
        
        const typingEl = document.createElement('div');
        typingEl.className = 'dec207-typing-indicator';
        typingEl.innerHTML = `
            <span>AI thinking...</span>
            <div class="dec207-typing-dots">
                <div class="dec207-typing-dot"></div>
                <div class="dec207-typing-dot"></div>
                <div class="dec207-typing-dot"></div>
            </div>
        `;
        
        chatMessages.appendChild(typingEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.dec207-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    sendToAI(message) {
        console.log('AI 전송 시작:', { message, isConnected: this.isConnected });
        
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const payload = {
                type: 'chat',
                message: message,
                conversation_history: this.getConversationHistoryForAI(),
                timestamp: new Date().toISOString()
            };
            
            console.log('WebSocket 전송:', payload);
            this.websocket.send(JSON.stringify(payload));
        } else {
            console.log('데모 모드로 전환');
            this.simulateDemoResponse(message);
        }
    }
    
    simulateDemoResponse(message) {
        console.log('데모 응답 시뮬레이션 시작');
        
        if (this.demoResponseTimer) {
            clearTimeout(this.demoResponseTimer);
        }
        
        this.demoResponseTimer = setTimeout(() => {
            try {
                this.hideTypingIndicator();
                
                const responses = [
                    "안녕하세요! **Dec207Hub AI 어시스턴트**입니다.\n\n어떻게 도와드릴까요?",
                    "흥미로운 질문이네요.\n\n더 자세히 설명해 주시겠어요?",
                    "네, 이해했습니다.\n\n다른 질문이 있으시면 언제든 말씀해 주세요.",
                    "**Dec207Hub의 MCP 연동 기능**을 통해 다음과 같은 도구들과 연결할 수 있습니다:\n\n- Blender 3D 모델링\n- Unity 게임 엔진\n- 파일 관리 시스템\n- 날씨 API 연동",
                    "레트로 Mac OS 스타일이 마음에 드시나요? 🤖\n\n이 인터페이스는 **클래식 Mac 디자인**에서 영감을 받아 제작되었습니다."
                ];
                
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                console.log('데모 응답 생성:', randomResponse.substring(0, 50) + '...');
                
                this.addMessageToChat(randomResponse, 'ai');
                
                const speakerBtn = document.querySelector('.dec207-voice-btn.speaker.active');
                if (this.synthesis && speakerBtn) {
                    const cleanText = randomResponse.replace(/<[^>]*>/g, '').replace(/```[\s\S]*?```/g, '코드 블록');
                    this.speak(cleanText);
                }
            } catch (error) {
                console.error('데모 응답 생성 오류:', error);
                this.addMessageToChat('죄송합니다. 응답 생성 중 오류가 발생했습니다.', 'ai');
            } finally {
                console.log('메시지 처리 완료');
                this.isProcessingMessage = false;
                this.demoResponseTimer = null;
            }
        }, 1000 + Math.random() * 2000);
    }

    // ===== 나머지 기본 메서드들 =====
    setupMenus() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('dec207-menu-item')) {
                e.preventDefault();
                e.stopPropagation();
                this.handleMenuClick(e.target);
            }
        });
    }

    handleMenuClick(menuItem) {
        const menuText = menuItem.textContent.toLowerCase();
        const event = new CustomEvent('dec207-menu-click', {
            detail: { menu: menuText, element: menuItem },
            bubbles: true
        });
        document.dispatchEvent(event);
    }

    setupButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('dec207-btn')) {
                this.handleButtonClick(e.target, e);
            }
        });
    }

    handleButtonClick(button, event) {
        // 전송 버튼인 경우 전송 처리를 다른 곳에서 하므로 여기서는 아무것도 하지 않음
        if (button.classList.contains('primary') && button.closest('.dec207-chat-form')) {
            // 전송 버튼은 setupChat()에서 처리하므로 여기서는 애니메이션만
            this.addClickAnimation(button);
            return;
        }
        
        // 다른 버튼들에 대한 기본 처리
        event.preventDefault();
        event.stopPropagation();
        
        this.addClickAnimation(button);
        const customEvent = new CustomEvent('dec207-button-click', {
            detail: { button, originalEvent: event },
            bubbles: true
        });
        document.dispatchEvent(customEvent);
    }

    addClickAnimation(button) {
        button.style.transform = 'translateY(1px)';
        setTimeout(() => {
            button.style.transform = '';
        }, 100);
    }

    setupVoice() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
        }
        
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
    }

    speak(text) {
        if (!this.synthesis) return;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ko-KR';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        this.synthesis.speak(utterance);
    }

    toggleTTS() {
        const speakerBtn = document.querySelector('.dec207-voice-btn.speaker');
        if (speakerBtn) {
            if (speakerBtn.classList.contains('active')) {
                speakerBtn.classList.remove('active');
                speakerBtn.textContent = '🔇';
                this.showNotification('TTS 비활성화됨');
                if (this.synthesis) {
                    this.synthesis.cancel();
                }
            } else {
                speakerBtn.classList.add('active');
                speakerBtn.textContent = '🔊';
                this.showNotification('TTS 활성화됨');
            }
        }
    }

    setupWebSocket() {
        // config.js에서 설정 읽기
        let SERVER_IP = '192.168.0.7'; // 기본값
        
        // config.js 설정 확인
        if (window.DEC207_SERVER_IP && window.DEC207_SERVER_IP !== 'auto') {
            SERVER_IP = window.DEC207_SERVER_IP;
            console.log('config.js에서 지정된 IP 사용:', SERVER_IP);
        } else {
            // 자동 감지 로직
            if (window.location.protocol !== 'file:') {
                // 웹서버에서 실행 중일 때
                SERVER_IP = window.location.hostname;
                console.log('웹서버 hostname 사용:', SERVER_IP);
            } else {
                // file:// 프로토콜일 때 기본값 사용
                SERVER_IP = '192.168.0.7';
                console.log('file:// 프로토콜 - 기본 IP 사용:', SERVER_IP);
            }
        }
        
        // 중복 연결 방지
        if (this.websocketAttempted) {
            console.log('WebSocket 연결 이미 시도됨, 재시도 안함');
            return;
        }
        this.websocketAttempted = true;
        
        const wsUrl = `ws://${SERVER_IP}:8000/ws`;
        console.log('🔌 WebSocket 연결 시도:', wsUrl);
        
        // 연결 타임아웃 설정 (15초) - 백엔드 처리 시간 고려
        const connectionTimeout = setTimeout(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
                console.log('⏰ WebSocket 연결 타임아웃 (15초), 데모 모드로 전환');
                this.websocket.close();
                this.websocket = null;
                this.isConnected = false;
                this.updateConnectionStatus(false);
                if (!this.websocketErrorShown) {
                    this.showNotification('AI 서버 연결 실패: 데모 모드로 전환', 3000);
                    this.websocketErrorShown = true;
                }
            }
        }, 15000);
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                clearTimeout(connectionTimeout);
                this.isConnected = true;
                this.updateConnectionStatus(true);
                console.log('✅ WebSocket 연결 성공!');
                this.showNotification('AI 서버 연결 성공!', 2000);
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = (event) => {
                clearTimeout(connectionTimeout);
                this.isConnected = false;
                this.updateConnectionStatus(false); // 항상 UI 갱신
                
                if (event.wasClean) {
                    console.log('🔌 WebSocket 연결 정상 종료');
                } else {
                    console.log('❌ WebSocket 연결 실패 - 데모 모드로 전환');
                    if (!this.websocketErrorShown) {
                        this.showNotification('AI 서버 연결 실패: 데모 모드로 전환', 3000);
                        this.websocketErrorShown = true;
                    }
                }
                
                this.websocket = null;
                // 메시지 처리 중이라면 해제
                if (this.isProcessingMessage) {
                    this.isProcessingMessage = false;
                    this.hideTypingIndicator();
                }
            };
            
            this.websocket.onerror = (error) => {
                clearTimeout(connectionTimeout);
                console.log('❌ WebSocket 오류 발생:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false); // 항상 UI 갱신
                
                // 오류 메시지를 한 번만 표시
                if (!this.websocketErrorShown) {
                    this.showNotification('AI 서버 연결 오류: 데모 모드로 전환', 3000);
                    this.websocketErrorShown = true;
                }
                
                this.websocket = null;
                // 메시지 처리 중이라면 해제
                if (this.isProcessingMessage) {
                    this.isProcessingMessage = false;
                    this.hideTypingIndicator();
                }
            };
            
        } catch (error) {
            clearTimeout(connectionTimeout);
            console.log('❌ WebSocket 생성 실패:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.websocket = null;
            if (!this.websocketErrorShown) {
                this.showNotification('AI 서버 연결 오류: 데모 모드로 전환', 3000);
                this.websocketErrorShown = true;
            }
            
            // 메시지 처리 중이라면 해제
            if (this.isProcessingMessage) {
                this.isProcessingMessage = false;
                this.hideTypingIndicator();
            }
        }
    }

    handleWebSocketMessage(data) {
        console.log('WebSocket 메시지 수신:', data);
        
        this.hideTypingIndicator();
        
        switch (data.type) {
            case 'chat_response':
                // 메시지 sanitization
                const sanitizedMessage = this.sanitizeMessage(data.message);
                this.addMessageToChat(sanitizedMessage, 'ai');
                this.isProcessingMessage = false; // 처리 완료
                break;
            case 'system':
                // 시스템 메시지 처리 (대기 메시지 등)
                const sanitizedSystemMessage = this.sanitizeMessage(data.message);
                this.addMessageToChat(sanitizedSystemMessage, 'system');
                // 시스템 메시지는 처리 상태를 변경하지 않음
                break;
            case 'error':
                // 오류 메시지 sanitization
                const sanitizedError = this.sanitizeMessage(data.message);
                this.showNotification(`오류: ${sanitizedError}`);
                this.isProcessingMessage = false; // 오류 시 처리 완료
                break;
        }
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.dec207-status-indicator');
        const statusText = document.querySelector('.dec207-chat-status span');
        
        if (statusIndicator) {
            statusIndicator.style.background = connected ? '#00ff00' : '#ff0000';
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'AI CONNECTED' : 'DEMO MODE';
        }
    }
    
    sanitizeMessage(message) {
        if (typeof message !== 'string') {
            return '잘못된 메시지 형식';
        }
        
        // XSS 방지를 위한 기본적인 HTML 태그 제거
        return message
            .replace(/<script[^>]*>.*?<\/script>/gi, '')
            .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
            .replace(/<object[^>]*>.*?<\/object>/gi, '')
            .replace(/<embed[^>]*>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .substring(0, 10000); // 메시지 길이 제한
    }

    // ===== 유틸리티 메서드들 =====
    showNotification(message, duration = 3000) {
        // 메시지 sanitization
        const sanitizedMessage = this.sanitizeMessage(message);
        
        const notification = document.createElement('div');
        notification.className = 'dec207-notification';
        notification.textContent = sanitizedMessage;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #000000;
            color: #ffffff;
            padding: 8px 16px;
            border: 2px solid #ffffff;
            font-family: 'VT323', monospace;
            font-size: 14px;
            z-index: 9999;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, duration);
    }

    showDialog(options = {}) {
        const { title = 'Dialog', message = '', buttons = ['OK'] } = options;
        return new Promise((resolve) => {
            alert(message);
            resolve(buttons[0]);
        });
    }

    addToConversationHistory(role, message) {
        const conversationRole = role === 'ai' ? 'assistant' : role;
        this.conversationHistory.push({
            role: conversationRole,
            content: message,
            timestamp: new Date().toISOString()
        });
        
        if (this.conversationHistory.length > this.maxHistoryLength) {
            this.conversationHistory = this.conversationHistory.slice(-this.maxHistoryLength);
        }
    }
    
    getConversationHistoryForAI() {
        return this.conversationHistory
            .slice(-10)
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));
    }
    
    clearChatHistory() {
        this.conversationHistory = [];
        const chatMessages = document.querySelector('.dec207-chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        this.showNotification('채팅 기록이 삭제되었습니다.');
    }

    showWelcomeMessage() {
        console.log('Dec207Hub 초기화 완료');
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
    }

    connectBlender() {
        this.showNotification('Blender MCP 연결 중...');
    }

    connectUnity() {
        this.showNotification('Unity MCP 연결 중...');
    }
}

// ===== AUTO INITIALIZATION =====
try {
    const dec207Hub = new Dec207Hub();
} catch (e) {
    console.error('Dec207Hub 초기화 중 치명적인 오류 발생:', e);
    alert('Dec207Hub 로딩 중 오류가 발생했습니다. 자세한 내용은 콘솔을 확인해주세요.');
}

// ===== GLOBAL HELPERS =====
window.Dec207Hub = {
    showDialog: (options) => dec207Hub.showDialog(options),
    showNotification: (message, duration) => dec207Hub.showNotification(message, duration),
    toggleTheme: () => dec207Hub.toggleTheme(),
    clearChat: () => dec207Hub.clearChatHistory(),
    connectBlender: () => dec207Hub.connectBlender(),
    connectUnity: () => dec207Hub.connectUnity()
};

// ===== EVENT LISTENERS =====
document.addEventListener('dec207-menu-click', (e) => {
    console.log('Menu clicked:', e.detail.menu);
});

document.addEventListener('dec207-button-click', (e) => {
    console.log('Button clicked:', e.detail.button.textContent);
});

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 'l':
                e.preventDefault();
                e.stopPropagation();
                Dec207Hub.clearChat();
                break;
        }
    }
});

// ===== 전역 안전장치: 리다이렉트 방지 =====
document.addEventListener('DOMContentLoaded', () => {
    // 모든 폼에 대한 기본 제출 동작 차단
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (form.classList.contains('dec207-chat-form')) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    });
    
    console.log('✅ 전역 안전장치 활성화: 리다이렉트 방지');
});

console.log('Dec207Hub v2.1 로드 완료 - 엔터 키 리다이렉트 문제 해결됨');
