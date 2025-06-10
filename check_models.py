#!/usr/bin/env python3
"""
Ollama 모델 확인 및 추천 스크립트
현재 설치된 모델들과 추천 모델들을 확인합니다.
"""

import subprocess
import json
import requests
import sys

def check_ollama_status():
    """Ollama 서버 상태 확인"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except Exception as e:
        return False, str(e)

def get_system_info():
    """시스템 정보 확인"""
    try:
        # GPU 메모리 확인 (nvidia-smi가 있는 경우)
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpu_info = []
            for line in lines:
                total, used = line.split(', ')
                gpu_info.append({
                    'total_mb': int(total),
                    'used_mb': int(used),
                    'free_mb': int(total) - int(used)
                })
            return gpu_info
        else:
            return None
    except:
        return None

def recommend_models(gpu_memory_mb=None):
    """GPU 메모리 기준 모델 추천"""
    models = {
        'current_setup': [
            {'name': 'orieg/gemma3-tools:4b-it-qat', 'memory_req': 3000, 'desc': '🚀 현재 메인 모델 - 툴 기능 지원'},
            {'name': 'gemma3:4b', 'memory_req': 2500, 'desc': '🔧 현재 백업 모델 - 기본 응답'},
        ],
        'entry_level': [
            {'name': 'llama3.2:3b', 'memory_req': 2000, 'desc': '경량화, 낮은 메모리'},
            {'name': 'gemma2:2b', 'memory_req': 1500, 'desc': '매우 경량, 빠른 응답'}
        ],
        'mid_level': [
            {'name': 'qwen2.5-coder:7b', 'memory_req': 4500, 'desc': '코딩 특화, 빠른 응답'},
            {'name': 'llama3.1:8b', 'memory_req': 5500, 'desc': '안정적 성능'},
            {'name': 'qwen2.5:7b', 'memory_req': 4500, 'desc': '일반적 용도'},
            {'name': 'gemma2:9b', 'memory_req': 6000, 'desc': 'Google 최신'}
        ],
        'high_level': [
            {'name': 'qwen2.5-coder:14b', 'memory_req': 9000, 'desc': '코딩 특화, 고성능'},
            {'name': 'qwen2.5:14b', 'memory_req': 9000, 'desc': '균형잡힌 성능'},
            {'name': 'llama3.3:70b', 'memory_req': 42000, 'desc': 'Meta 최신, 최고 성능'}
        ],
        'premium': [
            {'name': 'qwen2.5:32b', 'memory_req': 20000, 'desc': '고성능, 정확성 우수'},
            {'name': 'qwen2.5:72b', 'memory_req': 45000, 'desc': '최고 수준 성능'},
            {'name': 'deepseek-v3:67b', 'memory_req': 40000, 'desc': '최신 DeepSeek, 코딩 우수'}
        ]
    }
    
    if gpu_memory_mb:
        print(f"🔍 GPU 메모리: {gpu_memory_mb} MB 기준 추천:")
        for category, model_list in models.items():
            suitable_models = [m for m in model_list if m['memory_req'] <= gpu_memory_mb * 0.8]  # 80% 여유
            if suitable_models:
                print(f"\n📋 {category.upper().replace('_', ' ')}:")
                for model in suitable_models:
                    print(f"  ✅ {model['name']} - {model['desc']} (메모리: {model['memory_req']}MB)")
    else:
        print("💾 GPU 정보를 확인할 수 없어 전체 모델 목록을 표시합니다:")
        for category, model_list in models.items():
            print(f"\n📋 {category.upper().replace('_', ' ')}:")
            for model in model_list:
                print(f"  • {model['name']} - {model['desc']} (메모리: {model['memory_req']}MB)")

def check_current_models():
    """현재 설정된 모델 확인"""
    print("🎯 현재 Dec207Hub 설정:")
    print("  메인 모델: orieg/gemma3-tools:4b-it-qat (툴 기능 지원)")
    print("  백업 모델: gemma3:4b (기본 응답)")
    print("  특징: 4B 모델로 매우 빠른 응답, 낮은 메모리 사용량")

def main():
    print("🤖 Dec207Hub 모델 현황 체크 (Gemma3 Setup)")
    print("=" * 60)
    
    # 현재 설정 표시
    check_current_models()
    
    # Ollama 상태 확인
    is_running, data = check_ollama_status()
    if not is_running:
        print("\n❌ Ollama 서버가 실행되지 않습니다.")
        print("   명령어: ollama serve")
        return
    
    print("\n✅ Ollama 서버 실행 중")
    
    # 현재 설치된 모델 확인
    if data and 'models' in data:
        print(f"\n📦 현재 설치된 모델 ({len(data['models'])}개):")
        target_models = ['orieg/gemma3-tools:4b-it-qat', 'gemma3:4b']
        
        for model in data['models']:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0) / (1024**3)  # GB 변환
            if name in target_models:
                print(f"  ✅ {name} ({size:.1f}GB) - 현재 사용 중")
            else:
                print(f"  • {name} ({size:.1f}GB)")
        
        # 필요한 모델이 없는 경우 안내
        missing_models = [m for m in target_models if not any(m in model.get('name', '') for model in data['models'])]
        if missing_models:
            print(f"\n⚠️ 누락된 필수 모델:")
            for model in missing_models:
                print(f"  ❌ {model}")
            print(f"\n🔧 설치 명령어:")
            for model in missing_models:
                print(f"  ollama pull {model}")
    
    # 시스템 정보 확인
    gpu_info = get_system_info()
    if gpu_info:
        print(f"\n🖥️ GPU 정보:")
        for i, gpu in enumerate(gpu_info):
            print(f"  GPU {i}: {gpu['total_mb']}MB 총용량, {gpu['free_mb']}MB 사용가능")
        
        # 가장 큰 GPU 메모리 기준 추천
        max_gpu_memory = max(gpu['free_mb'] for gpu in gpu_info)
        recommend_models(max_gpu_memory)
    else:
        print("\n🖥️ GPU 정보를 확인할 수 없습니다 (CPU 모드 또는 nvidia-smi 없음)")
        recommend_models()
    
    print(f"\n💡 Gemma3 기반 업그레이드 순서:")
    print(f"  1. 현재: orieg/gemma3-tools:4b-it-qat + gemma3:4b (4GB 메모리)")
    print(f"  2. 중급: qwen2.5-coder:7b (코딩 성능 향상)")
    print(f"  3. 고급: qwen2.5-coder:14b (더 높은 성능)")
    print(f"  4. 최고급: qwen2.5:32b (최고 성능)")
    
    print(f"\n🔧 모델 설치 명령어 예시:")
    print(f"  ollama pull orieg/gemma3-tools:4b-it-qat")
    print(f"  ollama pull gemma3:4b")
    print(f"  ollama pull qwen2.5-coder:7b")

if __name__ == "__main__":
    main()
