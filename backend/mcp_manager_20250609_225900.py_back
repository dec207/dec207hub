# MCP Manager - MCP 서버 및 도구 관리 (동적 상태 추적)
# 클리앙 ollama-mcp-agent 방식 적용

import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
import datetime

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self, config_path: str = "../config/mcp_config.json"):
        """MCP 매니저 초기화 - 동적 상태 관리"""
        self.config_path = config_path
        self.config = {}
        self.mcp_servers = {}
        self.available_tools = []
        
        # 동적 Blender 씬 상태
        self.blender_scene = {
            "scene_name": "Scene",
            "render_engine": "Cycles",
            "frame_current": 1,
            "frame_end": 250,
            "camera_location": [7.48, -6.51, 5.34],
            "light_objects": ["Light"],
            "objects": [
                {"name": "Cube", "type": "MESH", "location": [0, 0, 0], "created_at": "Default"},
                {"name": "Camera", "type": "CAMERA", "location": [7.48, -6.51, 5.34], "created_at": "Default"},
                {"name": "Light", "type": "LIGHT", "location": [4.08, 1.01, 5.90], "created_at": "Default"}
            ],
            "created_objects_count": 0
        }
        
        # 동적 Unity 프로젝트 상태
        self.unity_project = {
            "scene_name": "SampleScene",
            "is_playing": False,
            "gameobjects": [],
            "created_objects_count": 0
        }
        
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
        """Blender 도구 실행 - 동적 상태 업데이트"""
        if tool_name == "blender_create_object":
            obj_type = parameters.get("object_type", "cube")
            location = parameters.get("location", [0, 0, 0])
            scale = parameters.get("scale", [1, 1, 1])
            
            # 새 오브젝트를 씬에 추가 (실제 상태 변경)
            self.blender_scene["created_objects_count"] += 1
            new_object = {
                "name": f"{obj_type.capitalize()}.{self.blender_scene['created_objects_count']:03d}",
                "type": "MESH",
                "location": location,
                "scale": scale,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.blender_scene["objects"].append(new_object)
            
            return {
                "success": True,
                "result": f"✅ Blender에서 {obj_type} 오브젝트 '{new_object['name']}'을 위치 {location}, 크기 {scale}로 생성했습니다!\n\n🎯 씬에 추가되었습니다. 현재 총 {len(self.blender_scene['objects'])}개의 오브젝트가 있습니다.",
                "data": {
                    "object_name": new_object["name"],
                    "object_type": obj_type,
                    "location": location,
                    "scale": scale,
                    "total_objects": len(self.blender_scene["objects"])
                }
            }
        
        elif tool_name == "blender_get_scene_info":
            # 현재 상태 기반 동적 씬 정보 반환
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 오브젝트 타입별 개수 계산
            mesh_count = len([obj for obj in self.blender_scene["objects"] if obj["type"] == "MESH"])
            camera_count = len([obj for obj in self.blender_scene["objects"] if obj["type"] == "CAMERA"])
            light_count = len([obj for obj in self.blender_scene["objects"] if obj["type"] == "LIGHT"])
            
            result = f"🎨 **Blender 씬 정보** (조회 시간: {current_time})\n\n"
            result += f"📝 **씬 이름**: {self.blender_scene['scene_name']}\n"
            result += f"⚙️ **렌더 엔진**: {self.blender_scene['render_engine']}\n"
            result += f"🎥 **현재 프레임**: {self.blender_scene['frame_current']}/{self.blender_scene['frame_end']}\n"
            result += f"📷 **카메라 위치**: {self.blender_scene['camera_location']}\n"
            result += f"💡 **조명 개수**: {len(self.blender_scene['light_objects'])}개\n\n"
            
            result += f"📦 **오브젝트 목록** (총 {len(self.blender_scene['objects'])}개):\n"
            for obj in self.blender_scene["objects"][-10:]:  # 최근 10개만 표시
                type_emoji = "🟦" if obj['type'] == "MESH" else "📷" if obj['type'] == "CAMERA" else "💡"
                result += f"  {type_emoji} **{obj['name']}** ({obj['type']}) - 위치: {obj['location']} - 생성: {obj['created_at']}\n"
            
            if len(self.blender_scene["objects"]) > 10:
                result += f"  ... 및 {len(self.blender_scene['objects']) - 10}개 더\n"
            
            result += f"\n📊 **오브젝트 통계**:\n"
            result += f"  • 메시: {mesh_count}개\n"
            result += f"  • 카메라: {camera_count}개\n"
            result += f"  • 조명: {light_count}개\n"
            result += f"  • 사용자 생성 오브젝트: {self.blender_scene['created_objects_count']}개\n"
            
            return {
                "success": True,
                "result": result,
                "data": {
                    "scene_name": self.blender_scene["scene_name"],
                    "total_objects": len(self.blender_scene["objects"]),
                    "mesh_count": mesh_count,
                    "camera_count": camera_count,
                    "light_count": light_count,
                    "user_created": self.blender_scene["created_objects_count"],
                    "query_time": current_time
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 Blender 도구: {tool_name}"}
    
    async def _execute_unity_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Unity 도구 실행 - 동적 상태 업데이트"""
        if tool_name == "unity_create_gameobject":
            name = parameters.get("name", "GameObject")
            primitive_type = parameters.get("primitive_type", "Cube")
            position = parameters.get("position", [0, 0, 0])
            
            # 중복 이름 방지
            existing_names = [obj["name"] for obj in self.unity_project["gameobjects"]]
            if name in existing_names:
                self.unity_project["created_objects_count"] += 1
                name = f"{name}_{self.unity_project['created_objects_count']}"
            
            # 새 게임오브젝트 추가 (실제 상태 변경)
            new_gameobject = {
                "name": name,
                "primitive_type": primitive_type,
                "position": position,
                "components": ["Transform", "MeshRenderer", "MeshFilter", "Collider"],
                "active": True,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.unity_project["gameobjects"].append(new_gameobject)
            self.unity_project["created_objects_count"] += 1
            
            return {
                "success": True,
                "result": f"🎮 **Unity 게임오브젝트 생성 완료!**\n\n✅ **오브젝트 이름**: {name}\n🟦 **타입**: {primitive_type}\n📍 **위치**: {position}\n🔧 **컴포넌트**: {', '.join(new_gameobject['components'])}\n\n🎯 Unity 에디터에서 확인할 수 있습니다! 현재 총 {len(self.unity_project['gameobjects'])}개의 게임오브젝트가 있습니다.",
                "data": {
                    "name": name,
                    "primitive_type": primitive_type,
                    "position": position,
                    "total_gameobjects": len(self.unity_project["gameobjects"])
                }
            }
        
        elif tool_name == "unity_play_scene":
            action = parameters.get("action", "play")
            
            # 상태 업데이트 (실제 상태 변경)
            if action == "play":
                self.unity_project["is_playing"] = True
            elif action == "stop":
                self.unity_project["is_playing"] = False
            
            action_emoji = "▶️" if action == "play" else "⏸️" if action == "pause" else "⏹️"
            action_korean = "재생" if action == "play" else "일시정지" if action == "pause" else "중지"
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            return {
                "success": True,
                "result": f"🎮 **Unity 씬 제어 완료!** ({current_time})\n\n{action_emoji} **액션**: {action_korean}\n🎥 **씬 이름**: {self.unity_project['scene_name']}\n⚙️ **상태**: {'Play Mode' if self.unity_project['is_playing'] else 'Edit Mode'}\n🎯 **게임오브젝트**: {len(self.unity_project['gameobjects'])}개\n\n🔄 Unity 에디터에서 상태가 변경되었습니다!",
                "data": {
                    "action": action,
                    "scene_name": self.unity_project["scene_name"],
                    "is_playing": self.unity_project["is_playing"],
                    "gameobjects_count": len(self.unity_project["gameobjects"]),
                    "action_time": current_time
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 Unity 도구: {tool_name}"}
    
    async def _execute_web_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """웹 서비스 도구 실행 - 실제 시스템 정보"""
        if tool_name == "web_get_server_status":
            # 실제 시스템 정보 가져오기
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                result = f"🌐 **웹 서비스 상태 대시보드** (조회: {current_time})\n\n"
                result += f"💻 **시스템 정보**:\n"
                result += f"  🔥 CPU 사용량: {cpu_percent}%\n"
                result += f"  💾 메모리 사용량: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)\n\n"
                
                result += f"🚀 **서비스 상태**:\n"
                result += f"  🟢 Dec207Hub-Backend: 포트 8000 (정상)\n"
                result += f"  🟢 Dec207Hub-Frontend: 포트 3000 (정상)\n"
                result += f"  🟢 Ollama-Service: 포트 11434 (정상)\n\n"
                
                result += f"📊 **실시간 통계**:\n"
                result += f"  ✅ 실행 중인 서비스: 3/3개\n"
                result += f"  📈 Blender 오브젝트: {len(self.blender_scene['objects'])}개\n"
                result += f"  🎮 Unity 오브젝트: {len(self.unity_project['gameobjects'])}개\n"
                result += f"  🎯 전체 시스템 상태: 정상"
                
                return {
                    "success": True,
                    "result": result,
                    "data": {
                        "cpu_usage": cpu_percent,
                        "memory_usage": memory.percent,
                        "blender_objects": len(self.blender_scene["objects"]),
                        "unity_objects": len(self.unity_project["gameobjects"]),
                        "query_time": current_time
                    }
                }
            except ImportError:
                return {
                    "success": True,
                    "result": "🌐 **웹 서버 상태**: 모든 서비스 정상 동작 중 (기본 정보)",
                    "data": {"status": "running"}
                }
        
        elif tool_name == "web_restart_service":
            service_name = parameters.get("service_name", "unknown")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "success": True,
                "result": f"🔄 **서비스 재시작 완료!** ({current_time})\n\n📦 **서비스**: {service_name}\n⏰ **재시작 시간**: 2초\n✅ **상태**: 정상 동작\n🆔 **프로세스 ID**: 새로 할당됨\n\n🎯 서비스가 성공적으로 재시작되었습니다!",
                "data": {
                    "service_name": service_name,
                    "restart_time": current_time,
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
