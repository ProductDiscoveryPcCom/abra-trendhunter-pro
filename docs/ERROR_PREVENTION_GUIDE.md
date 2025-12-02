# 🛡️ GUÍA DE PREVENCIÓN DE ERRORES - ABRA

## 📋 TABLA DE CONTENIDOS

1. [Errores Comunes Resueltos](#errores-comunes-resueltos)
2. [Reglas de Imports](#reglas-de-imports)
3. [Validación Pre-Deployment](#validación-pre-deployment)
4. [Checklist de Calidad](#checklist-de-calidad)
5. [Troubleshooting Rápido](#troubleshooting-rápido)

---

## 🔴 ERRORES COMUNES RESUELTOS

### Error #1: "No module named 'analysis'"

**Síntoma:**
```python
ModuleNotFoundError: No module named 'analysis'
ImportError: No module named 'utils'
ImportError: No module named 'components'
```

**Causa:**
Imports relativos sin el prefix `abra.`

**❌ INCORRECTO:**
```python
from analysis.historical import save_analysis_to_history
from utils.helpers import export_to_csv
from components.render import render_query_with_bar
from config.constants import COUNTRIES
```

**✅ CORRECTO:**
```python
from abra.analysis.historical import save_analysis_to_history
from abra.utils.helpers import export_to_csv
from abra.components.render import render_query_with_bar
from abra.config.constants import COUNTRIES
```

**Dónde ocurre:**
- ✅ Dentro de funciones
- ✅ En cualquier parte del código
- ✅ En imports condicionales
- ✅ En todos los archivos .py

---

### Error #2: "name 'COUNTRIES' is not defined"

**Síntoma:**
```python
NameError: name 'COUNTRIES' is not defined
NameError: name 'CHANNELS' is not defined
NameError: name 'PRODUCT_CATEGORIES' is not defined
```

**Causa:**
Usar constantes sin importarlas

**❌ INCORRECTO:**
```python
# En insights.py
def analyze_brand(brand, countries):
    for geo in countries:
        country_name = COUNTRIES[geo]['name']  # ❌ No importado
```

**✅ CORRECTO:**
```python
# En insights.py
from abra.config.constants import COUNTRIES, CHANNELS, PRODUCT_CATEGORIES

def analyze_brand(brand, countries):
    for geo in countries:
        country_name = COUNTRIES[geo]['name']  # ✅ Importado
```

**Archivos donde se necesita:**
- ✅ insights.py
- ✅ historical.py
- ✅ render.py
- ✅ helpers.py
- ✅ Cualquier archivo que use estas constantes

---

### Error #3: Streamlit Cloud "Updating files failed"

**Síntoma:**
```
🐙 Pulling code changes from Github...
❗️ Updating the app files has failed: exit status 1
```

**Causas posibles:**
1. Cache corrupto en Streamlit Cloud
2. Conflictos de Git
3. Archivos grandes (>100MB)
4. .gitignore incorrecto

**✅ SOLUCIÓN:**
```bash
# Opción 1: Limpiar cache
# En Streamlit Cloud: Settings → Delete app → New app

# Opción 2: Force push limpio
git fetch origin
git reset --hard origin/main
git push --force

# Opción 3: Verificar .gitignore
cat .gitignore
# Debe incluir: __pycache__/, *.pyc, .streamlit/secrets.toml
```

---

## 📚 REGLAS DE IMPORTS

### ✅ REGLA #1: Siempre usa imports absolutos

```python
# ✅ CORRECTO - Import absoluto con prefix completo
from abra.analysis.insights import calculate_relevance
from abra.config.constants import COUNTRIES
from abra.utils.helpers import export_to_csv

# ❌ INCORRECTO - Import relativo sin prefix
from analysis.insights import calculate_relevance
from config.constants import COUNTRIES
from utils.helpers import export_to_csv
```

---

### ✅ REGLA #2: Imports al inicio del archivo

```python
# ✅ CORRECTO - Imports al inicio
import streamlit as st
import pandas as pd
from abra.config.constants import COUNTRIES
from abra.analysis.insights import analyze_brand

def my_function():
    result = analyze_brand(...)
    return result
```

```python
# ⚠️ EVITAR - Imports dentro de funciones (solo si es necesario)
def my_function():
    from abra.analysis.insights import analyze_brand  # Menos eficiente
    result = analyze_brand(...)
    return result
```

**Excepción:** Solo usa imports dentro de funciones si:
- Evitas imports circulares
- El módulo es pesado y se usa raramente
- Tienes una razón específica

---

### ✅ REGLA #3: Orden de imports

```python
# 1. Imports de la librería estándar
import os
import sys
import time
import json

# 2. Imports de terceros
import streamlit as st
import pandas as pd
import numpy as np

# 3. Imports locales (tu proyecto)
from abra.config.constants import COUNTRIES, CHANNELS
from abra.analysis.insights import analyze_brand
from abra.utils.helpers import export_to_csv
```

---

### ✅ REGLA #4: Nunca uses `import *`

```python
# ❌ INCORRECTO - Import wildcard
from abra.config.constants import *
from abra.utils.helpers import *

# ✅ CORRECTO - Import explícito
from abra.config.constants import COUNTRIES, CHANNELS, PRODUCT_CATEGORIES
from abra.utils.helpers import export_to_csv, export_to_excel
```

**Por qué:**
- `import *` hace el código difícil de entender
- No sabes qué se importó
- Puede causar conflictos de nombres

---

## 🔍 VALIDACIÓN PRE-DEPLOYMENT

### Script de Validación

**Ubicación:** `validate_imports.py` (raíz del proyecto)

**Uso:**
```bash
# Antes de cada deployment
python3 validate_imports.py

# Si pasa:
✅ Todos los imports son correctos
✅ Listo para deployment

# Si falla:
❌ Encontrados X problemas críticos
❌ Deployment bloqueado
```

**Integración en workflow:**
```bash
# 1. Hacer cambios en el código
# 2. Validar imports
python3 validate_imports.py

# 3. Solo si pasa, hacer commit
git add -A
git commit -m "Feature XYZ"
git push
```

---

### ⚙️ Pre-commit Hook (Opcional)

Crea `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validar imports antes de cada commit

echo "Validando imports..."
python3 validate_imports.py

if [ $? -ne 0 ]; then
    echo "❌ Commit bloqueado: imports incorrectos"
    echo "Ejecuta 'python3 validate_imports.py' para ver detalles"
    exit 1
fi

echo "✅ Imports validados"
exit 0
```

```bash
# Hacer ejecutable
chmod +x .git/hooks/pre-commit
```

---

## ✅ CHECKLIST DE CALIDAD

### Antes de cada Deployment

- [ ] **Validar imports**
  ```bash
  python3 validate_imports.py
  ```

- [ ] **Verificar que el proyecto se instala**
  ```bash
  pip install -e .
  ```

- [ ] **Verificar que app.py importa correctamente**
  ```bash
  python3 -c "from abra import __version__; print(f'Version: {__version__}')"
  ```

- [ ] **Verificar requirements.txt**
  ```bash
  # Debe incluir -e . como primera línea
  head -1 requirements.txt
  # Output esperado: -e .
  ```

- [ ] **Verificar .gitignore**
  ```bash
  # Debe existir e incluir:
  cat .gitignore | grep -E "__pycache__|*.pyc|secrets.toml"
  ```

- [ ] **Verificar constantes**
  ```bash
  python3 -c "from abra.config.constants import COUNTRIES; print(f'{len(COUNTRIES)} países')"
  # Output esperado: 7 países
  ```

- [ ] **Git status limpio**
  ```bash
  git status
  # No debe haber archivos sin commitear importantes
  ```

---

## 🔧 TROUBLESHOOTING RÁPIDO

### "ModuleNotFoundError: No module named 'abra'"

**Causa:** requirements.txt no tiene `-e .`

**Fix:**
```bash
# Verificar
head -1 requirements.txt

# Si no está, añadir al inicio
echo "-e ." > requirements.txt.new
cat requirements.txt >> requirements.txt.new
mv requirements.txt.new requirements.txt

# Commit
git add requirements.txt
git commit -m "Fix: Add -e . to requirements.txt"
git push
```

---

### "No module named 'analysis'"

**Causa:** Import relativo sin prefix `abra.`

**Fix:**
```bash
# 1. Ejecutar validador
python3 validate_imports.py

# 2. Ver problemas
# 3. Arreglar cada import:
#    from analysis.X → from abra.analysis.X
#    from utils.X   → from abra.utils.X
#    etc.

# 4. Re-validar
python3 validate_imports.py

# 5. Commit
git add -A
git commit -m "Fix: Correct imports to use abra. prefix"
git push
```

---

### "name 'COUNTRIES' is not defined"

**Causa:** Falta importar constante

**Fix:**
```python
# Al inicio del archivo donde se usa COUNTRIES:
from abra.config.constants import COUNTRIES

# Si también usas CHANNELS:
from abra.config.constants import COUNTRIES, CHANNELS

# Si usas todas:
from abra.config.constants import COUNTRIES, CHANNELS, PRODUCT_CATEGORIES
```

---

### Streamlit Cloud no actualiza

**Causa:** Cache o conflicto de Git

**Fix rápido:**
```
1. Streamlit Cloud → Tu app → Settings
2. Scroll abajo → "Delete app"
3. Confirmar delete
4. Home → "New app"
5. Seleccionar repo, branch, app.py
6. Añadir secrets si los tienes
7. Deploy
```

---

## 📊 ESTADÍSTICAS DE ERRORES RESUELTOS

```
v11.4.3: 3 imports incorrectos encontrados y corregidos
v11.4.1: 8 imports faltantes encontrados y corregidos

Total errores de imports resueltos: 11
Archivos afectados: 5
Crashes prevenidos: 15+
```

---

## 🎓 MEJORES PRÁCTICAS

### ✅ DO (Hacer)

1. **Siempre valida antes de push**
   ```bash
   python3 validate_imports.py && git push
   ```

2. **Usa imports absolutos**
   ```python
   from abra.module.submodule import function
   ```

3. **Importa solo lo necesario**
   ```python
   from abra.config.constants import COUNTRIES  # No todo
   ```

4. **Mantén imports organizados**
   - Estándar → Terceros → Locales

5. **Documenta imports no obvios**
   ```python
   # Import dentro de función para evitar import circular
   from abra.analysis.insights import analyze_brand
   ```

---

### ❌ DON'T (No hacer)

1. **No uses imports relativos sin prefix**
   ```python
   from analysis.insights import ...  # ❌
   ```

2. **No uses `import *`**
   ```python
   from abra.config.constants import *  # ❌
   ```

3. **No hagas push sin validar**
   ```bash
   git push  # ❌ Valida primero!
   ```

4. **No ignores warnings del validador**
   - Si el script advierte algo, investígalo

5. **No copies imports de otros archivos sin verificar**
   - Cada archivo puede necesitar diferentes imports

---

## 🚀 RESUMEN EJECUTIVO

```
1. Usa SIEMPRE: from abra.module import X
2. Nunca: from module import X (sin abra.)
3. Valida ANTES de deployment: python3 validate_imports.py
4. Si falla: arregla y re-valida
5. Solo push cuando ✅ pasa validación
```

**Con estas reglas, NO más errores de imports.** 🎯

---

**Documento creado:** 2025-12-02  
**Última actualización:** v11.4.3  
**Errores prevenidos:** ∞
