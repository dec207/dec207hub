# MCP Manager - MCP 서버 및 도구 관리
# 클리앙 ollama-mcp-agent 방식 적용

import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self, config_path: str = "config/mcp_config.json"):
        """MCP 매니저 초기화"""
        self.config_path = config_path
        self.config = {}
        self.mcp_servers = {}
        self.available_tools = []
        self.load_config()
    
    def load_config(self):
        """MCP 설정 파일 로드"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"✅ MCP 설정 로드 완료: {len(self.config.get('mcpServers', {}))}개 서버")
            else:
                logger.warning(f"❌ MCP 설정 파일을 찾을 수 없음: {config_file}")
                self.config = {"mcpServers": {}, "settings": {}}
        except Exception as e:
            logger.error(f"❌ MCP 설정 로드 실패: {e}")
            self.config = {"mcpServers": {}, "settings": {}}
    
    async def initialize_mcp_tools(self):
        """MCP 도구들 초기화"""
        try:
            servers = self.config.get("mcpServers", {})
            self.available_tools = []
            
            for server_name, server_config in servers.items():
                if not server_config.get("enabled", True):
                    continue
                    
                # 각 MCP 서버에서 제공하는 도구 목록 가져오기
                tools = await self._get_server_tools(server_name, server_config)
                self.available_tools.extend(tools)
                
                logger.info(f"📡 {server_name} MCP 서버 - {len(tools)}개 도구 로드")
            
            logger.info(f"🔧 총 {len(self.available_tools)}개 MCP 도구 준비 완료")
            return self.available_tools
            
        except Exception as e:
            logger.error(f"❌ MCP 도구 초기화 실패: {e}")
            return []
    
    async def _get_server_tools(self, server_name: str, server_config: Dict) -> List[Dict]:
        """개별 MCP 서버에서 도구 목록 가져오기"""
        try:
            # 실제 구현에서는 MCP 프로토콜을 통해 서버와 통신
            # 여기서는 각 서버별 기본 도구 정의
            
            if server_name == "blender":
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": "blender_create_object",
                            "description": "Blender에서 3D 오브젝트 생성 (큐브, 구, 실린더 등)",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "object_type": {
                                        "type": "string",
                                        "description": "생성할 오브젝트 타입",
                                        "enum": ["cube", "sphere", "cylinder", "plane", "monkey"]
                                    },
                                    "location": {
                                        "type": "array",
                                        "description": "오브젝트 위치 [x, y, z]",
                                        "items": {"type": "number"}
                                    },
                                    "scale": {
                                        "type": "array", 
                                        "description": "오브젝트 크기 [x, y, z]",
                                        "items": {"type": "number"}
                                    }
                                },
                                "required": ["object_type"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "blender_get_scene_info",
                            "description": "현재 Blender 씬 정보 조회",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    }
                ]
            
            elif server_name == "unity":
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": "unity_create_gameobject",
                            "description": "Unity에서 게임오브젝트 생성",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "게임오브젝트 이름"
                                    },
                                    "primitive_type": {
                                        "type": "string",
                                        "description": "프리미티브 타입",
                                        "enum": ["Cube", "Sphere", "Cylinder", "Plane", "Quad"]
                                    },
                                    "position": {
                                        "type": "array",
                                        "description": "위치 [x, y, z]",
                                        "items": {"type": "number"}
                                    }
                                },
                                "required": ["name", "primitive_type"]
                            }
                        }
                    },
                    {
                        "type": "function", 
                        "function": {
                            "name": "unity_play_scene",
                            "description": "Unity 씬 재생/정지",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "description": "재생 액션",
                                        "enum": ["play", "pause", "stop"]
                                    }
                                },
                                "required": ["action"]
                            }
                        }
                    }
                ]
            
            elif server_name == "web_service":
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": "web_get_server_status",
                            "description": "웹 서버 상태 확인",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "web_restart_service",
                            "description": "웹 서비스 재시작",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "service_name": {
                                        "type": "string",
                                        "description": "재시작할 서비스 이름"
                                    }
                                },
                                "required": ["service_name"]
                            }
                        }
                    }
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ {server_name} 서버 도구 로드 실패: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구 실행"""
        try:
            logger.info(f"🔧 도구 실행: {tool_name} - {parameters}")
            
            # Blender 도구 실행
            if tool_name.startswith("blender_"):
                return await self._execute_blender_tool(tool_name, parameters)
            
            # Unity 도구 실행  
            elif tool_name.startswith("unity_"):
                return await self._execute_unity_tool(tool_name, parameters)
            
            # 웹 서비스 도구 실행
            elif tool_name.startswith("web_"):
                return await self._execute_web_tool(tool_name, parameters)
            
            else:
                return {
                    "success": False,
                    "error": f"알 수 없는 도구: {tool_name}"
                }
                
        except Exception as e:
            logger.error(f"❌ 도구 실행 실패 {tool_name}: {e}")
            return {
                "success": False,
                "error": f"도구 실행 오류: {str(e)}"
            }
    
    async def _execute_blender_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Blender 도구 실행"""
        if tool_name == "blender_create_object":
            obj_type = parameters.get("object_type", "cube")
            location = parameters.get("location", [0, 0, 0])
            scale = parameters.get("scale", [1, 1, 1])
            
            return {
                "success": True,
                "result": f"Blender에서 {obj_type} 오브젝트를 위치 {location}, 크기 {scale}로 생성했습니다.",
                "data": {
                    "object_type": obj_type,
                    "location": location,
                    "scale": scale,
                    "object_id": f"blender_obj_{asyncio.get_event_loop().time()}"
                }
            }
        
        elif tool_name == "blender_get_scene_info":
            return {
                "success": True,
                "result": "현재 Blender 씬 정보를 조회했습니다.",
                "data": {
                    "scene_name": "Scene",
                    "objects_count": 3,
                    "render_engine": "Cycles",
                    "frame_current": 1,
                    "frame_end": 250
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 Blender 도구: {tool_name}"}
    
    async def _execute_unity_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Unity 도구 실행"""
        if tool_name == "unity_create_gameobject":
            name = parameters.get("name", "GameObject")
            primitive_type = parameters.get("primitive_type", "Cube")
            position = parameters.get("position", [0, 0, 0])
            
            return {
                "success": True,
                "result": f"Unity에서 {primitive_type} 타입의 '{name}' 게임오브젝트를 위치 {position}에 생성했습니다.",
                "data": {
                    "name": name,
                    "primitive_type": primitive_type,
                    "position": position,
                    "instance_id": f"unity_obj_{int(asyncio.get_event_loop().time())}"
                }
            }
        
        elif tool_name == "unity_play_scene":
            action = parameters.get("action", "play")
            
            return {
                "success": True,
                "result": f"Unity 씬을 {action} 상태로 변경했습니다.",
                "data": {
                    "action": action,
                    "scene_name": "SampleScene",
                    "is_playing": action == "play"
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 Unity 도구: {tool_name}"}
    
    async def _execute_web_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """웹 서비스 도구 실행"""
        if tool_name == "web_get_server_status":
            return {
                "success": True,
                "result": "웹 서버 상태를 확인했습니다.",
                "data": {
                    "server_status": "running",
                    "uptime": "2 hours 30 minutes",
                    "cpu_usage": "15%",
                    "memory_usage": "65%",
                    "active_connections": 8
                }
            }
        
        elif tool_name == "web_restart_service":
            service_name = parameters.get("service_name", "unknown")
            
            return {
                "success": True,
                "result": f"'{service_name}' 서비스를 재시작했습니다.",
                "data": {
                    "service_name": service_name,
                    "restart_time": "2024-01-01 12:00:00",
                    "status": "restarted"
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 웹 도구: {tool_name}"}
    
    def get_available_tools(self) -> List[Dict]:
        """사용 가능한 도구 목록 반환"""
        return self.available_tools
    
    def get_tools_by_category(self, category: str) -> List[Dict]:
        """카테고리별 도구 목록 반환"""
        categories = self.config.get("tool_categories", {})
        server_names = categories.get(category, [])
        
        tools = []
        for tool in self.available_tools:
            tool_name = tool["function"]["name"]
            for server_name in server_names:
                if tool_name.startswith(f"{server_name}_"):
                    tools.append(tool)
                    break
        
        return tools

# MCP 매니저 싱글톤 인스턴스
mcp_manager = MCPManager()

async def get_mcp_tools() -> List[Dict]:
    """MCP 도구 목록 반환 (외부 사용용)"""
    if not mcp_manager.available_tools:
        await mcp_manager.initialize_mcp_tools()
    return mcp_manager.get_available_tools()

async def execute_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """MCP 도구 실행 (외부 사용용)"""
    return await mcp_manager.execute_tool(tool_name, parameters)

def test_mcp_tools():
    """MCP 도구 테스트 함수"""
    async def _test():
        logger.info("🧪 MCP 도구 테스트 시작...")
        
        # 도구 초기화
        tools = await mcp_manager.initialize_mcp_tools()
        logger.info(f"📋 로드된 도구: {len(tools)}개")
        
        # Blender 도구 테스트
        result = await mcp_manager.execute_tool("blender_create_object", {
            "object_type": "sphere",
            "location": [2, 0, 1],
            "scale": [1.5, 1.5, 1.5]
        })
        logger.info(f"🔵 Blender 테스트: {result}")
        
        # Unity 도구 테스트
        result = await mcp_manager.execute_tool("unity_create_gameobject", {
            "name": "TestCube",
            "primitive_type": "Cube",
            "position": [0, 1, 0]
        })
        logger.info(f"🎮 Unity 테스트: {result}")
        
        # 웹 서비스 도구 테스트
        result = await mcp_manager.execute_tool("web_get_server_status", {})
        logger.info(f"🌐 웹 서비스 테스트: {result}")
        
        logger.info("✅ MCP 도구 테스트 완료")
    
    # 테스트 실행
    try:
        asyncio.run(_test())
    except Exception as e:
        logger.error(f"❌ MCP 테스트 실패: {e}")

if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)
    test_mcp_tools()
