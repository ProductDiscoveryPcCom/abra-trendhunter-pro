#!/usr/bin/env python3
"""
ABRA - Import Validator
Valida que todos los imports usan el formato correcto con prefix 'abra.'

Ejecutar antes de cada deployment:
    python3 validate_imports.py

Exit codes:
    0 = Todos los imports correctos
    1 = Se encontraron imports incorrectos
"""

import ast
import os
import sys
from pathlib import Path

# Módulos internos que DEBEN usar prefix "abra."
INTERNAL_MODULES = ['analysis', 'components', 'config', 'core', 'pages', 'ui', 'utils']

# Colores para terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

issues = []
files_checked = 0
warnings = []


def check_file(filepath):
    """Revisa un archivo Python en busca de imports incorrectos"""
    global files_checked
    files_checked += 1
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=filepath)
        
        for node in ast.walk(tree):
            # Check ImportFrom statements
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module_parts = node.module.split('.')
                    
                    # CRITICAL: Import from internal module without abra prefix
                    if module_parts[0] in INTERNAL_MODULES:
                        issues.append({
                            'file': filepath,
                            'line': node.lineno,
                            'severity': 'CRITICAL',
                            'type': 'ImportFrom',
                            'module': node.module,
                            'code': f"from {node.module} import ...",
                            'fix': f"from abra.{node.module} import ..."
                        })
                    
                    # WARNING: Relative imports from internal modules
                    if node.level > 0 and len(module_parts) > 0:
                        if module_parts[0] in INTERNAL_MODULES or (node.module and module_parts[-1] in INTERNAL_MODULES):
                            warnings.append({
                                'file': filepath,
                                'line': node.lineno,
                                'severity': 'WARNING',
                                'type': 'RelativeImport',
                                'module': node.module,
                                'level': node.level,
                                'code': f"from {'.' * node.level}{node.module} import ...",
                                'note': 'Los imports relativos pueden causar problemas en deployment'
                            })
            
            # Check Import statements
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name_parts = alias.name.split('.')
                    if name_parts[0] in INTERNAL_MODULES:
                        issues.append({
                            'file': filepath,
                            'line': node.lineno,
                            'severity': 'CRITICAL',
                            'type': 'Import',
                            'module': alias.name,
                            'code': f"import {alias.name}",
                            'fix': f"import abra.{alias.name}"
                        })
    
    except SyntaxError as e:
        warnings.append({
            'file': filepath,
            'line': getattr(e, 'lineno', 0),
            'severity': 'ERROR',
            'type': 'SyntaxError',
            'code': str(e),
            'note': 'Este archivo tiene errores de sintaxis'
        })
    except Exception as e:
        warnings.append({
            'file': filepath,
            'line': 0,
            'severity': 'ERROR',
            'type': 'ParseError',
            'code': str(e),
            'note': f'No se pudo analizar este archivo'
        })


def main():
    """Función principal"""
    print(f"{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}ABRA - VALIDADOR DE IMPORTS{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")
    print()
    
    # Check all Python files in abra/
    if os.path.exists('abra'):
        for root, dirs, files in os.walk('abra'):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    check_file(filepath)
    
    # Check app.py
    if os.path.exists('app.py'):
        check_file('app.py')
    
    # Print results
    print(f"Archivos revisados: {files_checked}")
    print()
    
    # Print critical issues
    if issues:
        print(f"{RED}{'=' * 80}{RESET}")
        print(f"{RED}❌ ENCONTRADOS {len(issues)} PROBLEMAS CRÍTICOS{RESET}")
        print(f"{RED}{'=' * 80}{RESET}")
        print()
        
        by_file = {}
        for issue in issues:
            if issue['file'] not in by_file:
                by_file[issue['file']] = []
            by_file[issue['file']].append(issue)
        
        for filepath, file_issues in sorted(by_file.items()):
            print(f"{RED}📄 {filepath}{RESET}")
            print("-" * 80)
            for issue in sorted(file_issues, key=lambda x: x['line']):
                print(f"  {RED}Línea {issue['line']:4d}{RESET}: {issue['code']}")
                print(f"  {GREEN}Fix{RESET}:        {issue['fix']}")
                print()
        
        print(f"{RED}{'=' * 80}{RESET}")
        print(f"{RED}DEPLOYMENT BLOQUEADO - Corrige estos imports primero{RESET}")
        print(f"{RED}{'=' * 80}{RESET}")
        print()
        
        # Print fix instructions
        print(f"{YELLOW}CÓMO ARREGLAR:{RESET}")
        print()
        print("Reemplaza cada import incorrecto con su versión correcta:")
        print()
        for issue in issues[:5]:  # Show first 5
            print(f"  {RED}❌{RESET} {issue['code']}")
            print(f"  {GREEN}✅{RESET} {issue['fix']}")
            print()
        
        if len(issues) > 5:
            print(f"  ... y {len(issues) - 5} más")
            print()
        
        return 1
    
    # Print warnings
    if warnings:
        print(f"{YELLOW}{'=' * 80}{RESET}")
        print(f"{YELLOW}⚠️  {len(warnings)} ADVERTENCIAS{RESET}")
        print(f"{YELLOW}{'=' * 80}{RESET}")
        print()
        
        for warning in warnings:
            print(f"{YELLOW}📄 {warning['file']} (línea {warning['line']}){RESET}")
            print(f"  {warning['code']}")
            if 'note' in warning:
                print(f"  Nota: {warning['note']}")
            print()
    
    # Success
    print(f"{GREEN}{'=' * 80}{RESET}")
    print(f"{GREEN}✅ TODOS LOS IMPORTS SON CORRECTOS{RESET}")
    print(f"{GREEN}{'=' * 80}{RESET}")
    print()
    print(f"{GREEN}✓{RESET} {files_checked} archivos verificados")
    print(f"{GREEN}✓{RESET} 0 problemas críticos")
    print(f"{GREEN}✓{RESET} Listo para deployment")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
