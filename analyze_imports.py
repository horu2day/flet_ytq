# analyze_imports.py
import os
import ast
import sys
from collections import defaultdict

def get_imports(path):
    imports = set()
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    imports.add(name.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.add(node.module.split('.')[0])
                    except:
                        continue
    return imports

# 현재 디렉토리의 모든 .py 파일 분석
used_imports = get_imports('.')

# 설치된 패키지 확인
import pkg_resources
installed_packages = {pkg.key for pkg in pkg_resources.working_set}

# 사용 중인 패키지 출력
print("실제 사용 중인 패키지:")
for imp in sorted(used_imports):
    if imp in installed_packages:
        print(f"- {imp}")

# 제외할 수 있는 패키지 목록 생성
excludes = []
for pkg in installed_packages:
    if pkg not in used_imports and pkg not in ['pip', 'setuptools', 'wheel']:
        excludes.append(pkg)

print("\n제외 가능한 패키지:")
print(f"excludes={excludes}")