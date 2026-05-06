"""
Documentador Power BI - Interface Gráfica
==========================================
Interface moderna para gerar documentação de projetos Power BI (.pbip)
Suporta seleção de múltiplas pastas para processamento em lote.

Uso: Execute este arquivo (duplo clique ou python documentador_gui.py)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading
from pathlib import Path

# Importa o documentador principal
try:
    from documentador_pbip import DocumentadorPBIP
except ImportError:
    messagebox.showerror("Erro Fatal", "Arquivo 'documentador_pbip.py' não encontrado!\nCertifique-se de que está na mesma pasta.")
    sys.exit(1)


class DocumentadorGUI:
    """Interface gráfica para o Documentador Power BI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Documentador Power BI")
        self.root.geometry("850x800")
        
        # Não permite redimensionar para manter o design consistente
        self.root.resizable(False, False)
        
        # ========================================================================
        # CORES & ESTILO (Tema Dark Moderno)
        # ========================================================================
        self.cor_fundo = "#1e1e2e"
        self.cor_container = "#313244"
        self.cor_input_bg = "#45475a"
        self.cor_destaque = "#89b4fa"
        self.cor_texto = "#cdd6f4"
        self.cor_texto_sec = "#a6adc8"
        self.cor_sucesso = "#a6e3a1"
        self.cor_erro = "#f38ba8"
        self.cor_botao = "#89b4fa"
        self.cor_botao_txt = "#1e1e2e"
        self.cor_aviso = "#f9e2af"
        
        self.root.configure(bg=self.cor_fundo)
        
        # Variáveis
        self.projetos_encontrados: list[dict] = []  # [{"caminho": str, "nome": str}]
        self.status_texto = tk.StringVar(value="Selecione uma pasta raiz contendo projetos Power BI...")
        self.contador_texto = tk.StringVar(value="Nenhum projeto encontrado")
        self.caminho_raiz = tk.StringVar(value="")
        self.formato_saida = tk.StringVar(value="pdf")  # pdf | md | docx | todos
        
        self._criar_interface()
        self._centralizar_janela()

    def _criar_botao(self, parent, text, font, bg, fg, active_bg, active_fg, command, **kwargs):
        """Cria um botão com efeito hover automático"""
        btn = tk.Button(
            parent, text=text, font=font,
            bg=bg, fg=fg,
            activebackground=active_bg, activeforeground=active_fg,
            relief=tk.FLAT, bd=0, cursor="hand2", command=command, **kwargs
        )
        
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn['background'] = active_bg
                btn['foreground'] = active_fg
                
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn['background'] = bg
                btn['foreground'] = fg
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _criar_interface(self):
        """Cria todos os elementos da interface"""
        
        # --- CONTAINER PRINCIPAL ---
        main_frame = tk.Frame(self.root, bg=self.cor_fundo, padx=40, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- CABEÇALHO ---
        header_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        icon_label = tk.Label(
            header_frame, text="📊",
            font=("Segoe UI Emoji", 42),
            bg=self.cor_fundo, fg=self.cor_destaque
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        texto_header_frame = tk.Frame(header_frame, bg=self.cor_fundo)
        texto_header_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            texto_header_frame, text="Documentador Power BI",
            font=("Segoe UI", 24, "bold"),
            fg=self.cor_texto, bg=self.cor_fundo, anchor="w"
        ).pack(fill=tk.X)
        
        tk.Label(
            texto_header_frame,
            text="Selecione a pasta raiz e escolha quais projetos documentar",
            font=("Segoe UI", 11),
            fg=self.cor_texto_sec, bg=self.cor_fundo, anchor="w"
        ).pack(fill=tk.X, pady=(2, 0))
        
        # --- SELEÇÃO DA PASTA RAIZ ---
        tk.Label(
            main_frame, text="Pasta Raiz",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_fundo, fg=self.cor_texto, anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))
        
        raiz_frame = tk.Frame(main_frame, bg=self.cor_container, padx=15, pady=15)
        raiz_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Entry com "border" usando Frame
        entry_border = tk.Frame(raiz_frame, bg=self.cor_input_bg, highlightbackground=self.cor_input_bg, highlightcolor=self.cor_destaque, highlightthickness=1)
        entry_border.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.entry_raiz = tk.Entry(
            entry_border, textvariable=self.caminho_raiz,
            font=("Consolas", 11),
            bg=self.cor_input_bg, fg=self.cor_texto,
            readonlybackground=self.cor_input_bg,
            insertbackground=self.cor_texto,
            relief=tk.FLAT, state="readonly", bd=0
        )
        self.entry_raiz.pack(fill=tk.X, expand=True, padx=8, pady=8)
        
        self._criar_botao(
            raiz_frame, text="📂 Selecionar Pasta",
            font=("Segoe UI", 10, "bold"),
            bg=self.cor_texto, fg=self.cor_fundo,
            active_bg="#ffffff", active_fg=self.cor_fundo,
            command=self._selecionar_pasta_raiz,
            padx=15, pady=8
        ).pack(side=tk.RIGHT, padx=(15, 0))
        
        # --- LISTA DE PROJETOS ENCONTRADOS ---
        tk.Label(
            main_frame, text="Projetos Encontrados",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_fundo, fg=self.cor_texto, anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))
        
        projetos_frame = tk.Frame(main_frame, bg=self.cor_container, padx=15, pady=15)
        # O pack será feito no final para garantir que o layout responsivo funcione
        
        # Dica de uso
        self.label_dica = tk.Label(
            projetos_frame,
            text="💡 Use Ctrl+Clique para selecionar vários  |  Shift+Clique para intervalo  |  Ctrl+A para todos",
            font=("Segoe UI", 9),
            fg=self.cor_texto_sec, bg=self.cor_container,
            anchor="w"
        )
        self.label_dica.pack(fill=tk.X, pady=(0, 10))
        
        # Listbox container
        listbox_border = tk.Frame(projetos_frame, bg=self.cor_input_bg, highlightbackground=self.cor_input_bg, highlightcolor=self.cor_destaque, highlightthickness=1)
        listbox_border.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_border)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_projetos = tk.Listbox(
            listbox_border,
            font=("Consolas", 11),
            bg=self.cor_input_bg, fg=self.cor_texto,
            selectbackground=self.cor_destaque,
            selectforeground=self.cor_botao_txt,
            relief=tk.FLAT, bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            activestyle="none",
            selectmode=tk.EXTENDED
        )
        self.listbox_projetos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.listbox_projetos.yview)
        
        # Bind Ctrl+A para selecionar todos
        self.listbox_projetos.bind('<Control-a>', self._selecionar_todos)
        self.listbox_projetos.bind('<Control-A>', self._selecionar_todos)
        
        # Botões de seleção rápida + contador
        sel_frame = tk.Frame(projetos_frame, bg=self.cor_container)
        sel_frame.pack(fill=tk.X)
        
        self._criar_botao(
            sel_frame, text="✅ Selecionar Todos",
            font=("Segoe UI", 9, "bold"),
            bg=self.cor_sucesso, fg=self.cor_botao_txt,
            active_bg="#94e2d5", active_fg=self.cor_botao_txt,
            command=lambda: self._selecionar_todos(None),
            padx=12, pady=5
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self._criar_botao(
            sel_frame, text="⬜ Desmarcar Todos",
            font=("Segoe UI", 9),
            bg=self.cor_input_bg, fg=self.cor_texto,
            active_bg="#585b70", active_fg=self.cor_texto,
            command=self._desmarcar_todos,
            padx=12, pady=5
        ).pack(side=tk.LEFT)
        
        self.label_contador = tk.Label(
            sel_frame, textvariable=self.contador_texto,
            font=("Segoe UI", 9, "italic"),
            fg=self.cor_texto_sec, bg=self.cor_container, anchor="e"
        )
        self.label_contador.pack(side=tk.RIGHT)
        
        # --- FORMATO DE SAÍDA ---
        tk.Label(
            main_frame, text="Formato de Saída",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_fundo, fg=self.cor_texto, anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))
        
        formato_frame = tk.Frame(main_frame, bg=self.cor_container, padx=15, pady=12)
        formato_frame.pack(fill=tk.X, pady=(0, 20))
        
        opcoes_formato = [
            ("pdf",   "📄 PDF",      "Recomendado"),
            ("md",    "📝 Markdown", None),
            ("docx",  "📘 Word",     None),
            ("todos", "📦 Todos",    None),
        ]
        
        for valor, label, badge in opcoes_formato:
            rb_frame = tk.Frame(formato_frame, bg=self.cor_container)
            rb_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            rb = tk.Radiobutton(
                rb_frame, text=label, variable=self.formato_saida, value=valor,
                font=("Segoe UI", 10),
                bg=self.cor_container, fg=self.cor_texto,
                selectcolor=self.cor_input_bg,
                activebackground=self.cor_container,
                activeforeground=self.cor_destaque,
                indicatoron=True, cursor="hand2"
            )
            rb.pack(side=tk.LEFT)
            
            if badge:
                badge_label = tk.Label(
                    rb_frame, text=badge,
                    font=("Segoe UI", 7, "bold"),
                    bg=self.cor_sucesso, fg=self.cor_fundo,
                    padx=5, pady=1
                )
                badge_label.pack(side=tk.LEFT, padx=(4, 0))
        
        # --- ÁREA DE AÇÃO ---
        action_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        # pack movido para o final
        
        self.btn_gerar = self._criar_botao(
            action_frame, text="GERAR DOCUMENTAÇÃO",
            font=("Segoe UI", 12, "bold"),
            bg=self.cor_botao, fg=self.cor_botao_txt,
            active_bg="#b4befe", active_fg=self.cor_botao_txt,
            command=self._gerar_documentacao,
            width=25, pady=12
        )
        self.btn_gerar.pack(pady=(0, 15))
        self.btn_gerar.config(state=tk.DISABLED)
        
        # Progresso
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=8,
                        troughcolor=self.cor_container, background=self.cor_destaque)
        
        self.progress = ttk.Progressbar(
            action_frame, mode='indeterminate',
            style="TProgressbar", length=500
        )
        
        # Status
        self.label_status = tk.Label(
            action_frame, textvariable=self.status_texto,
            font=("Segoe UI", 10),
            fg=self.cor_texto_sec, bg=self.cor_fundo, wraplength=700
        )
        self.label_status.pack(pady=5)
        
        # Botão abrir pasta (escondido)
        self.btn_abrir = self._criar_botao(
            action_frame, text="📁 Abrir Pasta com Documentação",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_sucesso, fg=self.cor_botao_txt,
            active_bg="#94e2d5", active_fg=self.cor_botao_txt,
            command=lambda: None,
            padx=15, pady=8
        )
        
        # Rodapé
        tk.Label(
            main_frame, text="v2.1 | Suporte a múltiplas pastas e formatos",
            font=("Segoe UI", 8), fg="#585b70", bg=self.cor_fundo
        ).pack(side=tk.BOTTOM)
        
        # Ancorar o action_frame no fundo, logo acima do rodapé
        action_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # O projetos_frame agora preenche todo o espaço restante no meio,
        # sem empurrar os elementos inferiores para fora da janela
        projetos_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 20))
    
    # ========================================================================
    # SELEÇÃO E SCAN
    # ========================================================================
    
    def _selecionar_pasta_raiz(self):
        """Seleciona a pasta raiz e escaneia subpastas por projetos .pbip"""
        pasta = filedialog.askdirectory(
            title="Selecione a pasta que contém os projetos Power BI"
        )
        
        if not pasta:
            return
        
        pasta = os.path.normpath(pasta)
        
        # Atualiza o campo de texto
        self.entry_raiz.config(state="normal")
        self.caminho_raiz.set(pasta)
        self.entry_raiz.config(state="readonly")
        
        # Escaneia a pasta por projetos .pbip
        self._escanear_projetos(pasta)
    
    def _escanear_projetos(self, pasta_raiz: str):
        """Escaneia a pasta raiz e suas subpastas diretas por projetos Power BI"""
        self.projetos_encontrados.clear()
        self.listbox_projetos.delete(0, tk.END)
        
        raiz = Path(pasta_raiz)
        caminhos_adicionados = set()
        
        def _adicionar_projeto(caminho: Path, nome: str):
            """Adiciona projeto evitando duplicatas"""
            chave = str(caminho)
            if chave not in caminhos_adicionados:
                caminhos_adicionados.add(chave)
                self.projetos_encontrados.append({
                    "caminho": chave,
                    "nome": nome
                })
        
        def _detectar_projeto(pasta: Path) -> bool:
            """
            Detecta se uma pasta é um projeto Power BI.
            Retorna True se detectou (e já adicionou).
            
            Detecta 4 padrões:
              1. Pasta cujo nome termina em .pbip (a pasta É o projeto)
              2. Pasta que contém subpasta Model/ (layout novo)
              3. Pasta que contém subpasta *.SemanticModel (layout antigo)
              4. Pasta que contém arquivos *.pbip
            """
            # Padrão 1: O nome da pasta termina com .pbip
            if pasta.suffix.lower() == '.pbip':
                _adicionar_projeto(pasta, pasta.stem)
                return True
            
            # Padrão 2: Contém subpasta Model/ (layout novo)
            if (pasta / "Model").is_dir():
                # Busca nome no arquivo .pbip ou usa nome da pasta
                pbip_files = [p for p in pasta.glob("*.pbip") if p.is_file()]
                nome = pbip_files[0].stem if pbip_files else pasta.name
                _adicionar_projeto(pasta, nome)
                return True
            
            # Padrão 3: Contém subpasta *.SemanticModel (layout antigo)
            semantic_dirs = list(pasta.glob("*.SemanticModel"))
            if semantic_dirs:
                nome = semantic_dirs[0].stem
                _adicionar_projeto(pasta, nome)
                return True
            
            # Padrão 4: Contém arquivo(s) .pbip
            pbip_files = list(pasta.glob("*.pbip"))
            if pbip_files:
                pbip_reais = [f for f in pbip_files if f.is_file()]
                if pbip_reais:
                    _adicionar_projeto(pasta, pbip_reais[0].stem)
                    return True
            
            return False
        
        # Verifica se a própria pasta raiz é um projeto
        _detectar_projeto(raiz)
        
        # Escaneia subpastas diretas
        try:
            for subpasta in sorted(raiz.iterdir()):
                if subpasta.is_dir():
                    _detectar_projeto(subpasta)
        except PermissionError:
            pass
        
        # Preenche a Listbox
        for proj in self.projetos_encontrados:
            nome_pasta = Path(proj["caminho"]).name
            self.listbox_projetos.insert(tk.END, f"📊 {proj['nome']}   ({nome_pasta})")
        
        n = len(self.projetos_encontrados)
        
        if n == 0:
            self.contador_texto.set("Nenhum projeto .pbip encontrado")
            self.status_texto.set("⚠️ Nenhum projeto .pbip encontrado nesta pasta.")
            self.label_status.config(fg=self.cor_aviso)
            self.btn_gerar.config(state=tk.DISABLED)
        else:
            # Seleciona todos automaticamente
            self.listbox_projetos.select_set(0, tk.END)
            self.contador_texto.set(f"{n} projeto(s) encontrado(s)")
            self.status_texto.set(f"✅ {n} projeto(s) encontrado(s). Selecione quais documentar e clique em GERAR.")
            self.label_status.config(fg=self.cor_sucesso)
            self.btn_gerar.config(state=tk.NORMAL)
        
        # Esconde elementos anteriores
        self.btn_abrir.pack_forget()
        self.progress.pack_forget()
        self.progress.stop()
    
    def _selecionar_todos(self, event):
        """Seleciona todos os itens na listbox"""
        self.listbox_projetos.select_set(0, tk.END)
        return "break"  # Impede comportamento padrão do Ctrl+A
    
    def _desmarcar_todos(self):
        """Desmarca todos os itens na listbox"""
        self.listbox_projetos.selection_clear(0, tk.END)
    
    # ========================================================================
    # PROCESSAMENTO
    # ========================================================================
    
    def _gerar_documentacao(self):
        """Inicia o processo de geração"""
        selecionados = self.listbox_projetos.curselection()
        
        if not selecionados:
            self.status_texto.set("⚠️ Selecione pelo menos um projeto na lista.")
            self.label_status.config(fg=self.cor_aviso)
            return
        
        self.btn_gerar.config(state=tk.DISABLED, text="⏳ Processando...")
        
        # Mostra e inicia barra de progresso
        self.progress.pack(pady=(0, 8), before=self.label_status)
        self.progress.start(15)
        
        total = len(selecionados)
        self.status_texto.set(f"Iniciando processamento de {total} projeto(s)...")
        self.label_status.config(fg=self.cor_destaque)
        self.btn_abrir.pack_forget()
        
        # Coleta caminhos selecionados
        caminhos = [self.projetos_encontrados[i]["caminho"] for i in selecionados]
        
        # Thread
        thread = threading.Thread(target=self._processar_documentacao, args=(caminhos,))
        thread.daemon = True
        thread.start()
    
    def _processar_documentacao(self, caminhos: list):
        """Lógica de processamento em background"""
        total = len(caminhos)
        resultados_sucesso = []
        resultados_erro = []
        pastas_saida = set()
        
        # Pasta raiz selecionada pelo usuário — é onde os arquivos serão salvos
        pasta_raiz = self.caminho_raiz.get()
        formato = self.formato_saida.get()
        
        for i, caminho in enumerate(caminhos, 1):
            nome_pasta = Path(caminho).name
            
            def update_status(msg):
                self.root.after(0, lambda m=msg: (
                    self.status_texto.set(m),
                    self.label_status.config(fg=self.cor_destaque)
                ))

            update_status(f"[{nome_pasta}] Iniciando (1/4): Extraindo dados do Power BI...")
            
            try:
                doc = DocumentadorPBIP(caminho)
                doc.extrair_informacoes()
                
                # Gera apenas os formatos selecionados
                if formato in ('md', 'todos'):
                    update_status(f"[{nome_pasta}] Processando (2/4): Gerando Markdown...")
                    nome_arquivo_md = f"{doc.nome_projeto}_documentacao.md"
                    caminho_saida_md = str(Path(pasta_raiz) / nome_arquivo_md)
                    doc.salvar_documentacao(caminho_saida_md)
                
                if formato in ('docx', 'todos'):
                    update_status(f"[{nome_pasta}] Processando (3/4): Construindo Word (gerando imagem ER)...")
                    nome_arquivo_docx = f"{doc.nome_projeto}_documentacao.docx"
                    caminho_saida_docx = str(Path(pasta_raiz) / nome_arquivo_docx)
                    doc.salvar_documentacao_docx(caminho_saida_docx)
                
                if formato in ('pdf', 'todos'):
                    update_status(f"[{nome_pasta}] Processando (4/4): Exportando PDF via Playwright (pode demorar)...")
                    nome_arquivo_pdf = f"{doc.nome_projeto}_documentacao.pdf"
                    caminho_saida_pdf = str(Path(pasta_raiz) / nome_arquivo_pdf)
                    resultado_pdf = doc.salvar_documentacao_pdf(caminho_saida_pdf)
                    
                    if resultado_pdf is None:
                        raise Exception("O Playwright falhou. Feche o app, abra o terminal e digite: pip install playwright markdown && python -m playwright install chromium")
                
                resultados_sucesso.append(nome_pasta)
                pastas_saida.add(pasta_raiz)
                
            except PermissionError as e:
                resultados_erro.append((nome_pasta, "O arquivo já está aberto em outro programa (Word/PDF). Feche-o e tente novamente."))
            except Exception as e:
                import traceback
                traceback.print_exc()
                resultados_erro.append((nome_pasta, str(e)))
        
        self.root.after(0, lambda: self._finalizar(resultados_sucesso, resultados_erro, pastas_saida))
    
    def _finalizar(self, sucessos: list, erros: list, pastas_saida: set):
        """Atualiza a UI com o resultado final"""
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_gerar.config(state=tk.NORMAL, text="📄  Documentar Projetos Selecionados")
        
        total = len(sucessos) + len(erros)
        
        if erros and not sucessos:
            nomes_erro = ", ".join(nome for nome, _ in erros)
            self.status_texto.set(f"❌ Falha em todos os {total} projeto(s). Erros: {nomes_erro}")
            self.label_status.config(fg=self.cor_erro)
            messagebox.showerror("Erro na Geração", f"Falha ao gerar documentação para os projetos:\n{nomes_erro}")
        elif erros:
            nomes_erro = ", ".join(nome for nome, _ in erros)
            self.status_texto.set(
                f"⚠️ {len(sucessos)} de {total} processado(s) com sucesso. Falhas: {nomes_erro}"
            )
            self.label_status.config(fg=self.cor_aviso)
            self._mostrar_botao_abrir(pastas_saida)
            abrir = messagebox.askyesno("Aviso", f"{len(sucessos)} projetos documentados, mas houve falhas em:\n{nomes_erro}\n\nDeseja abrir a pasta da documentação agora?")
            if abrir and pastas_saida:
                self._abrir_pasta(list(pastas_saida)[0])
        else:
            self.status_texto.set(
                f"✅ Sucesso! {len(sucessos)} projeto(s) documentado(s)."
            )
            self.label_status.config(fg=self.cor_sucesso)
            self._mostrar_botao_abrir(pastas_saida)
            abrir = messagebox.askyesno("Sucesso", f"Documentação gerada com sucesso para {len(sucessos)} projeto(s)!\n\nDeseja abrir a pasta da documentação agora?")
            if abrir and pastas_saida:
                self._abrir_pasta(list(pastas_saida)[0])
    
    def _mostrar_botao_abrir(self, pastas_saida: set):
        """Mostra botão para abrir a pasta de saída"""
        if pastas_saida:
            primeira = list(pastas_saida)[0]
            texto = "📁  Abrir Pasta com Documentação"
            if len(pastas_saida) > 1:
                texto = f"📁  Abrir Pasta ({len(pastas_saida)} locais)"
            self.btn_abrir.config(text=texto, command=lambda: self._abrir_pasta(primeira))
            self.btn_abrir.pack(pady=(8, 0), before=self.label_status)
    
    def _abrir_pasta(self, caminho: str):
        """Abre a pasta no explorador de arquivos"""
        try:
            os.startfile(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")
    
    def executar(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DocumentadorGUI()
    app.executar()
