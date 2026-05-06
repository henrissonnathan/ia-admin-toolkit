"""
TRPROC LicitaPRO - Gerenciador Visual do Ambiente de Desenvolvimento
=====================================================================
Interface gráfica que gerencia MySQL, Servidor Flask e navegador.
Possui dois modos: Normal (login do site) e Testes (painel E2E/RBAC).
Extensão .pyw para NÃO abrir janela CMD.
"""
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import webbrowser
import time

# ── Caminhos ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "static", "img", "logo-trproc.png")
LOGO_CLEAR_PATH = os.path.join(BASE_DIR, "static", "img", "logo-trproc-clear.png")
MYSQL_START = r"C:\xampp\mysql_start.bat"
FLASK_SCRIPT = os.path.join(BASE_DIR, "TRPROC_WEB.py")
ICO_PATH = os.path.join(BASE_DIR, "static", "img", "trproc-launcher.ico")
SITE_URL = "http://localhost:5001/action-center"
TESTER_URL = "http://localhost:5001/dev/tester"


class TrprocLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.flask_process = None
        self.reader_thread = None
        self._stop_reader = False
        self._server_running = False

        # ── Janela ──
        self.title("TRPROC LicitaPRO")
        self.geometry("780x620")
        self.resizable(False, False)
        self.configure(bg="#0f172a")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Carrega logo
        self._logo_img = None
        for path in [LOGO_CLEAR_PATH, LOGO_PATH]:
            try:
                self._logo_img = tk.PhotoImage(file=path)
                # Reduz para caber bonito no header
                if self._logo_img.width() > 120:
                    factor = self._logo_img.width() // 120
                    if factor > 1:
                        self._logo_img = self._logo_img.subsample(factor, factor)
                self.iconphoto(True, self._logo_img)
                break
            except Exception:
                continue

        # Tenta usar .ico para ícone da barra de tarefas
        try:
            if os.path.exists(ICO_PATH):
                self.iconbitmap(ICO_PATH)
        except Exception:
            pass

        self._build_ui()
        self._log("Gerenciador TRPROC pronto. Clique em 'Iniciar Servidor' para começar.", tag="system")

    # ═══════════════════════════════════════════
    #  INTERFACE
    # ═══════════════════════════════════════════
    def _build_ui(self):
        # ── HEADER ──
        header = tk.Frame(self, bg="#0f172a", pady=14)
        header.pack(fill="x")

        if self._logo_img:
            tk.Label(header, image=self._logo_img, bg="#0f172a").pack()

        tk.Label(
            header, text="TRPROC LicitaPRO",
            font=("Segoe UI", 22, "bold"), fg="#60a5fa", bg="#0f172a"
        ).pack()
        tk.Label(
            header, text="Gerenciador do Ambiente de Desenvolvimento",
            font=("Segoe UI", 10), fg="#64748b", bg="#0f172a"
        ).pack()

        # ── BARRA DE STATUS ──
        self._status_var = tk.StringVar(value="⏸  Servidor Parado")
        self._status_label = tk.Label(
            self, textvariable=self._status_var,
            font=("Segoe UI", 11, "bold"), fg="#fbbf24", bg="#1e293b", pady=6
        )
        self._status_label.pack(fill="x")

        # ── CONTROLE DO SERVIDOR ──
        srv_frame = tk.Frame(self, bg="#0f172a", pady=8)
        srv_frame.pack(fill="x", padx=20)

        bstyle = dict(
            font=("Segoe UI", 10, "bold"), fg="white",
            relief="flat", cursor="hand2", padx=10, pady=7, bd=0
        )

        self.btn_start_srv = tk.Button(
            srv_frame, text="⚡ Iniciar Servidor", bg="#10b981",
            activebackground="#059669", command=self._start_all, **bstyle
        )
        self.btn_start_srv.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_restart = tk.Button(
            srv_frame, text="🔄 Reiniciar", bg="#6366f1",
            activebackground="#4f46e5", command=self._restart, **bstyle
        )
        self.btn_restart.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_stop = tk.Button(
            srv_frame, text="⏹ Parar", bg="#ef4444",
            activebackground="#dc2626", command=self._stop_flask, **bstyle
        )
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_tunel = tk.Button(
            srv_frame, text="🌐 Ligar Túnel", bg="#f97316",
            activebackground="#ea580c", command=self._start_tunnel, **bstyle
        )
        self.btn_tunel.pack(side="left", expand=True, fill="x", padx=3)

        # ── SEPARADOR ──
        tk.Frame(self, bg="#1e293b", height=1).pack(fill="x", padx=20, pady=8)

        # ── MODOS DE ACESSO ──
        mode_label = tk.Label(
            self, text="NÍVEIS DE ACESSO AO SISTEMA",
            font=("Segoe UI", 9, "bold"), fg="#475569", bg="#0f172a"
        )
        mode_label.pack(pady=(0, 5))

        # --- LINHA 1: ACESSO POR NÍVEL ---
        access_frame = tk.Frame(self, bg="#0f172a")
        access_frame.pack(fill="x", padx=20, pady=5)

        # Botão SUPER ADMIN
        btn_super = tk.Button(
            access_frame, text="⚡ Super Admin",
            font=("Segoe UI", 11, "bold"), fg="white", bg="#ef4444",
            activebackground="#dc2626", relief="flat", cursor="hand2",
            padx=10, pady=10, bd=0,
            command=lambda: self._open_url("http://localhost:5001/dev/tester/autologin/super_admin", "Abrindo como Super Administrador...")
        )
        btn_super.pack(side="left", expand=True, fill="both", padx=2)

        # Botão ADMIN
        btn_admin = tk.Button(
            access_frame, text="👑 Administrador",
            font=("Segoe UI", 11, "bold"), fg="white", bg="#3b82f6",
            activebackground="#2563eb", relief="flat", cursor="hand2",
            padx=10, pady=10, bd=0,
            command=lambda: self._open_url("http://localhost:5001/dev/tester/autologin/admin", "Abrindo como Administrador...")
        )
        btn_admin.pack(side="left", expand=True, fill="both", padx=2)

        # Botão CLIENTE
        btn_cliente = tk.Button(
            access_frame, text="👤 Usuário Cliente",
            font=("Segoe UI", 11, "bold"), fg="white", bg="#10b981",
            activebackground="#059669", relief="flat", cursor="hand2",
            padx=10, pady=10, bd=0,
            command=lambda: self._open_url("http://localhost:5001/dev/tester/autologin/cliente", "Abrindo como Cliente...")
        )
        btn_cliente.pack(side="left", expand=True, fill="both", padx=2)

        # --- LINHA 2: FERRAMENTAS ---
        tk.Label(
            self, text="FERRAMENTAS DE DIAGNÓSTICO",
            font=("Segoe UI", 8, "bold"), fg="#475569", bg="#0f172a"
        ).pack(pady=(10, 2))

        tools_frame = tk.Frame(self, bg="#0f172a")
        tools_frame.pack(fill="x", padx=20, pady=5)

        # Botão TESTES
        btn_tester = tk.Button(
            tools_frame, text="🧪 Painel de Testes",
            font=("Segoe UI", 10, "bold"), fg="white", bg="#f59e0b",
            activebackground="#d97706", relief="flat", cursor="hand2",
            padx=8, pady=8, bd=0,
            command=lambda: self._open_url(TESTER_URL, "Abrindo Painel de Testes E2E...")
        )
        btn_tester.pack(side="left", expand=True, fill="both", padx=2)

        # Botão EXPORTAR
        btn_debug = tk.Button(
            tools_frame, text="📥 Exportar Erros",
            font=("Segoe UI", 10, "bold"), fg="white", bg="#8b5cf6",
            activebackground="#7c3aed", relief="flat", cursor="hand2",
            padx=8, pady=8, bd=0,
            command=lambda: self._open_url("http://localhost:5001/dev/tester/api/debug/erros?limit=1000", "Baixando Logs de Erro...")
        )
        btn_debug.pack(side="left", expand=True, fill="both", padx=2)

        # ── CONSOLE ──
        tk.Label(
            self, text="  Terminal de Saída",
            font=("Consolas", 9), fg="#475569", bg="#020617",
            anchor="w", padx=8, pady=3
        ).pack(fill="x", padx=20, pady=(10, 0))

        self.console = scrolledtext.ScrolledText(
            self, wrap="word", font=("Consolas", 9),
            bg="#020617", fg="#cbd5e1", insertbackground="white",
            relief="flat", height=10, state="disabled",
            selectbackground="#334155"
        )
        self.console.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        self.console.tag_config("info", foreground="#60a5fa")
        self.console.tag_config("success", foreground="#34d399")
        self.console.tag_config("error", foreground="#f87171")
        self.console.tag_config("system", foreground="#fbbf24")

    # ═══════════════════════════════════════════
    #  LÓGICA
    # ═══════════════════════════════════════════
    def _log(self, msg, tag="info"):
        ts = time.strftime("%H:%M:%S")
        self.console.configure(state="normal")
        self.console.insert("end", f"[{ts}] {msg}\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_status(self, text, color):
        self._status_var.set(text)
        self._status_label.configure(fg=color)

    def _open_url(self, url, msg):
        if not self._server_running:
            self._log("Servidor não está rodando! Clique em 'Iniciar Servidor' primeiro.", tag="error")
            return
        self._log(msg, tag="info")
        webbrowser.open(url)

    # ── Servidor ──
    def _start_all(self):
        if self.flask_process and self.flask_process.poll() is None:
            self._log("Servidor já está rodando.", tag="system")
            return

        self._log("Iniciando MySQL (XAMPP)...", tag="system")
        try:
            subprocess.Popen([MYSQL_START], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self._log("MySQL iniciado.", tag="success")
        except Exception as e:
            self._log(f"Aviso MySQL: {e}", tag="error")

        self.after(3000, self._start_flask)

    def _start_flask(self):
        self._log("Iniciando Flask (TRPROC_WEB.py)...", tag="system")
        self._set_status("⏳  Iniciando...", "#fbbf24")

        for cmd in [["py", FLASK_SCRIPT], ["python", FLASK_SCRIPT]]:
            try:
                self.flask_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    cwd=BASE_DIR, text=True, bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                break
            except FileNotFoundError:
                continue
        else:
            self._log("ERRO: Python não encontrado!", tag="error")
            self._set_status("❌  Erro", "#ef4444")
            return

        self._server_running = True
        self._set_status("✅  Servidor Rodando (porta 5001)", "#10b981")
        self._log("Servidor Flask iniciado!", tag="success")

        self._stop_reader = False
        self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self.reader_thread.start()

    def _start_tunnel(self):
        self._log("Iniciando Túnel Cloudflare Seguro...", tag="system")
        # Procura cloudflared.exe em vários locais possíveis
        tunnel_token = 'eyJhIjoiZTRjN2EyZGExOGIxMjQwNWEwY2FmYjdhMDk1NjE0OWEiLCJ0IjoiZDkxYThhNjQtNzEwMS00NWViLWEwNDQtY2MzNWJiMjBmOWEyIiwicyI6Ik5ESTFPV1poWmpBdE5EWm1aQzAwWTJFMUxUZzVaVFl0WldNeE5XWmxORFUxTVROaCJ9'
        search_paths = [
            os.path.join(BASE_DIR, "cloudflared.exe"),
            r"c:\Robos\IZA\cloudflared.exe",
            os.path.expanduser(r"~\Desktop\Nova pasta\Robos\IZA\cloudflared.exe"),
        ]
        cf_path = None
        for p in search_paths:
            if os.path.exists(p):
                cf_path = p
                break
        if not cf_path:
            self._log("❌ cloudflared.exe NÃO encontrado!", tag="error")
            self._log(f"   Coloque-o em: {search_paths[0]}", tag="system")
            return
        cf_dir = os.path.dirname(cf_path)
        tunnel_cmd = f'cd /d "{cf_dir}" && .\\cloudflared.exe tunnel run --token {tunnel_token}'
        try:
            subprocess.Popen(f'start cmd /k "{tunnel_cmd}"', shell=True)
            self._log(f"Túnel iniciado via {cf_path}", tag="success")
        except Exception as e:
            self._log(f"ERRO ao iniciar túnel: {e}", tag="error")

    def _read_output(self):
        try:
            for line in self.flask_process.stdout:
                if self._stop_reader:
                    break
                s = line.strip()
                if s:
                    tag = "info"
                    low = s.lower()
                    if "error" in low or "erro" in low or "traceback" in low:
                        tag = "error"
                    elif "sucesso" in low or "success" in low or "running on" in low:
                        tag = "success"
                    elif "debug" in low or "warning" in low or "aviso" in low:
                        tag = "system"
                    self.after(0, self._log, s, tag)
        except Exception:
            pass
        self.after(0, self._on_flask_stopped)

    def _on_flask_stopped(self):
        if self.flask_process and self.flask_process.poll() is not None:
            self._log(f"Flask encerrado (código {self.flask_process.poll()}).", tag="system")
            self._set_status("⏸  Servidor Parado", "#fbbf24")
            self.flask_process = None
            self._server_running = False

    def _stop_flask(self):
        self._stop_reader = True
        if self.flask_process and self.flask_process.poll() is None:
            self._log("Encerrando Flask...", tag="system")
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
            except Exception:
                try: self.flask_process.kill()
                except Exception: pass
            self.flask_process = None
            self._server_running = False
            self._set_status("⏸  Servidor Parado", "#fbbf24")
            self._log("Servidor parado.", tag="success")
        else:
            self._log("Nenhum servidor em execução.", tag="system")

    def _restart(self):
        self._log("Reiniciando...", tag="system")
        self._stop_flask()
        self.after(1500, self._start_flask)

    def _on_close(self):
        self._stop_reader = True
        if self.flask_process and self.flask_process.poll() is None:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=3)
            except Exception:
                try: self.flask_process.kill()
                except Exception: pass
        self.destroy()


if __name__ == "__main__":
    app = TrprocLauncher()
    app.mainloop()
