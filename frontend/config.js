// Dec207Hub 설정 파일
// 자동 감지: 로컬 접속시 localhost, 외부 접속시 서버 IP 사용

// 수동 IP 설정 (서버 IP 주소로 변경)
window.DEC207_SERVER_IP = '192.168.0.7';

// 자동 감지 모드를 사용하려면 주석 처리
// window.DEC207_SERVER_IP = 'auto';

console.log('Dec207Hub 수동 IP 설정 로드됨');
console.log('🔌 WebSocket 주소: ws://192.168.0.7:8000/ws');
