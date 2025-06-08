/**
 * Dec207Hub - Retro Mac JavaScript Framework
 * AI 채팅 허브를 위한 레트로 Mac OS 스타일 웹 컴포넌트 라이브러리
 * Created by dec207
 */

class Dec207Hub {
    constructor() {
        this.windows = [];
        this.activeWindow = null;
        this.zIndexCounter = 10;
        this.chatHistory = [];
        this.isConnected = false;
        this.isRecording = false;
        this.recognition = null;
        this.synthesis = null;
        this.websocket = null;
        
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupWindows();
            this.setupMenus();
            this.setupButtons();
            this.setupSidebar();
            this.setupChat();
            this.setupVoice();
            this.setupWebSocket();
            this.showWelcomeMessage();
        });
    }

    // ===== WINDOW MANAGEMENT =====
    setupWindows() {
        const windows = document.querySelectorAll('.dec207-window');
        windows.forEach(windowEl => {
            this.registerWindow(windowEl);
        });
    }

    registerWindow(windowEl) {
        const windowObj = {
            element: windowEl,
            isMinimized: false,
            isMaximized: false,
            originalStyle: {
                width: windowEl.style.width,
                height: windowEl.style.height,
                top: windowEl.style.top,
                left: windowEl.style.left
            }
        };

        this.windows.push(windowObj);
        this.setupWindowControls(windowObj);
        this.makeDraggable(windowObj);
        
        windowEl.addEventListener('mousedown', () => {
            this.focusWindow(windowObj);
        });
    }

    setupWindowControls(windowObj) {
        const windowEl = windowObj.element;
        const controls = windowEl.querySelectorAll('.dec207-control-btn');
        
        controls.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.textContent.trim();
                
                switch(action) {
                    case '×':
                        this.closeWindow(windowObj);
                        break;
                    case '-':
                        this.minimizeWindow(windowObj);
                        break;
                    case '□':
                        this.toggleMaximize(windowObj);
                        break;
                }
            });
        });
    }

    closeWindow(windowObj) {
        windowObj.element.style.display = 'none';
        this.windows = this.windows.filter(w => w !== windowObj);
    }

    minimizeWindow(windowObj) {
        if (windowObj.isMinimized) {
            windowObj.element.style.display = 'block';
            windowObj.isMinimized = false;
        } else {
            windowObj.element.style.display = 'none';
            windowObj.isMinimized = true;
        }
    }

    toggleMaximize(windowObj) {
        const windowEl = windowObj.element;
        
        if (windowObj.isMaximized) {
            windowEl.classList.remove('fullscreen');
            windowEl.style.width = windowObj.originalStyle.width || '80%';
            windowEl.style.height = windowObj.originalStyle.height || '75%';
            windowEl.style.top = windowObj.originalStyle.top || '10%';
            windowEl.style.left = windowObj.originalStyle.left || '10%';
            windowObj.isMaximized = false;
        } else {
            windowEl.classList.add('fullscreen');
            windowObj.isMaximized = true;
        }
    }

    focusWindow(windowObj) {
        // Remove active class from all title bars
        this.windows.forEach(w => {
            w.element.querySelector('.dec207-title-bar')?.classList.remove('active');
        });
        
        // Add active class to current window
        this.activeWindow = windowObj;
        windowObj.element.style.zIndex = ++this.zIndexCounter;
        windowObj.element.querySelector('.dec207-title-bar')?.classList.add('active');
    }

    makeDraggable(windowObj) {
        const windowEl = windowObj.element;
        const titleBar = windowEl.querySelector('.dec207-title-bar');
        
        if (!titleBar) return;

        let isDragging = false;
        let currentX = 0;
        let currentY = 0;
        let initialX = 0;
        let initialY = 0;

        titleBar.addEventListener('mousedown', (e) => {
            if (windowObj.isMaximized) return;
            
            isDragging = true;
            initialX = e.clientX - windowEl.offsetLeft;
            initialY = e.clientY - windowEl.offsetTop;
            
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', stopDrag);
        });

        function drag(e) {
            if (!isDragging) return;
            
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            windowEl.style.left = currentX + 'px';
            windowEl.style.top = currentY + 'px';
        }

        function stopDrag() {
            isDragging = false;
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('mouseup', stopDrag);
        }
    }

    // ===== CHAT SYSTEM =====
    setupChat() {
        const chatInput = document.querySelector('.dec207-input-field');
        const sendBtn = document.querySelector('.dec207-btn.primary');
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }
    }

    sendMessage() {
        const chatInput = document.querySelector('.dec207-input-field');
        const message = chatInput?.value.trim();
        
        if (!message) return;
        
        // Clear input
        chatInput.value = '';
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to AI (WebSocket or API)
        this.sendToAI(message);
    }

    addMessageToChat(message, sender) {
        const chatMessages = document.querySelector('.dec207-chat-messages');
        if (!chatMessages) return;
        
        const messageEl = document.createElement('div');
        messageEl.className = `dec207-message ${sender}`;
        
        // Format message based on sender
        if (sender === 'system') {
            messageEl.innerHTML = `<strong>[SYSTEM]</strong> ${message}`;
        } else {
            messageEl.textContent = message;
        }
        
        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to history
        this.chatHistory.push({ message, sender, timestamp: new Date() });
        
        // Animate new message
        messageEl.style.opacity = '0';
        messageEl.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageEl.style.transition = 'all 0.3s ease';
            messageEl.style.opacity = '1';
            messageEl.style.transform = 'translateY(0)';
        }, 50);
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
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            // Send via WebSocket
            this.websocket.send(JSON.stringify({
                type: 'chat',
                message: message,
                timestamp: new Date().toISOString()
            }));
        } else {
            // Fallback: simulate AI response for demo
            setTimeout(() => {
                this.hideTypingIndicator();
                
                const responses = [
                    "안녕하세요! Dec207Hub AI 어시스턴트입니다. 어떻게 도와드릴까요?",
                    "흥미로운 질문이네요. 더 자세히 설명해 주시겠어요?",
                    "네, 이해했습니다. 다른 질문이 있으시면 언제든 말씀해 주세요.",
                    "Dec207Hub의 MCP 연동 기능을 통해 Blender나 Unity와 연결할 수 있습니다.",
                    "음성 인식 기능도 지원됩니다. 마이크 버튼을 눌러보세요!",
                    "레트로 Mac OS 스타일이 마음에 드시나요? 🤖"
                ];
                
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                this.addMessageToChat(randomResponse, 'ai');
                
                // Optional: TTS
                if (this.synthesis) {
                    this.speak(randomResponse);
                }
            }, 1000 + Math.random() * 2000); // 1-3초 랜덤 딜레이
        }
    }

    // ===== VOICE SYSTEM =====
    setupVoice() {
        // Speech Recognition 설정
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'ko-KR';
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.updateVoiceButton(true);
                this.showNotification('음성 인식 시작됨');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const chatInput = document.querySelector('.dec207-input-field');
                if (chatInput) {
                    chatInput.value = transcript;
                    this.sendMessage();
                }
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
                this.updateVoiceButton(false);
            };
            
            this.recognition.onerror = (event) => {
                this.isRecording = false;
                this.updateVoiceButton(false);
                this.showNotification(`음성 인식 오류: ${event.error}`);
            };
        }
        
        // Speech Synthesis 설정
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
        }
        
        // Voice button 이벤트
        const micBtn = document.querySelector('.dec207-voice-btn.mic');
        const speakerBtn = document.querySelector('.dec207-voice-btn.speaker');
        
        if (micBtn) {
            micBtn.addEventListener('click', () => {
                this.toggleRecording();
            });
        }
        
        if (speakerBtn) {
            speakerBtn.addEventListener('click', () => {
                this.toggleTTS();
            });
        }
    }

    toggleRecording() {
        if (!this.recognition) {
            this.showNotification('음성 인식이 지원되지 않습니다.');
            return;
        }
        
        if (this.isRecording) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateVoiceButton(isActive) {
        const micBtn = document.querySelector('.dec207-voice-btn.mic');
        if (micBtn) {
            if (isActive) {
                micBtn.classList.add('active');
                micBtn.textContent = '🔴';
            } else {
                micBtn.classList.remove('active');
                micBtn.textContent = '🎤';
            }
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
            speakerBtn.classList.toggle('active');
            
            if (speakerBtn.classList.contains('active')) {
                this.showNotification('TTS 활성화됨');
                speakerBtn.textContent = '🔊';
            } else {
                this.showNotification('TTS 비활성화됨');
                speakerBtn.textContent = '🔇';
            }
        }
    }

    // ===== WEBSOCKET CONNECTION =====
    setupWebSocket() {
        const wsUrl = 'ws://localhost:8000/ws'; // Backend WebSocket URL
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.showNotification('서버에 연결되었습니다.');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.showNotification('서버 연결이 끊어졌습니다.');
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showNotification('연결 오류가 발생했습니다.');
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.showNotification('서버에 연결할 수 없습니다. 로컬 모드로 실행됩니다.');
        }
    }

    handleWebSocketMessage(data) {
        this.hideTypingIndicator();
        
        switch (data.type) {
            case 'chat_response':
                this.addMessageToChat(data.message, 'ai');
                if (this.synthesis && document.querySelector('.dec207-voice-btn.speaker.active')) {
                    this.speak(data.message);
                }
                break;
            case 'system':
                this.addMessageToChat(data.message, 'system');
                break;
            case 'error':
                this.showNotification(`오류: ${data.message}`);
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
            statusText.textContent = connected ? 'CONNECTED' : 'OFFLINE';
        }
    }

    // ===== MENU SYSTEM =====
    setupMenus() {
        const menuItems = document.querySelectorAll('.dec207-menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                this.handleMenuClick(item);
            });
        });
    }

    handleMenuClick(menuItem) {
        const menuText = menuItem.textContent.toLowerCase();
        
        switch (menuText) {
            case 'file':
                this.showFileMenu();
                break;
            case 'edit':
                this.showEditMenu();
                break;
            case 'view':
                this.showViewMenu();
                break;
            case 'help':
                this.showHelpDialog();
                break;
            case 'blender':
                this.openBlenderMCP();
                break;
            case 'unity':
                this.openUnityMCP();
                break;
        }
        
        // Custom event
        const event = new CustomEvent('dec207-menu-click', {
            detail: { menu: menuText, element: menuItem }
        });
        document.dispatchEvent(event);
    }

    // ===== BUTTON SYSTEM =====
    setupButtons() {
        const buttons = document.querySelectorAll('.dec207-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleButtonClick(btn, e);
            });
        });
    }

    handleButtonClick(button, event) {
        // Click animation
        button.style.transform = 'translateY(1px)';
        setTimeout(() => {
            button.style.transform = '';
        }, 100);

        // Custom event
        const customEvent = new CustomEvent('dec207-button-click', {
            detail: { button, originalEvent: event }
        });
        document.dispatchEvent(customEvent);
    }

    // ===== SIDEBAR SYSTEM =====
    setupSidebar() {
        const sidebarItems = document.querySelectorAll('.dec207-sidebar-item');
        sidebarItems.forEach(item => {
            item.addEventListener('click', () => {
                this.selectSidebarItem(item);
            });
        });
    }

    selectSidebarItem(item) {
        const sidebar = item.closest('.dec207-sidebar');
        const allItems = sidebar.querySelectorAll('.dec207-sidebar-item');
        allItems.forEach(i => i.classList.remove('selected'));
        
        item.classList.add('selected');

        const event = new CustomEvent('dec207-sidebar-select', {
            detail: { item, text: item.textContent.trim() }
        });
        document.dispatchEvent(event);
    }

    // ===== DIALOG SYSTEM =====
    showDialog(options = {}) {
        const {
            title = 'Dec207Hub Dialog',
            message = '',
            buttons = ['OK'],
            type = 'info'
        } = options;

        return new Promise((resolve) => {
            const dialogEl = this.createWindow({
                title,
                width: '400px',
                height: '250px',
                content: `
                    <div class="dec207-p-3">
                        <div class="dec207-m-2" style="margin-bottom: 16px;">${message}</div>
                        <div class="dec207-flex dec207-flex-center" style="gap: 8px;">
                            ${buttons.map((btn, index) => `
                                <button class="dec207-btn ${index === 0 ? 'primary' : ''}" 
                                        data-dialog-result="${btn}">${btn}</button>
                            `).join('')}
                        </div>
                    </div>
                `
            });

            // Center dialog
            dialogEl.style.left = 'calc(50% - 200px)';
            dialogEl.style.top = 'calc(50% - 125px)';

            // Button events
            const dialogButtons = dialogEl.querySelectorAll('[data-dialog-result]');
            dialogButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const result = btn.getAttribute('data-dialog-result');
                    document.body.removeChild(dialogEl);
                    resolve(result);
                });
            });
        });
    }

    showHelpDialog() {
        this.showDialog({
            title: 'Dec207Hub - Help',
            message: `
                <div style="text-align: left;">
                    <h3>Dec207Hub AI Chat System</h3>
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Created by:</strong> dec207</p>
                    <br>
                    <p><strong>Features:</strong></p>
                    <ul>
                        <li>AI Chat with Ollama</li>
                        <li>Voice Recognition (STT)</li>
                        <li>Text-to-Speech (TTS)</li>
                        <li>MCP Integration</li>
                        <li>Blender & Unity Support</li>
                    </ul>
                </div>
            `,
            buttons: ['확인']
        });
    }

    // ===== NOTIFICATION SYSTEM =====
    showNotification(message, duration = 3000) {
        const notification = document.createElement('div');
        notification.className = 'dec207-notification';
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, duration);
    }

    // ===== WINDOW CREATION =====
    createWindow(options = {}) {
        const {
            title = 'New Window',
            content = '',
            width = '400px',
            height = '300px',
            x = '50px',
            y = '50px',
            hasMenu = false,
            icon = true
        } = options;

        const windowEl = document.createElement('div');
        windowEl.className = 'dec207-window';
        windowEl.style.width = width;
        windowEl.style.height = height;
        windowEl.style.left = x;
        windowEl.style.top = y;

        windowEl.innerHTML = `
            <div class="dec207-title-bar">
                <div class="dec207-title-bar-left">
                    ${icon ? '<div class="dec207-window-icon"></div>' : ''}
                    <span class="dec207-window-title">${title}</span>
                </div>
                <div class="dec207-window-controls">
                    <div class="dec207-control-btn">-</div>
                    <div class="dec207-control-btn">□</div>
                    <div class="dec207-control-btn">×</div>
                </div>
            </div>
            ${hasMenu ? `
                <div class="dec207-menu-bar">
                    <span class="dec207-menu-item">File</span>
                    <span class="dec207-menu-item">Edit</span>
                    <span class="dec207-menu-item">View</span>
                    <span class="dec207-menu-item">Help</span>
                </div>
            ` : ''}
            <div class="dec207-content-area ${hasMenu ? '' : 'no-menu'}">
                <div class="dec207-main-content">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(windowEl);
        this.registerWindow(windowEl);
        
        return windowEl;
    }

    // ===== MCP INTEGRATION =====
    openBlenderMCP() {
        this.showNotification('Blender MCP 연결 중...');
        // TODO: Implement Blender MCP connection
        setTimeout(() => {
            this.addMessageToChat('Blender MCP 서버에 연결되었습니다.', 'system');
        }, 1000);
    }

    openUnityMCP() {
        this.showNotification('Unity MCP 연결 중...');
        // TODO: Implement Unity MCP connection
        setTimeout(() => {
            this.addMessageToChat('Unity MCP 서버에 연결되었습니다.', 'system');
        }, 1000);
    }

    // ===== UTILITY METHODS =====
    showWelcomeMessage() {
        setTimeout(() => {
            this.addMessageToChat('Dec207Hub에 오신 것을 환영합니다! 🤖', 'system');
            this.addMessageToChat('AI 채팅, 음성 인식, MCP 연동을 지원합니다.', 'system');
        }, 1000);
    }

    playSystemSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'square';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            console.log('Audio not supported');
        }
    }

    toggleTheme() {
        document.querySelector('.dec207-desktop')?.classList.toggle('dark-mode');
        this.showNotification('테마가 변경되었습니다.');
    }

    // ===== CHAT HISTORY MANAGEMENT =====
    saveChatHistory() {
        localStorage.setItem('dec207-chat-history', JSON.stringify(this.chatHistory));
    }

    loadChatHistory() {
        const saved = localStorage.getItem('dec207-chat-history');
        if (saved) {
            this.chatHistory = JSON.parse(saved);
            this.chatHistory.forEach(entry => {
                this.addMessageToChat(entry.message, entry.sender);
            });
        }
    }

    clearChatHistory() {
        this.chatHistory = [];
        const chatMessages = document.querySelector('.dec207-chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        localStorage.removeItem('dec207-chat-history');
        this.showNotification('채팅 기록이 삭제되었습니다.');
    }
}

// ===== AUTO INITIALIZATION =====
const dec207Hub = new Dec207Hub();

// ===== GLOBAL HELPERS =====
window.Dec207Hub = {
    createWindow: (options) => dec207Hub.createWindow(options),
    showDialog: (options) => dec207Hub.showDialog(options),
    showNotification: (message, duration) => dec207Hub.showNotification(message, duration),
    playSound: () => dec207Hub.playSystemSound(),
    toggleTheme: () => dec207Hub.toggleTheme(),
    clearChat: () => dec207Hub.clearChatHistory(),
    connectBlender: () => dec207Hub.openBlenderMCP(),
    connectUnity: () => dec207Hub.openUnityMCP()
};

// ===== EVENT LISTENERS =====
document.addEventListener('dec207-menu-click', (e) => {
    console.log('Menu clicked:', e.detail.menu);
});

document.addEventListener('dec207-button-click', (e) => {
    console.log('Button clicked:', e.detail.button.textContent);
});

document.addEventListener('dec207-sidebar-select', (e) => {
    console.log('Sidebar item selected:', e.detail.text);
});

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 'n':
                e.preventDefault();
                Dec207Hub.createWindow({ title: 'New Window' });
                break;
            case 't':
                e.preventDefault();
                Dec207Hub.toggleTheme();
                break;
            case 'l':
                e.preventDefault();
                Dec207Hub.clearChat();
                break;
        }
    }
});

// ===== EXPORT FOR MODULES =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Dec207Hub;
}
