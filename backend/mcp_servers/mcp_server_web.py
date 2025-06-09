# Web Service MCP Server
# FastMCP를 사용한 웹 서비스 관리 및 제어 서버

from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import json
import psutil
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP(
    "WebService-MCP",
    host="0.0.0.0",
    port=8003,
    instructions="웹 서비스 관리 및 시스템 모니터링을 위한 MCP 서버입니다. 서버 상태 확인, 프로세스 관리, 로그 조회 등의 기능을 제공합니다."
)

# 가상의 웹 서비스 상태
web_services = {
    "Dec207Hub-Backend": {
        "status": "running",
        "port": 8000,
        "pid": 12345,
        "uptime": "2 hours 30 minutes",
        "cpu_usage": "15%",
        "memory_usage": "245MB",
        "requests_count": 1547,
        "last_error": None
    },
    "Dec207Hub-Frontend": {
        "status": "running", 
        "port": 3000,
        "pid": 12346,
        "uptime": "2 hours 28 minutes",
        "cpu_usage": "5%",
        "memory_usage": "89MB",
        "requests_count": 892,
        "last_error": None
    },
    "Ollama-Service": {
        "status": "running",
        "port": 11434,
        "pid": 12347,
        "uptime": "5 hours 12 minutes", 
        "cpu_usage": "35%",
        "memory_usage": "2.1GB",
        "requests_count": 234,
        "last_error": None
    }
}

@mcp.tool()
async def get_web_server_status() -> str:
    """
    모든 웹 서비스의 현재 상태를 조회합니다.
    """
    try:
        print(f"\n[DEBUG] Web MCP: get_server_status called\n")
        
        # 실제 시스템 정보 가져오기
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        result = f"🌐 웹 서비스 상태 대시보드\n"
        result += f"🕐 조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 시스템 정보
        result += f"💻 시스템 정보:\n"
        result += f"  • CPU 사용량: {cpu_percent}%\n"
        result += f"  • 메모리 사용량: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)\n"
        result += f"  • 디스크 사용량: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)\n\n"
        
        # 서비스별 상태
        result += f"🚀 서비스 상태:\n"
        running_services = 0
        total_requests = 0
        
        for service_name, service_info in web_services.items():
            status_emoji = "🟢" if service_info["status"] == "running" else "🔴"
            result += f"  {status_emoji} {service_name}\n"
            result += f"    - 포트: {service_info['port']}\n"
            result += f"    - 가동시간: {service_info['uptime']}\n"
            result += f"    - CPU: {service_info['cpu_usage']}, 메모리: {service_info['memory_usage']}\n"
            result += f"    - 요청 수: {service_info['requests_count']:,}개\n"
            
            if service_info["status"] == "running":
                running_services += 1
            total_requests += service_info["requests_count"]
        
        result += f"\n📊 요약:\n"
        result += f"  • 실행 중인 서비스: {running_services}/{len(web_services)}개\n"
        result += f"  • 총 처리 요청: {total_requests:,}개\n"
        result += f"  • 전체 시스템 상태: {'정상' if running_services == len(web_services) else '일부 장애'}"
        
        logger.info("웹 서버 상태 조회 완료")
        return result
        
    except Exception as e:
        error_msg = f"❌ 웹 서버 상태 조회 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def restart_web_service(service_name: str) -> str:
    """
    지정된 웹 서비스를 재시작합니다.
    
    Args:
        service_name: 재시작할 서비스 이름
    """
    try:
        print(f"\n[DEBUG] Web MCP: restart_service called - {service_name}\n")
        
        if service_name in web_services:
            # 재시작 시뮬레이션
            web_services[service_name]["status"] = "restarting"
            await asyncio.sleep(2)  # 재시작 시간 시뮬레이션
            
            web_services[service_name]["status"] = "running"
            web_services[service_name]["uptime"] = "0 minutes"
            web_services[service_name]["requests_count"] = 0
            
            result = f"🔄 서비스 '{service_name}' 재시작 완료!\n"
            result += f"📡 포트: {web_services[service_name]['port']}\n"
            result += f"🆔 프로세스 ID: {web_services[service_name]['pid']}\n"
            result += f"✅ 상태: 정상 동작\n"
            result += f"🕐 재시작 시간: {datetime.now().strftime('%H:%M:%S')}"
            
            logger.info(f"웹 서비스 재시작: {service_name}")
            return result
        else:
            available_services = list(web_services.keys())
            result = f"❌ 서비스 '{service_name}'을 찾을 수 없습니다.\n"
            result += f"📋 사용 가능한 서비스: {', '.join(available_services)}"
            return result
            
    except Exception as e:
        error_msg = f"❌ 웹 서비스 재시작 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def get_service_logs(
    service_name: str,
    lines: int = 50,
    log_level: str = "all"
) -> str:
    """
    지정된 서비스의 로그를 조회합니다.
    
    Args:
        service_name: 조회할 서비스 이름
        lines: 조회할 로그 라인 수
        log_level: 로그 레벨 (error, warning, info, all)
    """
    try:
        print(f"\n[DEBUG] Web MCP: get_service_logs called - {service_name}\n")
        
        if service_name not in web_services:
            available_services = list(web_services.keys())
            result = f"❌ 서비스 '{service_name}'을 찾을 수 없습니다.\n"
            result += f"📋 사용 가능한 서비스: {', '.join(available_services)}"
            return result
        
        # 가상의 로그 생성 (실제로는 로그 파일 읽기)
        sample_logs = [
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {service_name} started successfully",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Listening on port {web_services[service_name]['port']}",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Request processed: GET /api/health",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WebSocket connection established",
            f"[WARNING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - High CPU usage detected: 85%",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Request processed: POST /api/chat",
            f"[ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Failed to connect to external API",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Cache cleared successfully",
            f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Health check passed"
        ]
        
        # 로그 레벨 필터링
        if log_level != "all":
            filtered_logs = [log for log in sample_logs if f"[{log_level.upper()}]" in log]
        else:
            filtered_logs = sample_logs
        
        # 라인 수 제한
        recent_logs = filtered_logs[-lines:]
        
        result = f"📋 {service_name} 서비스 로그 (최근 {len(recent_logs)}줄)\n"
        result += f"🔍 필터: {log_level}\n"
        result += f"🕐 조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += "=" * 60 + "\n"
        
        for log_line in recent_logs:
            result += f"{log_line}\n"
            
        result += "=" * 60
        
        logger.info(f"서비스 로그 조회: {service_name} ({len(recent_logs)}줄)")
        return result
        
    except Exception as e:
        error_msg = f"❌ 서비스 로그 조회 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def monitor_system_resources() -> str:
    """
    시스템 리소스 사용량을 실시간으로 모니터링합니다.
    """
    try:
        print(f"\n[DEBUG] Web MCP: monitor_system_resources called\n")
        
        # 시스템 정보 수집
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # 프로세스 정보
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 1.0:  # CPU 사용량 1% 이상인 프로세스만
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 상위 5개 프로세스
        top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        
        result = f"📊 시스템 리소스 모니터링\n"
        result += f"🕐 조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # CPU 정보
        result += f"🔥 CPU 사용량: {cpu_percent}%\n"
        cpu_bar = "█" * int(cpu_percent // 5) + "░" * (20 - int(cpu_percent // 5))
        result += f"   [{cpu_bar}] {cpu_percent}%\n\n"
        
        # 메모리 정보
        memory_percent = memory.percent
        result += f"💾 메모리 사용량: {memory_percent}%\n"
        result += f"   사용량: {memory.used // 1024**3}GB / {memory.total // 1024**3}GB\n"
        memory_bar = "█" * int(memory_percent // 5) + "░" * (20 - int(memory_percent // 5))
        result += f"   [{memory_bar}] {memory_percent}%\n\n"
        
        # 디스크 정보
        disk_percent = disk.percent
        result += f"💿 디스크 사용량: {disk_percent}%\n"
        result += f"   사용량: {disk.used // 1024**3}GB / {disk.total // 1024**3}GB\n"
        disk_bar = "█" * int(disk_percent // 5) + "░" * (20 - int(disk_percent // 5))
        result += f"   [{disk_bar}] {disk_percent}%\n\n"
        
        # 네트워크 정보
        result += f"🌐 네트워크:\n"
        result += f"   송신: {network.bytes_sent // 1024**2}MB\n"
        result += f"   수신: {network.bytes_recv // 1024**2}MB\n\n"
        
        # 상위 프로세스
        result += f"⚡ 상위 CPU 사용 프로세스:\n"
        for i, proc in enumerate(top_processes, 1):
            result += f"   {i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}%\n"
        
        logger.info("시스템 리소스 모니터링 완료")
        return result
        
    except Exception as e:
        error_msg = f"❌ 시스템 리소스 모니터링 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def backup_service_data(service_name: str, backup_path: str = "backups/") -> str:
    """
    서비스 데이터를 백업합니다.
    
    Args:
        service_name: 백업할 서비스 이름
        backup_path: 백업 저장 경로
    """
    try:
        print(f"\n[DEBUG] Web MCP: backup_service_data called - {service_name}\n")
        
        if service_name not in web_services:
            available_services = list(web_services.keys())
            result = f"❌ 서비스 '{service_name}'을 찾을 수 없습니다.\n"
            result += f"📋 사용 가능한 서비스: {', '.join(available_services)}"
            return result
        
        # 백업 시뮬레이션
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{service_name}_backup_{timestamp}.tar.gz"
        full_backup_path = os.path.join(backup_path, backup_filename)
        
        await asyncio.sleep(1)  # 백업 시간 시뮬레이션
        
        result = f"💾 서비스 데이터 백업 완료!\n"
        result += f"📁 서비스: {service_name}\n"
        result += f"📄 백업 파일: {backup_filename}\n"
        result += f"📍 저장 경로: {full_backup_path}\n"
        result += f"🕐 백업 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"📊 포함 데이터:\n"
        result += f"   • 설정 파일\n"
        result += f"   • 로그 파일\n"
        result += f"   • 사용자 데이터\n"
        result += f"   • 캐시 데이터"
        
        logger.info(f"서비스 데이터 백업: {service_name}")
        return result
        
    except Exception as e:
        error_msg = f"❌ 서비스 데이터 백업 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    print("🌐 웹 서비스 MCP 서버 시작 중...")
    print("📡 포트: 8003")
    print("🔧 사용 가능한 도구:")
    print("  • get_web_server_status - 서버 상태 조회")
    print("  • restart_web_service - 서비스 재시작")
    print("  • get_service_logs - 서비스 로그 조회")
    print("  • monitor_system_resources - 시스템 리소스 모니터링")
    print("  • backup_service_data - 서비스 데이터 백업")
    print("=" * 50)
    
    mcp.run(transport="stdio")
