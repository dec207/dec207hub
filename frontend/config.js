// Dec207Hub 설정 파일
// 자동 감지: 로컬 접속시 localhost, 외부 접속시 서버 IP 사용

window.DEC207_SERVER_IP = 'auto';

// 수동 IP 설정을 사용하려면 위 줄을 주석 처리하고 아래 줄의 주석을 해제하세요.
// window.DEC207_SERVER_IP = '192.168.0.7';

console.log('Dec207Hub 수동 IP 설정 로드됨');
console.log('🔌 WebSocket 주소: ws://192.168.0.7:8000/ws');
