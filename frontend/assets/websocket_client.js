/**
 * Dec207Hub - WebSocket Client
 * WebSocket 연결 관리 및 실시간 통신 (알림 메시지 최소화)
 */

class WebSocketClient {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.websocketAttempted = false;
        this.websocketErrorShown = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 5000;
        this.initialConnectionMessageShown = false;
    }

    // ===== WebSocket 연결 =====
    setupWebSocket() {
        // 중복 연결 방지
        if (this.websocketAttempted) {
            console.log('WebSocket 연결 이미 시도됨, 재시도 안함');
            return;
        }
        this.websocketAttempted = true;

        const serverIP = this.determineServerIP();
        const wsUrl = `ws://${serverIP}:${DEC207_CONFIG.SERVER_PORT}/ws`;
        
        console.log('🔌 WebSocket 연결 시도:', wsUrl);
        
        this.connectWebSocket(wsUrl);
    }

    determineServerIP() {
        let serverIP = '192.168.0.7'; // 기본값
        
        // config.js 설정 확인
        if (DEC207_CONFIG.SERVER_IP && DEC207_CONFIG.SERVER_IP !== 'auto') {
            serverIP = DEC207_CONFIG.SERVER_IP;
            console.log('config.js에서 지정된 IP 사용:', serverIP);
        } else {
            // 자동 감지 로직
            if (window.location.protocol !== 'file:') {
                // 웹서버에서 실행 중일 때
                serverIP = window.location.hostname;
                console.log('웹서버 hostname 사용:', serverIP);
            } else {
                // file:// 프로토콜일 때 기본값 사용
                serverIP = '192.168.0.7';
                console.log('file:// 프로토콜 - 기본 IP 사용:', serverIP);
            }
        }
        
        return serverIP;
    }

    connectWebSocket(wsUrl) {
        // 연결 타임아웃 설정
        const connectionTimeout = setTimeout(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
                console.log('⏰ WebSocket 연결 타임아웃, 데모 모드로 전환');
                this.websocket.close();
                this.handleConnectionFailure();
            }
        }, DEC207_CONFIG.WEBSOCKET_TIMEOUT);

        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                clearTimeout(connectionTimeout);
                this.handleConnectionSuccess();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event);
            };
            
            this.websocket.onclose = (event) => {
                clearTimeout(connectionTimeout);
                this.handleConnectionClose(event);
            };
            
            this.websocket.onerror = (error) => {
                clearTimeout(connectionTimeout);
                this.handleConnectionError(error);
            };
            
        } catch (error) {
            clearTimeout(connectionTimeout);
            console.log('❌ WebSocket 생성 실패:', error);
            this.handleConnectionFailure();
        }
    }

    // ===== 연결 이벤트 처리 =====
    handleConnectionSuccess() {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateConnectionStatus(true);
        console.log('✅ WebSocket 연결 성공!');
        
        // 알림 메시지 제거 - 콘솔 로그만 남김
    }

    handleConnectionClose(event) {
        this.isConnected = false;
        this.updateConnectionStatus(false);
        
        if (event.wasClean) {
            console.log('🔌 WebSocket 연결 정상 종료');
        } else {
            console.log('❌ WebSocket 연결 실패 - 데모 모드로 전환');
            this.handleConnectionFailure();
        }
        
        this.websocket = null;
        this.resetProcessingState();
    }

    handleConnectionError(error) {
        console.log('❌ WebSocket 오류 발생:', error);
        this.handleConnectionFailure();
    }

    handleConnectionFailure() {
        this.isConnected = false;
        this.updateConnectionStatus(false);
        this.websocket = null;
        this.resetProcessingState();
        
        // 오류 알림 메시지 완전 제거 - 콘솔 로그만
        console.log('WebSocket 연결 실패: 데모 모드로 동작합니다');

        // 재연결 시도 (선택적)
        this.attemptReconnect();
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.websocketAttempted = false;
                this.setupWebSocket();
            }, this.reconnectDelay);
        } else {
            console.log('🔄 최대 재연결 시도 횟수 초과, 데모 모드 유지');
        }
    }

    // ===== 메시지 처리 =====
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket 메시지 수신:', data);
            
            if (window.chatSystem) {
                window.chatSystem.handleWebSocketMessage(data);
            }
        } catch (error) {
            console.error('WebSocket 메시지 파싱 오류:', error);
        }
    }

    // ===== 메시지 전송 =====
    sendMessage(message, conversationHistory = []) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            const payload = {
                type: 'chat',
                message: message,
                conversation_history: conversationHistory,
                timestamp: new Date().toISOString()
            };
            
            console.log('WebSocket 전송:', payload);
            this.websocket.send(JSON.stringify(payload));
            return true;
        }
        
        return false;
    }

    // ===== 상태 관리 =====
    updateConnectionStatus(connected) {
        if (window.uiComponents) {
            window.uiComponents.updateConnectionStatus(connected);
        }
    }

    resetProcessingState() {
        if (window.chatSystem && window.chatSystem.isProcessingMessage) {
            window.chatSystem.isProcessingMessage = false;
            window.chatSystem.hideTypingIndicator();
        }
    }

    addSystemMessage(message) {
        if (window.chatSystem) {
            window.chatSystem.addMessageToChat(message, 'system');
        }
    }

    // ===== 연결 상태 확인 =====
    isWebSocketConnected() {
        return this.websocket && this.websocket.readyState === WebSocket.OPEN;
    }

    // ===== 수동 재연결 =====
    manualReconnect() {
        console.log('🔄 수동 재연결 시도');
        
        if (this.websocket) {
            this.websocket.close();
        }
        
        this.websocketAttempted = false;
        this.websocketErrorShown = false;
        this.reconnectAttempts = 0;
        
        setTimeout(() => {
            this.setupWebSocket();
        }, 1000);
    }

    // ===== 연결 종료 =====
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }
}

// 전역 인스턴스 생성
window.websocketClient = new WebSocketClient();
