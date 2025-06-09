# Unity MCP Server
# FastMCP를 사용한 Unity 3D 게임 엔진 제어 서버

from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP(
    "Unity-MCP",
    host="0.0.0.0",
    port=8002,
    instructions="Unity 게임 엔진 제어를 위한 MCP 서버입니다. 게임오브젝트 생성, 씬 관리, 스크립트 실행, 빌드 등의 기능을 제공합니다."
)

# 가상의 Unity 프로젝트 상태 (실제로는 Unity Editor API 연동)
unity_project = {
    "scene_name": "SampleScene",
    "gameobjects": [],
    "is_playing": False,
    "build_settings": {
        "target_platform": "PC",
        "build_path": "Builds/"
    },
    "project_settings": {
        "company_name": "Dec207",
        "product_name": "Dec207Hub Unity Demo"
    }
}

@mcp.tool()
async def create_unity_gameobject(
    name: str,
    primitive_type: str = "Cube",
    position: List[float] = [0, 0, 0],
    rotation: List[float] = [0, 0, 0],
    scale: List[float] = [1, 1, 1],
    add_components: List[str] = []
) -> str:
    """
    Unity에서 게임오브젝트를 생성합니다.
    
    Args:
        name: 게임오브젝트 이름
        primitive_type: 프리미티브 타입 (Cube, Sphere, Cylinder, Plane, Quad, Capsule)
        position: 위치 [x, y, z]
        rotation: 회전 [x, y, z] (오일러 각도)
        scale: 크기 [x, y, z]
        add_components: 추가할 컴포넌트 목록
    """
    try:
        print(f"\n[DEBUG] Unity MCP: create_gameobject called - {name} ({primitive_type})\n")
        
        # 중복 이름 확인
        existing_names = [obj["name"] for obj in unity_project["gameobjects"]]
        if name in existing_names:
            # 자동으로 번호 추가
            counter = 1
            original_name = name
            while name in existing_names:
                name = f"{original_name} ({counter})"
                counter += 1
        
        # 새 게임오브젝트 생성
        new_gameobject = {
            "name": name,
            "primitive_type": primitive_type,
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "components": ["Transform"] + add_components,
            "created_time": asyncio.get_event_loop().time(),
            "active": True,
            "tag": "Untagged",
            "layer": 0
        }
        
        # 프리미티브 타입별 기본 컴포넌트 추가
        if primitive_type in ["Cube", "Sphere", "Cylinder", "Capsule"]:
            if "MeshRenderer" not in new_gameobject["components"]:
                new_gameobject["components"].extend(["MeshRenderer", "MeshFilter"])
            if primitive_type in ["Cube", "Sphere", "Cylinder", "Capsule"]:
                new_gameobject["components"].append("Collider")
        
        # 프로젝트에 추가
        unity_project["gameobjects"].append(new_gameobject)
        
        result = f"🎮 Unity에서 게임오브젝트 '{name}'을 생성했습니다.\n"
        result += f"🧊 타입: {primitive_type}\n"
        result += f"📍 위치: {position}\n"
        result += f"🔄 회전: {rotation}\n"
        result += f"📏 크기: {scale}\n"
        result += f"🔧 컴포넌트: {', '.join(new_gameobject['components'])}\n"
        result += f"🎯 총 오브젝트 수: {len(unity_project['gameobjects'])}개"
        
        logger.info(f"Unity 게임오브젝트 생성: {name} ({primitive_type})")
        return result
        
    except Exception as e:
        error_msg = f"❌ Unity 게임오브젝트 생성 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def unity_play_control(action: str) -> str:
    """
    Unity 에디터의 재생 상태를 제어합니다.
    
    Args:
        action: 제어 액션 (play, pause, stop)
    """
    try:
        print(f"\n[DEBUG] Unity MCP: play_control called - {action}\n")
        
        if action == "play":
            unity_project["is_playing"] = True
            result = f"▶️ Unity 씬 '{unity_project['scene_name']}'이 재생되었습니다.\n"
            result += f"🎮 게임오브젝트 {len(unity_project['gameobjects'])}개가 활성화되었습니다."
            
        elif action == "pause":
            result = f"⏸️ Unity 씬 재생이 일시정지되었습니다.\n"
            result += f"🕐 현재 상태: {'재생 중' if unity_project['is_playing'] else '정지'}"
            
        elif action == "stop":
            unity_project["is_playing"] = False
            result = f"⏹️ Unity 씬 재생이 중지되었습니다.\n"
            result += f"🔄 씬이 초기 상태로 되돌아갔습니다."
            
        else:
            result = f"❌ 알 수 없는 액션: {action}\n"
            result += "사용 가능한 액션: play, pause, stop"
            
        logger.info(f"Unity 재생 제어: {action}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Unity 재생 제어 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def get_unity_project_info() -> str:
    """
    현재 Unity 프로젝트의 상태 정보를 조회합니다.
    """
    try:
        print(f"\n[DEBUG] Unity MCP: get_project_info called\n")
        
        # 게임오브젝트 타입별 개수 계산
        primitive_types = {}
        for obj in unity_project["gameobjects"]:
            obj_type = obj["primitive_type"]
            primitive_types[obj_type] = primitive_types.get(obj_type, 0) + 1
        
        result = f"🎮 Unity 프로젝트 정보\n"
        result += f"📝 씬 이름: {unity_project['scene_name']}\n"
        result += f"▶️ 재생 상태: {'재생 중' if unity_project['is_playing'] else '정지'}\n"
        result += f"🏢 회사명: {unity_project['project_settings']['company_name']}\n"
        result += f"📦 제품명: {unity_project['project_settings']['product_name']}\n"
        result += f"🎯 타겟 플랫폼: {unity_project['build_settings']['target_platform']}\n\n"
        
        result += f"🎲 게임오브젝트 현황 (총 {len(unity_project['gameobjects'])}개):\n"
        if primitive_types:
            for obj_type, count in primitive_types.items():
                result += f"  • {obj_type}: {count}개\n"
        else:
            result += "  • 생성된 게임오브젝트가 없습니다.\n"
        
        # 최근 생성된 게임오브젝트 목록
        if unity_project["gameobjects"]:
            result += f"\n📋 게임오브젝트 목록:\n"
            for obj in unity_project["gameobjects"][-5:]:  # 최근 5개만 표시
                status = "🟢" if obj["active"] else "🔴"
                result += f"  {status} {obj['name']} ({obj['primitive_type']}) - 위치: {obj['position']}\n"
        
        logger.info("Unity 프로젝트 정보 조회 완료")
        return result
        
    except Exception as e:
        error_msg = f"❌ Unity 프로젝트 정보 조회 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def unity_add_component(
    gameobject_name: str,
    component_type: str,
    component_properties: Dict[str, Any] = {}
) -> str:
    """
    Unity 게임오브젝트에 컴포넌트를 추가합니다.
    
    Args:
        gameobject_name: 대상 게임오브젝트 이름
        component_type: 추가할 컴포넌트 타입 (Rigidbody, BoxCollider, MeshRenderer 등)
        component_properties: 컴포넌트 속성 (딕셔너리)
    """
    try:
        print(f"\n[DEBUG] Unity MCP: add_component called - {gameobject_name}.{component_type}\n")
        
        # 게임오브젝트 찾기
        for obj in unity_project["gameobjects"]:
            if obj["name"] == gameobject_name:
                if component_type not in obj["components"]:
                    obj["components"].append(component_type)
                    
                    # 컴포넌트 속성 저장 (실제로는 Unity API 호출)
                    if component_properties:
                        if "component_data" not in obj:
                            obj["component_data"] = {}
                        obj["component_data"][component_type] = component_properties
                    
                    result = f"🔧 게임오브젝트 '{gameobject_name}'에 {component_type} 컴포넌트를 추가했습니다.\n"
                    if component_properties:
                        result += f"⚙️ 설정된 속성: {component_properties}\n"
                    result += f"📝 총 컴포넌트: {', '.join(obj['components'])}"
                    
                    logger.info(f"Unity 컴포넌트 추가: {gameobject_name}.{component_type}")
                    return result
                else:
                    result = f"ℹ️ 게임오브젝트 '{gameobject_name}'에 이미 {component_type} 컴포넌트가 있습니다."
                    return result
        
        # 게임오브젝트를 찾을 수 없는 경우
        available_objects = [obj["name"] for obj in unity_project["gameobjects"]]
        result = f"❌ 게임오브젝트 '{gameobject_name}'을 찾을 수 없습니다.\n"
        result += f"📋 사용 가능한 오브젝트: {', '.join(available_objects) if available_objects else '없음'}"
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Unity 컴포넌트 추가 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def unity_build_project(
    target_platform: str = "PC",
    build_path: str = "Builds/",
    development_build: bool = False
) -> str:
    """
    Unity 프로젝트를 빌드합니다.
    
    Args:
        target_platform: 타겟 플랫폼 (PC, Android, iOS, WebGL)
        build_path: 빌드 출력 경로
        development_build: 개발 빌드 여부
    """
    try:
        print(f"\n[DEBUG] Unity MCP: build_project called - {target_platform}\n")
        
        # 빌드 시뮬레이션 (실제로는 BuildPipeline.BuildPlayer() 호출)
        await asyncio.sleep(2)  # 빌드 시간 시뮬레이션
        
        # 빌드 설정 업데이트
        unity_project["build_settings"]["target_platform"] = target_platform
        unity_project["build_settings"]["build_path"] = build_path
        
        result = f"🏗️ Unity 프로젝트 빌드 완료!\n"
        result += f"🎯 타겟 플랫폼: {target_platform}\n"
        result += f"📁 출력 경로: {build_path}\n"
        result += f"🔨 빌드 타입: {'개발' if development_build else '릴리즈'}\n"
        result += f"📦 포함된 씬: {unity_project['scene_name']}\n"
        result += f"🎮 게임오브젝트: {len(unity_project['gameobjects'])}개"
        
        logger.info(f"Unity 프로젝트 빌드: {target_platform}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Unity 프로젝트 빌드 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    print("🎮 Unity MCP 서버 시작 중...")
    print("📡 포트: 8002")
    print("🔧 사용 가능한 도구:")
    print("  • create_unity_gameobject - 게임오브젝트 생성")
    print("  • unity_play_control - 재생 제어")
    print("  • get_unity_project_info - 프로젝트 정보 조회")
    print("  • unity_add_component - 컴포넌트 추가")
    print("  • unity_build_project - 프로젝트 빌드")
    print("=" * 50)
    
    mcp.run(transport="stdio")
