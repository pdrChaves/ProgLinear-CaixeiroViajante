# interface - rebalanceamento de bicicletas
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import backend

FUNDO = "#2b2b2b"
LETRA = "#dddddd"


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rebalanceamento de Bicicletas")
        self.root.geometry("900x640")
        self.root.configure(bg=FUNDO)

        # configuracoes
        self.tipo = tk.StringVar(value="FIXO")
        self.tamanho = tk.StringVar(value="6")
        self.Q = tk.StringVar()
        self.L0 = tk.StringVar()
        self.dep_x = tk.StringVar()
        self.dep_y = tk.StringVar()
        self.alfa = tk.StringVar(value="1")
        self.beta = tk.StringVar(value="1")
        self.estacoes = []
        self.P = None

        # metodos
        self.metodo = tk.StringVar(value="Subida de Encosta")
        self.tmax = tk.StringVar(value="10")
        self.Tini = tk.StringVar(value="100")
        self.Tfim = tk.StringVar(value="0.01")
        self.fator = tk.StringVar(value="0.99")

        self.CarregarDados(backend.DadosFixos())
        self.tela = None
        self.Principal()

    def Label(self, pai, txt, **kw):
        return tk.Label(pai, text=txt, bg=FUNDO, fg=LETRA, **kw)

    def Grupo(self, pai, titulo):
        g = tk.LabelFrame(pai, text=titulo, bg=FUNDO, fg=LETRA, padx=8, pady=6)
        g.pack(fill="x", padx=8, pady=4)
        return g

    def Entrada(self, pai, var, largura=8):
        return tk.Entry(pai, textvariable=var, width=largura)

    def Combo(self, pai, var, valores, largura=12, comando=None):
        c = ttk.Combobox(pai, textvariable=var, values=valores, width=largura, state="readonly")
        if comando:
            c.bind("<<ComboboxSelected>>", lambda e: comando(var.get()))
        return c

    def AreaExibicao(self, pai, linhas=18):
        f = tk.Frame(pai, bg=FUNDO)
        f.pack(fill="both", expand=True)
        txt = tk.Text(f, height=linhas, bg="#1e1e1e", fg="white", insertbackground="white",
                      font=("Consolas", 10), wrap="none")
        barra = tk.Scrollbar(f, command=txt.yview)
        txt.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        return txt

    def NovaTela(self, voltar=True):
        if self.tela:
            self.tela.destroy()
        self.tela = tk.Frame(self.root, bg=FUNDO)
        self.tela.pack(fill="both", expand=True)
        if voltar:
            tk.Button(self.tela, text="Voltar", command=self.Principal).pack(anchor="w", padx=8, pady=6)

        # rolagem
        canvas = tk.Canvas(self.tela, bg=FUNDO, highlightthickness=0)
        barra = tk.Scrollbar(self.tela, orient="vertical", command=canvas.yview)
        corpo = tk.Frame(canvas, bg=FUNDO)
        janela = canvas.create_window((0, 0), window=corpo, anchor="nw")
        corpo.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(janela, width=e.width))
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def rolar(e):
            try:
                canvas.yview_scroll(int(-e.delta / 120), "units")
            except tk.TclError:
                pass
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", rolar))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        return corpo

    # tela principal
    def Principal(self):
        self.root.title("Rebalanceamento de Bicicletas")
        corpo = self.NovaTela(voltar=False)
        tk.Button(corpo, text="Sobre", width=20, command=self.Sobre).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Button(corpo, text="Configurações", width=20, command=self.Configuracoes).pack(anchor="w", padx=12, pady=4)
        tk.Button(corpo, text="Métodos Básicos", width=20, command=self.MetodosBasicos).pack(anchor="w", padx=12, pady=4)
        tk.Button(corpo, text="Algoritmos Genéticos", width=20,
                  command=lambda: messagebox.showinfo("Algoritmos Genéticos", "Módulo em Desenvolvimento")).pack(anchor="w", padx=12, pady=4)
        if self.P:
            situacao = f"Problema gerado: {len(self.P['pontos']) - 1} estações ({self.tipo.get()})"
        else:
            situacao = "Nenhum problema gerado ainda"
        self.Label(corpo, situacao).pack(anchor="w", padx=12, pady=10)

    def Sobre(self):
        self.root.title("Sobre o Sistema")
        corpo = self.NovaTela()
        texto = (
            "Rebalanceamento de bicicletas compartilhadas em pontos de coleta\n\n"
            "Disciplina: Programação Linear e Aplicações\n"
            "Curso: Análise e Desenvolvimento de Sistemas - Fatec Cruzeiro\n"
            "Docente: Luis Fernando\n"
            "Alunos: Bruno Kenji, Fabiano José, Murilo Fernando e Pedro Chaves\n\n"
            "Problema: em um sistema de bicicletas compartilhadas algumas estações ficam com\n"
            "bicicletas sobrando e outras ficam vazias. Um caminhão sai do depósito, coleta onde\n"
            "sobra, entrega onde falta, passa no máximo uma vez em cada estação e volta ao\n"
            "depósito. É uma variação do caixeiro viajante (coleta e entrega).\n\n"
            "Função objetivo:\n"
            "min f = alfa * distância percorrida + beta * desequilíbrio residual\n"
            "desequilíbrio residual = bicicletas que ficaram fora da meta depois da rota\n\n"
            "Métodos:\n"
            "Solução = ordem de visita das estações.\n"
            "Subida de Encosta: escolhe uma posição e troca com cada uma das outras (N-1 vizinhos);\n"
            "vai para o melhor vizinho e para quando nenhum é melhor que a solução atual.\n"
            "Subida de Encosta com Tentativas: igual, mas só para depois de TMAX tentativas\n"
            "seguidas sem melhora (cada tentativa usa outra posição).\n"
            "Têmpera Simulada: aceita piora com uma chance que diminui com a temperatura."
        )
        self.Label(corpo, texto, justify="left").pack(anchor="w", padx=12, pady=8)

    def Configuracoes(self):
        self.root.title("Configuração do Problema")
        corpo = self.NovaTela()

        g = self.Grupo(corpo, "Problema")
        self.Label(g, "Tipo de execução").grid(row=0, column=0, sticky="w")
        self.Combo(g, self.tipo, ["FIXO", "ALEATÓRIO"], 11, self.MudouTipo).grid(row=0, column=1, padx=(4, 16))
        self.Label(g, "Tamanho do problema").grid(row=0, column=2, sticky="w")
        self.campo_tamanho = self.Entrada(g, self.tamanho, 5)
        self.campo_tamanho.grid(row=0, column=3, padx=(4, 16))
        tk.Button(g, text="Gerar problema", command=self.GerarProblema).grid(row=0, column=4)
        self.MudouTipo(self.tipo.get(), recarregar=False)

        g = self.Grupo(corpo, "Caminhão")
        campos = [("Capacidade (Q)", self.Q), ("Bikes ao sair (L0)", self.L0),
                  ("Depósito X", self.dep_x), ("Depósito Y", self.dep_y),
                  ("Peso alfa (distância)", self.alfa), ("Peso beta (desequilíbrio)", self.beta)]
        for k, (nome, var) in enumerate(campos):
            self.Label(g, nome).grid(row=k // 2, column=(k % 2) * 2, sticky="w", pady=2)
            self.Entrada(g, var).grid(row=k // 2, column=(k % 2) * 2 + 1, sticky="w", padx=(4, 20), pady=2)

        g = self.Grupo(corpo, "Estações")
        tk.Button(g, text="+ estação", command=self.NovaEstacao).pack(anchor="w", pady=(0, 4))
        self.grade = tk.Frame(g, bg=FUNDO)
        self.grade.pack(fill="x")
        self.DesenharEstacoes()

        g = self.Grupo(corpo, "Problema gerado")
        self.area_problema = self.AreaExibicao(g, 18)
        if self.P:
            self.area_problema.insert("end", self.TextoProblema())

    def MudouTipo(self, valor, recarregar=True):
        if valor == "FIXO":
            self.campo_tamanho.configure(state="disabled")
            if recarregar:
                self.CarregarDados(backend.DadosFixos())
                self.DesenharEstacoes()
        else:
            self.campo_tamanho.configure(state="normal")

    def CarregarDados(self, dados):
        self.Q.set(str(dados["Q"]))
        self.L0.set(str(dados["L0"]))
        self.dep_x.set(str(dados["deposito"][0]))
        self.dep_y.set(str(dados["deposito"][1]))
        self.estacoes = [[tk.StringVar(value=str(v)) for v in e] for e in dados["estacoes"]]

    def DesenharEstacoes(self):
        for w in self.grade.winfo_children():
            w.destroy()
        self.estacoes = [[tk.StringVar(value=v.get()) for v in e] for e in self.estacoes]
        for i, e in enumerate(self.estacoes):
            self.Quadrado(i, e).grid(row=i // 4, column=i % 4, sticky="nw", padx=3, pady=3)

    def Quadrado(self, i, e):
        x, y, tem, meta, cap = e
        q = tk.LabelFrame(self.grade, text=f"Estação {i + 1}", bg=FUNDO, fg=LETRA, padx=5, pady=3)
        situacao = self.Label(q, "")
        situacao.grid(row=0, column=0, columnspan=4, sticky="w")
        for lin, col, nome, var in [(1, 0, "X", x), (1, 1, "Y", y), (2, 0, "Tem", tem),
                                    (2, 1, "Meta", meta), (3, 0, "Cap", cap)]:
            self.Label(q, nome).grid(row=lin, column=col * 2, sticky="w")
            self.Entrada(q, var, 5).grid(row=lin, column=col * 2 + 1, sticky="w", padx=(2, 6), pady=1)
        tk.Button(q, text="remover", command=lambda: self.RemoverEstacao(i)).grid(row=3, column=2, columnspan=2, sticky="e")

        def atualizar(*_):
            try:
                d = int(meta.get()) - int(tem.get())
            except ValueError:
                situacao.configure(text="tem ? / meta ?")
                return
            if d > 0:
                obs = f"entregar {d}"
            elif d < 0:
                obs = f"coletar {-d}"
            else:
                obs = "ok"
            situacao.configure(text=f"tem {tem.get()} / meta {meta.get()} ({obs})")

        tem.trace_add("write", atualizar)
        meta.trace_add("write", atualizar)
        atualizar()
        return q

    def NovaEstacao(self):
        self.estacoes.append([tk.StringVar(value=v) for v in ("0", "0", "0", "0", "10")])
        self.DesenharEstacoes()

    def RemoverEstacao(self, i):
        if len(self.estacoes) > 1:
            self.estacoes.pop(i)
            self.DesenharEstacoes()


    def LerDados(self):
        erros = []

        def numero(txt, nome, inteiro=True):
            try:
                v = float(txt.replace(",", "."))
                if inteiro and v != int(v):
                    raise ValueError
                return int(v) if inteiro else v
            except ValueError:
                erros.append(f"{nome}: '{txt}' não é um número válido")
                return 0

        Q = numero(self.Q.get(), "Capacidade do caminhão")
        L0 = numero(self.L0.get(), "Bikes ao sair")
        dep = [numero(self.dep_x.get(), "Depósito X", False), numero(self.dep_y.get(), "Depósito Y", False)]
        alfa = numero(self.alfa.get(), "Peso α", False)
        beta = numero(self.beta.get(), "Peso β", False)
        if Q < 1:
            erros.append("A capacidade do caminhão tem que ser pelo menos 1")
        if L0 < 0 or L0 > Q:
            erros.append("Bikes ao sair tem que estar entre 0 e a capacidade do caminhão")
        if alfa < 0 or beta < 0 or (alfa == 0 and beta == 0):
            erros.append("Os pesos não podem ser negativos nem os dois iguais a 0")

        estacoes = []
        for i, e in enumerate(self.estacoes, 1):
            x = numero(e[0].get(), f"Estação {i}, X", False)
            y = numero(e[1].get(), f"Estação {i}, Y", False)
            tem = numero(e[2].get(), f"Estação {i}, tem")
            meta = numero(e[3].get(), f"Estação {i}, meta")
            cap = numero(e[4].get(), f"Estação {i}, capacidade")
            if tem < 0 or meta < 0 or tem > cap or meta > cap:
                erros.append(f"Estação {i}: tem e meta precisam ficar entre 0 e a capacidade ({cap})")
            estacoes.append([x, y, tem, meta, cap])

        dados = {"deposito": dep, "Q": Q, "L0": L0, "estacoes": estacoes}
        return dados, alfa, beta, erros

    def GerarProblema(self):
        if self.tipo.get() == "ALEATÓRIO":
            try:
                n = int(self.tamanho.get())
            except ValueError:
                n = 0
            if n < 2 or n > 30:
                self.area_problema.delete("1.0", "end")
                self.area_problema.insert("end", "Tamanho do problema tem que ser um número inteiro de 2 a 30.")
                return
            self.CarregarDados(backend.DadosAleatorios(n))
            self.DesenharEstacoes()

        dados, alfa, beta, erros = self.LerDados()
        self.area_problema.delete("1.0", "end")
        if erros:
            self.P = None
            self.area_problema.insert("end", "Corrija os dados:\n\n" + "\n".join(erros))
            return
        self.P = backend.GerarProblema(dados, alfa, beta)
        self.area_problema.insert("end", self.TextoProblema())

    def TextoProblema(self):
        P = self.P
        n = len(P["pontos"])
        nomes = ["Dep"] + [f"E{i}" for i in range(1, n)]
        txt = f"Problema {self.tipo.get().lower()}: depósito + {n - 1} estações\n\n"

        txt += "Matriz C - distância entre os pontos (km)\n"
        txt += "       " + "".join(f"{nm:>6}" for nm in nomes) + "\n"
        for i in range(n):
            txt += f"{nomes[i]:>6} " + "".join(f"{P['C'][i][j]:>6}" for j in range(n)) + "\n"

        txt += "\nVetores das estações\n"
        txt += f"{'':>8}{'X,Y':>8}{'Tem (s)':>9}{'Meta (t)':>10}{'Capac.':>8}   Demanda d = t - s\n"
        for i in range(1, n):
            d = P["d"][i]
            if d > 0:
                acao = f"+{d}  entregar"
            elif d < 0:
                acao = f"{d}  coletar"
            else:
                acao = "0  já está na meta"
            xy = f"{P['pontos'][i][0]:g},{P['pontos'][i][1]:g}"
            txt += f"{nomes[i]:>8}{xy:>8}{P['s'][i]:>9}{P['t'][i]:>10}{P['cap'][i]:>8}   {acao}\n"

        dx, dy = P["pontos"][0]
        txt += f"\nCaminhão: capacidade Q = {P['Q']}, sai do depósito ({dx:g}, {dy:g}) com L0 = {P['L0']}\n"
        txt += f"f = {P['alfa']:g} x distância + {P['beta']:g} x desequilíbrio residual\n"
        txt += f"Estações que precisam de ajuste: {len(P['estacoes'])}"
        return txt

    def MetodosBasicos(self):
        self.root.title("Métodos Básicos")
        corpo = self.NovaTela()
        if not self.P:
            self.Label(corpo, "Gere o problema em Configurações primeiro.").pack(anchor="w", padx=12, pady=10)
            return

        g = self.Grupo(corpo, "Parâmetros")
        self.Label(g, "Método").grid(row=0, column=0, sticky="w", pady=2)
        self.Combo(g, self.metodo, backend.METODOS, 32, self.MudouMetodo).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        self.campo_tmax = self.Entrada(g, self.tmax)
        self.campos_temp = [self.Entrada(g, self.Tini), self.Entrada(g, self.Tfim), self.Entrada(g, self.fator)]
        nomes = ["TMAX", "Temperatura inicial", "Temperatura final", "Fator redutor"]
        for k, (nome, campo) in enumerate(zip(nomes, [self.campo_tmax] + self.campos_temp), 1):
            self.Label(g, nome).grid(row=k, column=0, sticky="w", pady=2)
            campo.grid(row=k, column=1, sticky="w", padx=4, pady=2)
        self.MudouMetodo(self.metodo.get())

        b = tk.Frame(g, bg=FUNDO)
        b.grid(row=5, column=0, columnspan=4, sticky="w", pady=(6, 0))
        tk.Button(b, text="Executar", width=12, command=self.ExecutarMetodo).pack(side="left", padx=(0, 6))
        tk.Button(b, text="Análise Comparativa", width=18, command=self.AnaliseComparativa).pack(side="left")

        g = self.Grupo(corpo, "Resultados")
        self.area_busca = self.AreaExibicao(g, 22)

    def MudouMetodo(self, metodo):
        self.campo_tmax.configure(state="normal" if metodo == "Subida de Encosta com Tentativas" else "disabled")
        for c in self.campos_temp:
            c.configure(state="normal" if metodo == "Têmpera Simulada" else "disabled")

    def LerParametros(self):
        try:
            tmax = int(self.tmax.get())
            Tini = float(self.Tini.get().replace(",", "."))
            Tfim = float(self.Tfim.get().replace(",", "."))
            fator = float(self.fator.get().replace(",", "."))
        except ValueError:
            return None, "Algum parâmetro não é um número."
        if not (0 < fator < 1) or Tfim <= 0 or Tini <= Tfim:
            return None, "Use fator redutor entre 0 e 1 e temperatura inicial maior que a final (> 0)."
        if tmax < 1:
            return None, "TMAX tem que ser pelo menos 1."
        return (tmax, Tini, Tfim, fator), None

    def Mostrar(self, txt):
        self.area_busca.delete("1.0", "end")
        self.area_busca.insert("end", txt)

    def ExecutarMetodo(self):
        par, erro = self.LerParametros()
        if erro:
            self.Mostrar(erro)
            return
        if not self.P["estacoes"]:
            self.Mostrar("Nenhuma estação precisa de ajuste.")
            return
        tmax, Tini, Tfim, fator = par
        metodo = self.metodo.get()

        sol0 = backend.SolInicial(self.P)
        f0 = backend.Avalia(sol0, self.P)
        log = []
        inicio = time.perf_counter()
        sol, f = backend.Executar(self.P, metodo, sol0[:], tmax, Tini, Tfim, fator, log)
        tempo = (time.perf_counter() - inicio) * 1000
        _, dist, sobra, passos = backend.Simular(sol, self.P)

        txt = f"{metodo}\n"
        txt += f"Solução inicial: {sol0}   f = {f0:g}\n\n"
        txt += "Iterações:\n" + ("\n".join(log) if log else "(nenhum vizinho melhorou a solução inicial)")
        txt += "\n\nResultado\n"
        txt += "Rota: " + " -> ".join(map(str, [0] + sol + [0])) + "\n"
        txt += f"Distância: {dist:g} km   Desequilíbrio residual: {sobra}\n"
        txt += f"f = {self.P['alfa']:g} x {dist:g} + {self.P['beta']:g} x {sobra} = {f:g}\n"
        txt += f"Ganho: {f0 - f:g} ({100 * (f0 - f) / f0 if f0 else 0:.1f}%)   Tempo: {tempo:.1f} ms\n\n"
        txt += "\n".join(passos)
        self.Mostrar(txt)

    def AnaliseComparativa(self):
        par, erro = self.LerParametros()
        if erro:
            self.Mostrar(erro)
            return
        if not self.P["estacoes"]:
            self.Mostrar("Nenhuma estação precisa de ajuste.")
            return
        tmax, Tini, Tfim, fator = par
        execucoes = 10
        res = backend.Analise(self.P, tmax, Tini, Tfim, fator, execucoes)

        txt = f"Análise comparativa ({execucoes} execuções por método, mesma solução inicial para os três)\n\n"
        txt += f"{'Método':<34}{'f médio':>9}{'Melhor f':>10}{'Ganho %':>9}{'Tempo ms':>10}\n"
        for r in res:
            txt += f"{r['metodo']:<34}{r['f_medio']:>9.1f}{r['f_melhor']:>10g}{r['ganho']:>9.1f}{r['tempo']:>10.1f}\n"
        txt += "\nMelhor rota de cada método:\n"
        for r in res:
            txt += f"{r['metodo']}: {' -> '.join(map(str, r['rota']))}\n"

        caminho = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
                                               initialfile="relatorio_busca_local.pdf")
        if caminho:
            backend.RelatorioPDF(caminho, self.P, res, execucoes)
            txt += f"\nRelatório salvo em: {caminho}"
        else:
            txt += "\nRelatório PDF não foi salvo."
        self.Mostrar(txt)

    def Rodar(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().Rodar()