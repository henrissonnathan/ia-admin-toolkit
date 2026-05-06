import requests
import random
import string
import time

# Configurações
BASE_URL = "http://localhost:5001"
TARGET_ENDPOINTS = [
    {"url": "/api/perguntas", "method": "POST", "fields": ["pergunta", "slug", "tipo"]},
    {"url": "/api/v1/admin/usuarios", "method": "POST", "fields": ["nome", "email"]},
    # Adicionar mais conforme necessário
]

def generate_random_string(length, chars=string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.choice(chars) for _ in range(length))

def run_fuzz_test():
    print("🚀 Iniciando Smart Fuzzer TRPROC...")
    
    for target in TARGET_ENDPOINTS:
        print(f"\nTesting endpoint: {target['url']}")
        
        # Test Case 1: Long Strings (Overflow Test)
        payload = {field: generate_random_string(5000) for field in target['fields']}
        print(f"  - Teste de String Longa (5000 chars)...", end=" ")
        try:
            resp = requests.request(target['method'], f"{BASE_URL}{target['url']}", json=payload, timeout=5)
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"ERRO: {e}")

        # Test Case 2: Special Characters (SQLi/XSS candidates)
        special_chars = "' OR '1'='1' -- <script>alert(1)</script> \"); DROP TABLE usuarios; --"
        payload = {field: special_chars for field in target['fields']}
        print(f"  - Teste de Caracteres Especiais/Injeção...", end=" ")
        try:
            resp = requests.request(target['method'], f"{BASE_URL}{target['url']}", json=payload, timeout=5)
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"ERRO: {e}")

        # Test Case 3: Empty/Null fields
        payload = {field: None for field in target['fields']}
        print(f"  - Teste de Campos Nulos...", end=" ")
        try:
            resp = requests.request(target['method'], f"{BASE_URL}{target['url']}", json=payload, timeout=5)
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"ERRO: {e}")

    print("\n✅ Fuzz Testing concluído.")

if __name__ == "__main__":
    # Nota: requer que o servidor esteja rodando
    run_fuzz_test()
