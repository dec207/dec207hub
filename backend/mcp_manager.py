# MCP Manager - MCP 기능 비활성화 (일상 대화만 지원)

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self, config_path: str = "../config/mcp_config.json"):
        """MCP 매니저 초기화 - 기능 비활성화"""
        self.available_tools = []
        logger.info("🔒 MCP 기능이 비활성화되었습니다. 일상 대화만 지원합니다.")
    
    async def initialize_mcp_tools(self):
        """MCP 도구들 초기화 - 빈 목록 반환"""
        logger.info("📝 MCP 도구 비활성화 - 일상 대화 모드")
        return []
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구 실행 - 비활성화됨"""
        logger.warning(f"⚠️ MCP 도구 '{tool_name}' 호출 시도 - 기능이 비활성화되어 있습니다")
        return {
            "success": False,
            "error": "MCP 기능이 현재 비활성화되어 있습니다. 일상 대화만 가능합니다."
        }
    
    def get_available_tools(self) -> List[Dict]:
        """사용 가능한 도구 목록 반환 - 빈 목록"""
        return []
    
    def get_connection_status(self) -> Dict[str, bool]:
        """모든 MCP 서버 연결 상태 반환 - 모두 비활성화"""
        return {
            "blender": False,
            "unity": False,
            "web_service": False,
            "mcp_enabled": False
        }

# MCP 매니저 싱글톤 인스턴스
mcp_manager = MCPManager()

async def get_mcp_tools() -> List[Dict]:
    """MCP 도구 목록 반환 (외부 사용용) - 빈 목록"""
    return []

async def execute_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """MCP 도구 실행 (외부 사용용) - 비활성화"""
    return {
        "success": False,
        "error": "MCP 기능이 비활성화되어 있습니다."
    }

def get_mcp_connection_status() -> Dict[str, bool]:
    """MCP 서버 연결 상태 반환 (외부 사용용) - 모두 비활성화"""
    return {
        "blender": False,
        "unity": False,
        "web_service": False,
        "mcp_enabled": False
    }

if __name__ == "__main__":
    # 연결 상태 테스트
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 MCP 서버 연결 상태 확인:")
    status = get_mcp_connection_status()
    for server, connected in status.items():
        print(f"  {'✅' if connected else '❌'} {server}: {'연결됨' if connected else '비활성화'}")
    
    print(f"\n📊 MCP 기능: 비활성화 (일상 대화만 지원)")
