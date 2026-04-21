# Solver de Programación Lineal — 2 Variables

Aplicación web para resolver problemas de programación lineal de 2 variables usando el **Método Simplex**. Permite ingresar una función objetivo (Maximizar o Minimizar) y cualquier número de restricciones lineales, y muestra:

- La **región factible** graficada de forma interactiva
- El **punto óptimo** marcado en el gráfico
- Las **tablas del Método Simplex** iteración por iteración
- Un **historial** de problemas resueltos durante la sesión

---

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- [Python 3.10 o superior](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

Para verificar que los tienes, abre una terminal y ejecuta:

```bash
python --version
git --version
```

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd <nombre-de-la-carpeta>
```

### 2. Crear un entorno virtual

Un entorno virtual mantiene las dependencias del proyecto separadas del resto de tu sistema.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno esté activo, verás `(venv)` al inicio de tu terminal.

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

Esto abrirá automáticamente el navegador en `http://localhost:8501`. Si no abre solo, copia esa dirección y pégala en tu navegador.

---

## Cómo usar la aplicación

1. En el panel izquierdo, escribe una **descripción** opcional del problema.
2. Elige **Maximizar** o **Minimizar**.
3. Ingresa los coeficientes `cx` y `cy` de la función objetivo `f(x, y) = cx·x + cy·y`.
4. Agrega tus **restricciones** (`a·x + b·y ≤ / ≥ / = rhs`) con los botones ➕ y ➖.
5. Presiona **Resolver**.

> Las restricciones `x ≥ 0` e `y ≥ 0` se asumen siempre de forma implícita.

---

## Ejemplo rápido

**Maximizar** `f(x, y) = 3x + 5y` sujeto a:

| a | b | op | rhs |
|---|---|----|-----|
| 1 | 0 | ≤  | 4   |
| 0 | 2 | ≤  | 12  |
| 3 | 2 | ≤  | 18  |

Resultado esperado: `x* = 2`, `y* = 6`, `f* = 36`

---

## Dependencias

| Librería | Uso |
|----------|-----|
| `streamlit` | Framework de la interfaz web |
| `numpy` | Implementación del algoritmo Simplex |
| `plotly` | Gráficas interactivas de la región factible |
| `scipy` | Verificación numérica de resultados |

---

## Versión en línea

La aplicación también está disponible en Streamlit Cloud (sin necesidad de instalar nada):

> 🔗 _Enlace disponible próximamente_
