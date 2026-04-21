GitHub 上传前脱敏脚本 - 清理版本
"""  import os import re from pathlib import Path from typing import List, Tuple  SANITIZE_RULES: List[Tuple[str, str]] = [     # Workspace ID → 占位符     (r'workspaces/[A-Za-z0-9]{5}', 'workspaces/YOUR_WORKSPACE'),          # 可能的敏感信息     (r'api[_-]?key\s*[=:]\s*["\'][A-Za-z0-9]+["\']', 'api_key: "YOUR_API_KEY"'),
    (r'secret\s*[=:]\s*["\'][A-Za-z0-9]+["\']', 'secret: "YOUR_SECRET"'),
    (r'token\s*[=:]\s*["\'][A-Za-z0-9]+["\']', 'token: "YOUR_TOKEN"'),
    
    # 邮箱地址
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'your.email@example.com'),
]

SKIP_PATTERNS = [
    '.git', '__pycache__', '*.pyc', '*.db', '*.sqlite', '*.log',
    '.DS_Store', 'venv', 'env', '.venv', 'node_modules',
]

def should_skip(path: Path) -> bool:
    path_str = str(path)
    for pattern in SKIP_PATTERNS:
        if pattern in path_str:
            return True
    return False

def sanitize_content(content: str, file_path: str) -> str:
    original = content
    for pattern, replacement in SANITIZE_RULES:
        content = re.sub(pattern, replacement, content)
    if content != original:
        print(f"  ✓ 脱敏：{file_path}")
    return content

def main():
    import argparse
    parser = argparse.ArgumentParser(description='GitHub 脱敏脚本')
    parser.add_argument('--dir', type=str, default='.', help='要脱敏的目录')
    args = parser.parse_args()
    
    root_path = Path(args.dir)
    stats = {'processed': 0, 'modified': 0, 'skipped': 0}
    
    print(f"\n🔍 开始脱敏检查：{args.dir}\n")
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and not should_skip(file_path):
            stats['processed'] += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                sanitized = sanitize_content(content, str(file_path))
                if sanitized != content:
                    stats['modified'] += 1
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(sanitized)
                else:
                    stats['skipped'] += 1
            except Exception as e:
                stats['skipped'] += 1
    
    print(f"\n✅ 完成：处理 {stats['processed']} 个文件，修改 {stats['modified']} 个，跳过 {stats['skipped']} 个\n")

if __name__ == '__main__':
    main()
