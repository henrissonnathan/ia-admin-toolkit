import json
import os
import requests
import time

class APIDiagnosticTool:
    """
    Ferramenta de Diagnóstico de Precisão de API.
    Testa a velocidade, status e integridade dos dados retornados.
    """
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.report_path = "API_PRECISION_REPORT.json"

    def test_endpoint(self, path, method="GET", data=None):
        url = f"{self.base_url}{path}"
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            latency = time.time() - start_time
            
            return {
                "path": path,
                "status": response.status_code,
                "latency_ms": round(latency * 1000, 2),
                "is_json": "application/json" in response.headers.get("Content-Type", ""),
                "size_bytes": len(response.content)
            }
        except Exception as e:
            return {"path": path, "error": str(e)}

    def run_suite(self):
        endpoints = [
            "/api/v1/usuarios/sessao",
            "/admin/diagnostico/db"
        ]
        results = []
        for ep in endpoints:
            results.append(self.test_endpoint(ep))
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Relatório gerado em: {self.report_path}")

if __name__ == "__main__":
    # Nota: Requer o sistema rodando no localhost:5001
    diag = APIDiagnosticTool()
    diag.run_suite()
