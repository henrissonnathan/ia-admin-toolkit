import os
import ast
import json
import re

def get_js_functions(file_path):
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic regex for JS functions: function name(...) or name = function(...) or name = (...) =>
            matches = re.finditer(r'(?:function\s+([a-zA-Z0-9_$]+)|([a-zA-Z0-9_$]+)\s*=\s*function|([a-zA-Z0-9_$]+)\s*=\s*\([^)]*\)\s*=>)', content)
            for m in matches:
                name = m.group(1) or m.group(2) or m.group(3)
                if name:
                    functions.append(name)
    except Exception as e:
        print(f"Error reading JS {file_path}: {e}")
    return list(set(functions))

def get_py_context(file_path):
    context = {"functions": [], "routes": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for route decorators
                    route = None
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and getattr(dec.func, 'attr', '') == 'route':
                            if dec.args:
                                route = dec.args[0].value if hasattr(dec.args[0], 'value') else str(dec.args[0])
                    
                    func_info = {"name": node.name, "doc": ast.get_docstring(node)}
                    if route:
                        context["routes"].append({"path": route, "function": node.name})
                    else:
                        context["functions"].append(func_info)
    except Exception as e:
        print(f"Error parsing PY {file_path}: {e}")
    return context

def generate_map():
    project_map = {
        "routes": {},
        "controllers": {},
        "static_js": {}
    }
    
    # Map Routes
    routes_dir = "routes"
    if os.path.exists(routes_dir):
        for f in os.listdir(routes_dir):
            if f.endswith(".py"):
                project_map["routes"][f] = get_py_context(os.path.join(routes_dir, f))
                
    # Map Controllers
    ctrl_dir = "controllers"
    if os.path.exists(ctrl_dir):
        for f in os.listdir(ctrl_dir):
            if f.endswith(".py"):
                project_map["controllers"][f] = get_py_context(os.path.join(ctrl_dir, f))
                
    # Map JS
    js_dir = "static/js"
    if os.path.exists(js_dir):
        for f in os.listdir(js_dir):
            if f.endswith(".js"):
                project_map["static_js"][f] = get_js_functions(os.path.join(js_dir, f))
                
    with open("TECHNICAL_MAP.json", "w", encoding="utf-8") as f:
        json.dump(project_map, f, indent=2, ensure_ascii=False)
    
    print("TECHNICAL_MAP.json generated successfully.")

if __name__ == "__main__":
    generate_map()
