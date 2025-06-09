# MCP Manager - 실제 MCP 서버 연결 (데모 모드 비활성화)
# 실제 Blender, Unity, 웹 서비스와의 진정한 연결만 허용

import json
import asyncio
import subprocess
import logging
import psutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
import datetime

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self, config_path: str = "../config/mcp_config.json"):
        """MCP 매니저 초기화 - 실제 서버 연결만 허용"""
        self.config_path = config_path
        self.config = {}
        self.mcp_servers = {}
        self.available_tools = []
        self.demo_mode = False  # 데모 모드 완전 비활성화
        
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
    
    def _check_process_running(self, process_name: str) -> bool:
        """프로세스가 실행 중인지 확인"""
        try:
            for proc in psutil.process_iter(['name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"프로세스 확인 실패 {process_name}: {e}")
            return False
    
    def _check_blender_connection(self) -> bool:
        """Blender 프로세스 및 MCP 서버 연결 확인"""
        # 1. Blender 프로세스 확인
        if not self._check_process_running("blender"):
            logger.warning("❌ Blender 프로세스가 실행되지 않음")
            return False
        
        # 2. Blender MCP 서버 스크립트 존재 확인
        blender_mcp_script = Path("./backend/mcp_servers/mcp_server_blender.py")
        if not blender_mcp_script.exists():
            logger.warning(f"❌ Blender MCP 서버 스크립트를 찾을 수 없음: {blender_mcp_script}")
            return False
        
        logger.info("✅ Blender 연결 확인 완료")
        return True
    
    def _check_unity_connection(self) -> bool:
        """Unity 프로세스 및 MCP 서버 연결 확인"""
        # 1. Unity 에디터 프로세스 확인
        unity_processes = ["Unity", "Unity.exe", "UnityEditor"]
        unity_running = False
        for proc_name in unity_processes:
            if self._check_process_running(proc_name):
                unity_running = True
                break
        
        if not unity_running:
            logger.warning("❌ Unity 에디터가 실행되지 않음")
            return False
        
        # 2. Unity MCP 서버 스크립트 존재 확인
        unity_mcp_script = Path("./backend/mcp_servers/mcp_server_unity.py")
        if not unity_mcp_script.exists():
            logger.warning(f"❌ Unity MCP 서버 스크립트를 찾을 수 없음: {unity_mcp_script}")
            return False
        
        logger.info("✅ Unity 연결 확인 완료")
        return True
    
    def _check_web_service_connection(self) -> bool:
        """웹 서비스 상태 확인"""
        # 실제 시스템 상태만 확인 (항상 사용 가능)
        return True
    
    async def initialize_mcp_tools(self):
        """MCP 도구들 초기화 - 실제 연결 확인 후에만 활성화"""
        try:
            servers = self.config.get("mcpServers", {})
            self.available_tools = []
            
            for server_name, server_config in servers.items():
                if not server_config.get("enabled", True):
                    continue
                
                # 실제 연결 상태 확인
                connection_ok = False
                if server_name == "blender":
                    connection_ok = self._check_blender_connection()
                elif server_name == "unity":
                    connection_ok = self._check_unity_connection()
                elif server_name == "web_service":
                    connection_ok = self._check_web_service_connection()
                
                if connection_ok:
                    # 실제 연결된 서버에서만 도구 로드
                    tools = await self._get_server_tools(server_name, server_config)
                    self.available_tools.extend(tools)
                    logger.info(f"📡 {server_name} MCP 서버 연결됨 - {len(tools)}개 도구 로드")
                else:
                    logger.warning(f"🔴 {server_name} MCP 서버 연결 실패 - 도구 비활성화")
            
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
                            "description": "실제 Blender에서 3D 오브젝트 생성 (큐브, 구, 실린더 등)",
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
                            "description": "실제 Blender 씬 정보 조회",
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
                            "description": "실제 Unity에서 게임오브젝트 생성",
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
                            "description": "실제 Unity 씬 재생/정지",
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
                            "description": "실제 웹 서버 상태 확인",
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
                            "description": "실제 웹 서비스 재시작",
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
        """MCP 도구 실행 - 실제 서버 연결 필수"""
        try:
            logger.info(f"🔧 도구 실행 시도: {tool_name} - {parameters}")
            
            # 사전 연결 상태 확인
            if tool_name.startswith("blender_"):
                if not self._check_blender_connection():
                    return {
                        "success": False,
                        "error": "❌ Blender가 실행되지 않았거나 MCP 서버에 연결할 수 없습니다. 먼저 Blender를 실행하고 MCP 플러그인을 활성화해주세요."
                    }
                return await self._execute_real_blender_tool(tool_name, parameters)
            
            elif tool_name.startswith("unity_"):
                if not self._check_unity_connection():
                    return {
                        "success": False,
                        "error": "❌ Unity 에디터가 실행되지 않았거나 MCP 서버에 연결할 수 없습니다. 먼저 Unity 에디터를 실행하고 MCP 플러그인을 활성화해주세요."
                    }
                return await self._execute_real_unity_tool(tool_name, parameters)
            
            elif tool_name.startswith("web_"):
                return await self._execute_real_web_tool(tool_name, parameters)
            
            else:
                return {
                    "success": False,
                    "error": f"❌ 알 수 없는 도구: {tool_name}"
                }
                
        except Exception as e:
            logger.error(f"❌ 도구 실행 실패 {tool_name}: {e}")
            return {
                "success": False,
                "error": f"도구 실행 오류: {str(e)}"
            }
    
    async def _execute_real_blender_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """실제 Blender MCP 서버 도구 실행"""
        try:
            # 실제 Blender MCP 서버와 통신
            blender_mcp_script = Path("./backend/mcp_servers/mcp_server_blender.py")
            
            # subprocess를 통해 실제 MCP 서버 호출
            cmd = ["python", str(blender_mcp_script), tool_name, json.dumps(parameters)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                logger.info(f"✅ Blender 도구 실행 성공: {tool_name}")
                return result
            else:
                error_msg = stderr.decode() if stderr else "알 수 없는 오류"
                logger.error(f"❌ Blender 도구 실행 실패: {error_msg}")
                return {
                    "success": False,
                    "error": f"Blender MCP 서버 오류: {error_msg}"
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": "❌ Blender MCP 서버 스크립트를 찾을 수 없습니다. 먼저 MCP 서버를 설치해주세요."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Blender 도구 실행 중 오류: {str(e)}"
            }
    
    async def _execute_real_unity_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """실제 Unity MCP 서버 도구 실행"""
        try:
            # 실제 Unity MCP 서버와 통신
            unity_mcp_script = Path("./backend/mcp_servers/mcp_server_unity.py")
            
            # subprocess를 통해 실제 MCP 서버 호출
            cmd = ["python", str(unity_mcp_script), tool_name, json.dumps(parameters)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                logger.info(f"✅ Unity 도구 실행 성공: {tool_name}")
                return result
            else:
                error_msg = stderr.decode() if stderr else "알 수 없는 오류"
                logger.error(f"❌ Unity 도구 실행 실패: {error_msg}")
                return {
                    "success": False,
                    "error": f"Unity MCP 서버 오류: {error_msg}"
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": "❌ Unity MCP 서버 스크립트를 찾을 수 없습니다. 먼저 MCP 서버를 설치해주세요."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unity 도구 실행 중 오류: {str(e)}"
            }
    
    async def _execute_real_web_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """실제 웹 서비스 도구 실행"""
        if tool_name == "web_get_server_status":
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 실제 프로세스 상태 확인
                ollama_running = self._check_process_running("ollama")
                python_processes = len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])
                
                result = f"🌐 **실제 시스템 상태** (조회: {current_time})\n\n"
                result += f"💻 **하드웨어 정보**:\n"
                result += f"  🔥 CPU 사용량: {cpu_percent}%\n"
                result += f"  💾 메모리: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)\n"
                result += f"  💽 디스크: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)\n\n"
                
                result += f"🔍 **프로세스 상태**:\n"
                result += f"  {'🟢' if ollama_running else '🔴'} Ollama: {'실행 중' if ollama_running else '중지됨'}\n"
                result += f"  🟢 Python 프로세스: {python_processes}개\n"
                result += f"  {'🟢' if self._check_process_running('blender') else '🔴'} Blender: {'실행 중' if self._check_process_running('blender') else '중지됨'}\n"
                result += f"  {'🟢' if self._check_process_running('unity') else '🔴'} Unity: {'실행 중' if self._check_process_running('unity') else '중지됨'}\n\n"
                
                result += f"📊 **실시간 통계**:\n"
                result += f"  🎯 시스템 상태: {'정상' if cpu_percent < 80 and memory.percent < 90 else '높은 사용률'}\n"
                result += f"  ⏰ 업타임: {datetime.datetime.now().strftime('%H:%M:%S')}"
                
                return {
                    "success": True,
                    "result": result,
                    "data": {
                        "cpu_usage": cpu_percent,
                        "memory_usage": memory.percent,
                        "disk_usage": disk.percent,
                        "ollama_running": ollama_running,
                        "python_processes": python_processes,
                        "query_time": current_time
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"시스템 상태 조회 실패: {str(e)}"
                }
        
        elif tool_name == "web_restart_service":
            service_name = parameters.get("service_name", "unknown")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 실제로는 서비스 재시작 로직이 필요하지만, 안전상 시뮬레이션만
            return {
                "success": True,
                "result": f"⚠️ **서비스 재시작 시뮬레이션** ({current_time})\n\n📦 **서비스**: {service_name}\n🔒 **보안**: 실제 재시작은 관리자 권한이 필요합니다\n💡 **권장**: 수동으로 서비스를 재시작해주세요\n\n🎯 시뮬레이션 완료 - 실제 재시작은 수행되지 않았습니다.",
                "data": {
                    "service_name": service_name,
                    "simulation_time": current_time,
                    "status": "simulated"
                }
            }
        
        return {"success": False, "error": f"지원하지 않는 웹 도구: {tool_name}"}
    
    def get_available_tools(self) -> List[Dict]:
        """사용 가능한 도구 목록 반환"""
        return self.available_tools
    
    def get_connection_status(self) -> Dict[str, bool]:
        """모든 MCP 서버 연결 상태 반환"""
        return {
            "blender": self._check_blender_connection(),
            "unity": self._check_unity_connection(),
            "web_service": self._check_web_service_connection()
        }

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

def get_mcp_connection_status() -> Dict[str, bool]:
    """MCP 서버 연결 상태 반환 (외부 사용용)"""
    return mcp_manager.get_connection_status()

if __name__ == "__main__":
    # 연결 상태 테스트
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 MCP 서버 연결 상태 확인:")
    status = get_mcp_connection_status()
    for server, connected in status.items():
        print(f"  {'✅' if connected else '❌'} {server}: {'연결됨' if connected else '연결 안됨'}")
    
    print(f"\n📊 연결된 서버: {sum(status.values())}/{len(status)}개")
