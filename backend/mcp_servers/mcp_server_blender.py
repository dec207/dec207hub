# Blender MCP Server
# FastMCP를 사용한 Blender 3D 제어 서버

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
    "Blender-MCP",
    host="0.0.0.0",
    port=8001,
    instructions="Blender 3D 모델링 및 렌더링을 위한 MCP 서버입니다. 3D 오브젝트 생성, 수정, 씬 관리, 렌더링 등의 기능을 제공합니다."
)

# 가상의 Blender 씬 상태 (실제로는 Blender Python API 연동)
blender_scene = {
    "objects": [],
    "scene_name": "Scene",
    "render_engine": "Cycles",
    "frame_current": 1,
    "frame_end": 250,
    "camera_location": [7.48, -6.51, 5.34],
    "light_objects": ["Light"]
}

@mcp.tool()
async def create_blender_object(
    object_type: str,
    name: str = None,
    location: List[float] = [0, 0, 0],
    rotation: List[float] = [0, 0, 0], 
    scale: List[float] = [1, 1, 1]
) -> str:
    """
    Blender에서 3D 오브젝트를 생성합니다.
    
    Args:
        object_type: 생성할 오브젝트 타입 (cube, sphere, cylinder, plane, monkey, cone, torus)
        name: 오브젝트 이름 (선택사항)
        location: 오브젝트 위치 [x, y, z] 
        rotation: 오브젝트 회전 [x, y, z] (라디안)
        scale: 오브젝트 크기 [x, y, z]
    """
    try:
        print(f"\n[DEBUG] Blender MCP: create_object called - {object_type} at {location}\n")
        
        # 오브젝트 이름 생성
        if not name:
            obj_count = len([obj for obj in blender_scene["objects"] if obj["type"] == object_type])
            name = f"{object_type.capitalize()}.{obj_count + 1:03d}"
        
        # 새 오브젝트 생성
        new_object = {
            "name": name,
            "type": object_type,
            "location": location,
            "rotation": rotation,
            "scale": scale,
            "created_time": asyncio.get_event_loop().time(),
            "materials": [],
            "modifiers": []
        }
        
        # 씬에 추가
        blender_scene["objects"].append(new_object)
        
        result = f"✅ Blender에서 {object_type} 오브젝트 '{name}'을 생성했습니다.\n"
        result += f"📍 위치: {location}\n"
        result += f"🔄 회전: {rotation}\n" 
        result += f"📏 크기: {scale}\n"
        result += f"🎯 총 오브젝트 수: {len(blender_scene['objects'])}개"
        
        logger.info(f"Blender 오브젝트 생성: {name} ({object_type})")
        return result
        
    except Exception as e:
        error_msg = f"❌ Blender 오브젝트 생성 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def get_blender_scene_info() -> str:
    """
    현재 Blender 씬의 상태 정보를 조회합니다.
    """
    try:
        print(f"\n[DEBUG] Blender MCP: get_scene_info called\n")
        
        # 오브젝트 타입별 개수 계산
        object_types = {}
        for obj in blender_scene["objects"]:
            obj_type = obj["type"]
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        result = f"🎬 Blender 씬 정보\n"
        result += f"📝 씬 이름: {blender_scene['scene_name']}\n"
        result += f"🎭 렌더 엔진: {blender_scene['render_engine']}\n"
        result += f"🎞️ 현재 프레임: {blender_scene['frame_current']}/{blender_scene['frame_end']}\n"
        result += f"📷 카메라 위치: {blender_scene['camera_location']}\n"
        result += f"🔆 조명 수: {len(blender_scene['light_objects'])}\n\n"
        
        result += f"📦 오브젝트 현황 (총 {len(blender_scene['objects'])}개):\n"
        if object_types:
            for obj_type, count in object_types.items():
                result += f"  • {obj_type}: {count}개\n"
        else:
            result += "  • 생성된 오브젝트가 없습니다.\n"
        
        # 최근 생성된 오브젝트 목록
        if blender_scene["objects"]:
            result += f"\n📋 오브젝트 목록:\n"
            for obj in blender_scene["objects"][-5:]:  # 최근 5개만 표시
                result += f"  • {obj['name']} ({obj['type']}) - 위치: {obj['location']}\n"
        
        logger.info("Blender 씬 정보 조회 완료")
        return result
        
    except Exception as e:
        error_msg = f"❌ Blender 씬 정보 조회 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def render_blender_scene(
    output_path: str = "render_output.png",
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    samples: int = 128
) -> str:
    """
    Blender 씬을 렌더링합니다.
    
    Args:
        output_path: 출력 파일 경로
        resolution_x: 렌더링 해상도 X
        resolution_y: 렌더링 해상도 Y  
        samples: 렌더링 샘플 수
    """
    try:
        print(f"\n[DEBUG] Blender MCP: render_scene called - {output_path}\n")
        
        # 렌더링 시뮬레이션 (실제로는 bpy.ops.render.render() 호출)
        await asyncio.sleep(1)  # 렌더링 시간 시뮬레이션
        
        render_info = {
            "output_path": output_path,
            "resolution": f"{resolution_x}x{resolution_y}",
            "samples": samples,
            "render_engine": blender_scene["render_engine"],
            "objects_count": len(blender_scene["objects"])
        }
        
        result = f"🎨 Blender 렌더링 완료!\n"
        result += f"📁 출력 파일: {output_path}\n"
        result += f"📐 해상도: {resolution_x}x{resolution_y}\n"
        result += f"🔢 샘플 수: {samples}\n"
        result += f"⚙️ 렌더 엔진: {blender_scene['render_engine']}\n"
        result += f"📦 렌더링된 오브젝트: {len(blender_scene['objects'])}개"
        
        logger.info(f"Blender 렌더링 완료: {output_path}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Blender 렌더링 실패: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    print("🎨 Blender MCP 서버 시작 중...")
    print("📡 포트: 8001")
    print("🔧 사용 가능한 도구:")
    print("  • create_blender_object - 3D 오브젝트 생성")
    print("  • get_blender_scene_info - 씬 정보 조회")
    print("  • render_blender_scene - 씬 렌더링")
    print("=" * 50)
    
    mcp.run(transport="stdio")
