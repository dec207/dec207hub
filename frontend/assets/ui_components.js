/**
 * Dec207Hub - UI Components and Utilities
 * UI 컴포넌트, 메뉴, 버튼, 알림 시스템 (MCP 기능 비활성화)
 */

class UIComponents {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.setupMenus();
        this.setupButtons();
        this.setupMobileViewport();
        this.setupGlobalSafeGuards();
        this.setupKeyboardShortcuts();
    }

    // ===== 메뉴 시스템 =====
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

    // ===== 버튼 시스템 =====
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
            // 전송 버튼은 chat_system.js에서 처리하므로 여기서는 애니메이션만
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
        }, DEC207_CONFIG.CLICK_ANIMATION_DURATION);
    }

    // ===== 모바일 뷰포트 =====
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

    // ===== 알림 시스템 =====
    showNotification(message, duration = DEC207_CONFIG.NOTIFICATION_DURATION) {
        // 메시지 sanitization
        const sanitizedMessage = this.sanitizeMessage(message);
        
        const notification = document.createElement('div');
        notification.className = 'dec207-notification';
        notification.textContent = sanitizedMessage;
        notification.style.cssText = DEC207_CONFIG.NOTIFICATION_STYLE;

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

    // ===== 유틸리티 메서드 =====
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
            .substring(0, DEC207_CONFIG.MAX_MESSAGE_LENGTH);
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.dec207-status-indicator');
        const statusText = document.querySelector('.dec207-chat-status span');
        
        if (statusIndicator) {
            statusIndicator.style.background = connected ? '#00ff00' : '#ff0000';
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'AI CONNECTED' : 'CHAT ONLY';
        }
    }

    // ===== 테마 토글 =====
    toggleTheme() {
        document.body.classList.toggle('dark-mode');
    }

    // ===== 전역 안전장치 =====
    setupGlobalSafeGuards() {
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
    }

    // ===== 키보드 단축키 =====
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'l':
                        e.preventDefault();
                        e.stopPropagation();
                        if (window.chatSystem) {
                            window.chatSystem.clearChatHistory();
                        }
                        break;
                }
            }
        });
    }

    // ===== MCP 연결 메서드 (비활성화) =====
    connectBlender() {
        this.showDialog({
            title: 'Blender MCP 연결',
            message: `
                <div style="text-align: left;">
                    <h4>⚠️ MCP 기능 비활성화</h4>
                    <p>현재 MCP (Model Context Protocol) 기능이 비활성화되어 있습니다.</p>
                    <br>
                    <p><strong>사용 가능한 기능:</strong></p>
                    <ul>
                        <li>일상 대화</li>
                        <li>질문 답변</li>
                        <li>텍스트 기반 도움말</li>
                        <li>간단한 계산</li>
                    </ul>
                    <br>
                    <p><em>Blender 연결은 현재 지원되지 않습니다.</em></p>
                </div>
            `,
            buttons: ['확인']
        });
    }

    connectUnity() {
        this.showDialog({
            title: 'Unity MCP 연결',
            message: `
                <div style="text-align: left;">
                    <h4>⚠️ MCP 기능 비활성화</h4>
                    <p>현재 MCP (Model Context Protocol) 기능이 비활성화되어 있습니다.</p>
                    <br>
                    <p><strong>사용 가능한 기능:</strong></p>
                    <ul>
                        <li>일상 대화</li>
                        <li>질문 답변</li>
                        <li>텍스트 기반 도움말</li>
                        <li>간단한 계산</li>
                    </ul>
                    <br>
                    <p><em>Unity 연결은 현재 지원되지 않습니다.</em></p>
                </div>
            `,
            buttons: ['확인']
        });
    }
}

// 전역 인스턴스 생성
window.uiComponents = new UIComponents();

// 전역 헬퍼 함수 노출
window.Dec207UI = {
    showDialog: (options) => window.uiComponents.showDialog(options),
    showNotification: (message, duration) => window.uiComponents.showNotification(message, duration),
    toggleTheme: () => window.uiComponents.toggleTheme(),
    connectBlender: () => window.uiComponents.connectBlender(),
    connectUnity: () => window.uiComponents.connectUnity()
};
