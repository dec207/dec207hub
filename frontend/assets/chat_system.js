/**
 * Dec207Hub - Chat System
 * 채팅 메시지 처리, 포맷팅, 히스토리 관리 (알림 최소화)
 */

class ChatSystem {
    constructor() {
        this.conversationHistory = [];
        this.isProcessingMessage = false;
        this.demoResponseTimer = null;
        this.init();
    }

    init() {
        this.setupChat();
        this.showWelcomeMessage();
    }

    // ===== 채팅 설정 =====
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
        
        // 엔터 키 처리
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

    // ===== 메시지 전송 =====
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
            
            // Send to AI (WebSocket or Demo)
            this.sendToAI(message);
        } catch (error) {
            console.error('메시지 전송 오류:', error);
            this.isProcessingMessage = false;
        }
    }

    sendToAI(message) {
        console.log('AI 전송 시작:', { message, isConnected: window.websocketClient?.isConnected });
        
        // WebSocket 전송 시도
        const sent = window.websocketClient?.sendMessage(message, this.getConversationHistoryForAI());
        
        if (!sent) {
            console.log('WebSocket 전송 실패, 데모 모드로 전환');
            this.simulateDemoResponse(message);
        }
    }

    // ===== 메시지 추가 =====
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
            messageEl.innerHTML = `<strong>[시스템]</strong> ${message}`;
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
        
        // 가벼운 애니메이션
        messageEl.style.opacity = '0.8';
        setTimeout(() => {
            messageEl.style.transition = 'opacity 0.2s ease';
            messageEl.style.opacity = '1';
        }, 10);
    }

    // ===== 메시지 포맷팅 =====
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

    // ===== 타이핑 인디케이터 =====
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

    // ===== 데모 응답 =====
    simulateDemoResponse(message) {
        console.log('데모 응답 시뮬레이션 시작');
        
        if (this.demoResponseTimer) {
            clearTimeout(this.demoResponseTimer);
        }
        
        const delay = DEC207_CONFIG.TYPING_DELAY_MIN + 
                     Math.random() * (DEC207_CONFIG.TYPING_DELAY_MAX - DEC207_CONFIG.TYPING_DELAY_MIN);
        
        this.demoResponseTimer = setTimeout(() => {
            try {
                this.hideTypingIndicator();
                
                const randomResponse = DEMO_RESPONSES[Math.floor(Math.random() * DEMO_RESPONSES.length)];
                console.log('데모 응답 생성:', randomResponse.substring(0, 50) + '...');
                
                this.addMessageToChat(randomResponse, 'ai');
                
                // TTS 처리
                if (window.voiceHandler?.isTTSActive()) {
                    const cleanText = window.voiceHandler.cleanTextForTTS(randomResponse);
                    window.voiceHandler.speak(cleanText);
                }
            } catch (error) {
                console.error('데모 응답 생성 오류:', error);
                this.addMessageToChat('죄송합니다. 응답 생성 중 오류가 발생했습니다.', 'ai');
            } finally {
                console.log('메시지 처리 완료');
                this.isProcessingMessage = false;
                this.demoResponseTimer = null;
            }
        }, delay);
    }

    // ===== WebSocket 메시지 처리 =====
    handleWebSocketMessage(data) {
        this.hideTypingIndicator();
        
        switch (data.type) {
            case 'chat_response':
                const sanitizedMessage = this.sanitizeMessage(data.message);
                this.addMessageToChat(sanitizedMessage, 'ai');
                this.isProcessingMessage = false;

                // TTS 처리
                if (window.voiceHandler?.isTTSActive()) {
                    const cleanText = window.voiceHandler.cleanTextForTTS(sanitizedMessage);
                    window.voiceHandler.speak(cleanText);
                }
                break;
                
            case 'system':
                const sanitizedSystemMessage = this.sanitizeMessage(data.message);
                this.addMessageToChat(sanitizedSystemMessage, 'system');
                break;
                
            case 'error':
                const sanitizedError = this.sanitizeMessage(data.message);
                console.error('WebSocket 오류:', sanitizedError);
                // 오류 알림 메시지 제거 - 콘솔 로그만
                this.isProcessingMessage = false;
                break;
        }
    }

    sanitizeMessage(message) {
        if (typeof message !== 'string') {
            return '잘못된 메시지 형식';
        }
        
        return message
            .replace(/<script[^>]*>.*?<\/script>/gi, '')
            .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
            .replace(/<object[^>]*>.*?<\/object>/gi, '')
            .replace(/<embed[^>]*>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .substring(0, DEC207_CONFIG.MAX_MESSAGE_LENGTH);
    }

    // ===== 대화 히스토리 관리 =====
    addToConversationHistory(role, message) {
        const conversationRole = role === 'ai' ? 'assistant' : role;
        this.conversationHistory.push({
            role: conversationRole,
            content: message,
            timestamp: new Date().toISOString()
        });
        
        if (this.conversationHistory.length > DEC207_CONFIG.MAX_HISTORY_LENGTH) {
            this.conversationHistory = this.conversationHistory.slice(-DEC207_CONFIG.MAX_HISTORY_LENGTH);
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
        console.log('채팅 기록이 삭제되었습니다');
        // 알림 메시지 제거 - 콘솔 로그만
    }

    showWelcomeMessage() {
        console.log('Dec207Hub 채팅 시스템 초기화 완료');
    }
}

// 전역 인스턴스 생성
window.chatSystem = new ChatSystem();

// 전역 헬퍼 함수
window.Dec207Chat = {
    clearChat: () => window.chatSystem.clearChatHistory(),
    sendMessage: (message) => {
        const chatInput = document.querySelector('#chat-input-field');
        if (chatInput) {
            chatInput.value = message;
            window.chatSystem.sendMessage();
        }
    }
};
