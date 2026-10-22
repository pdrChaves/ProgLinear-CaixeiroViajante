import tkinter as tk
from tkinter import filedialog, ttk


try:
    import customtkinter as ctk
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
except ImportError:
    ctk = None


class ReBikeApp:
    def __init__(self):
        self.root = ctk.CTk() if ctk else tk.Tk()
        self.root.title("Rebalanceamento de Bicicletas")
        self.root.geometry("960x640")
        self.root.minsize(700, 480)
        self.bg, self.blue, self.text, self.muted = "#F3F6FB", "#2563EB", "#172033", "#64748B"
        if ctk:
            self.root.configure(fg_color=self.bg)
        else:
            self.root.configure(bg=self.bg)
        self.container = None
        self.page = None

        self.tipo = tk.StringVar(value="Aleatória")
        self.tamanho = tk.StringVar(value="5")
        self.metodo = tk.StringVar(value="Subida de Encosta")
        self.tentativas = tk.StringVar(value="10")
        self.tini = tk.StringVar(value="100")
        self.tfim = tk.StringVar(value="1")
        self.fator = tk.StringVar(value="0.95")
        self.pop = tk.StringVar(value="30")
        self.ger = tk.StringVar(value="100")
        self.cruz = tk.StringVar(value="0.8")
        self.mut = tk.StringVar(value="0.05")
        self.intervalo = tk.StringVar(value="10")
        self.home()
        self.root.after(200, self.maximize)

    def maximize(self):
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

    def frame(self, parent, fg=None, radius=12):
        if ctk:
            return ctk.CTkFrame(parent, fg_color=fg or "white", corner_radius=radius)
        return ttk.Frame(parent)

    def label(self, parent, text, size=12, bold=False, color=None, **kwargs):
        if ctk:
            return ctk.CTkLabel(parent, text=text,
                font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
                text_color=color or self.text, **kwargs)
        return ttk.Label(parent, text=text, **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        if ctk:
            return ctk.CTkButton(parent, text=text, command=command, height=36,
                corner_radius=8, fg_color=self.blue if primary else "#E8EEF8",
                hover_color="#1D4ED8" if primary else "#D9E3F2",
                text_color="white" if primary else self.text, **kwargs)
        return ttk.Button(parent, text=text, command=command, **kwargs)

    def entry(self, parent, var, width=170):
        if ctk:
            return ctk.CTkEntry(parent, textvariable=var, width=width, height=34)
        return ttk.Entry(parent, textvariable=var, width=max(12, width // 9))

    def option(self, parent, var, values, width=220, command=None):
        if ctk:
            return ctk.CTkOptionMenu(parent, variable=var, values=values, width=width,
                                     height=34, command=command)
        w = ttk.Combobox(parent, textvariable=var, values=values,
                         width=max(15, width // 9), state="readonly")
        if command:
            w.bind("<<ComboboxSelected>>", lambda _e: command(var.get()))
        return w

    def textbox(self, parent, height=8):
        if ctk:
            return ctk.CTkTextbox(parent, height=height * 18, corner_radius=8)
        return tk.Text(parent, height=height, wrap="word", font=("Consolas", 10),
                       relief="solid", bd=1, bg="white", fg=self.text)

    def scroll_area(self, parent):
        if ctk:
            area = ctk.CTkScrollableFrame(parent, fg_color=self.bg, corner_radius=0)
            return area, area
        outer = tk.Frame(parent, bg=self.bg)
        canvas = tk.Canvas(outer, bg=self.bg, highlightthickness=0)
        bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.bg)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.configure(yscrollcommand=bar.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        return outer, inner

    def clear(self, back=True):
        if self.container:
            self.container.destroy()
        self.container = self.frame(self.root, self.bg, radius=0)
        self.container.pack(fill="both", expand=True)
        if back:
            bar = self.frame(self.container, self.bg, radius=0)
            bar.pack(fill="x", padx=28, pady=(12, 0))
            self.button(bar, "← Voltar à tela principal", self.home, width=190).pack(anchor="w")
        holder, self.page = self.scroll_area(self.container)
        holder.pack(fill="both", expand=True)

    def header(self, title, subtitle):
        top = self.frame(self.page, self.bg)
        top.pack(fill="x", padx=28, pady=(14, 10))
        self.label(top, "SISTEMA DE OTIMIZAÇÃO", 10, True, self.blue).pack(anchor="w")
        self.label(top, title, 26, True).pack(anchor="w", pady=(6, 2))
        self.label(top, subtitle, 12, color=self.muted).pack(anchor="w")

    def card(self, title, subtitle=None):
        card = self.frame(self.page)
        card.pack(fill="x", padx=28, pady=7)
        inside = self.frame(card)
        inside.pack(fill="both", expand=True, padx=17, pady=14)
        self.label(inside, title, 15, True).pack(anchor="w")
        if subtitle:
            self.label(inside, subtitle, 11, color=self.muted).pack(anchor="w", pady=(3, 10))
        return inside

    def footer(self):
        self.button(self.page, "← Voltar à tela principal", self.home, width=190).pack(
            anchor="w", padx=28, pady=15)

    def gerar_relatorio_pdf(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
            initialfile="relatorio_busca_local.pdf")
        if not caminho:
            return
        cols = [50, 140, 410, 545]
        topo, alt = 780, 24
        ops = ["0.5 w"]
        for y in (topo, topo - alt):
            ops.append(f"{cols[0]} {y} m {cols[-1]} {y} l S")
        for x in cols:
            ops.append(f"{x} {topo} m {x} {topo - alt} l S")
        for x, t in zip(cols, ("Método", "Configuração", "Ganho")):
            ops.append(f"BT /F1 11 Tf {x + 6} {topo - 16} Td ({t}) Tj ET")
        dados = "\n".join(ops).encode("cp1252", "replace")
        objs = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
            b"<< /Length " + str(len(dados)).encode() + b" >>\nstream\n" + dados + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        ]
        saida = bytearray(b"%PDF-1.4\n")
        posicoes = []
        for k, obj in enumerate(objs, 1):
            posicoes.append(len(saida))
            saida += f"{k} 0 obj\n".encode() + obj + b"\nendobj\n"
        inicio = len(saida)
        saida += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
        for p in posicoes:
            saida += f"{p:010d} 00000 n \n".encode()
        saida += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
                  f"startxref\n{inicio}\n%%EOF").encode()
        with open(caminho, "wb") as arquivo:
            arquivo.write(saida)

    def home(self):
        self.clear(back=False)
        self.header("Rebalanceamento de bicicletas",
                    "Trabalho de Programação Linear e Aplicações")
        intro = self.card("OBJETIVO DO PROJETO")
        self.label(intro,
            "Planejar uma rota para coletar bicicletas de estações com excesso e entregá-las "
            "às estações com falta, considerando os custos de deslocamento.",
            14, wraplength=720, justify="left").pack(anchor="w", pady=(10, 3))
        self.label(self.page, "ÁREAS DO SISTEMA", 12, True).pack(anchor="w", padx=30, pady=(15, 4))
        for num, title, desc, action in [
            ("01", "Configurações", "Tipo de execução e problema", self.config),
            ("02", "Busca Local", "Métodos e parâmetros de busca", self.local),
            ("03", "Algoritmos Genéticos", "Parâmetros do AG — segunda avaliação", self.genetico),
        ]:
            row = self.frame(self.page)
            row.pack(fill="x", padx=28, pady=5)
            self.label(row, num, 17, True, self.blue, width=38).pack(side="left", padx=14, pady=12)
            details = self.frame(row)
            details.pack(side="left", fill="x", expand=True, pady=9)
            self.label(details, title, 14, True).pack(anchor="w")
            self.label(details, desc, 11, color=self.muted).pack(anchor="w")
            self.button(row, "Abrir  →", action, primary=(num == "01"), width=110).pack(side="right", padx=14)

    def config(self):
        self.clear()
        self.header("Configurações", "Defina as opções que serão exibidas no problema.")
        box = self.card("Geração do problema", "Escolha o tipo de execução e o tamanho.")
        row = self.frame(box)
        row.pack(fill="x", pady=5)
        self.label(row, "Tipo de execução", 12).grid(row=0, column=0, sticky="w", padx=(0, 20), pady=8)
        self.option(row, self.tipo, ["Fixa", "Aleatória"], 190, self.update_size).grid(row=0, column=1, sticky="w")
        self.label(row, "Tamanho do problema", 12).grid(row=1, column=0, sticky="w", padx=(0, 20), pady=8)
        self.size_widget = self.option(row, self.tamanho, ["3", "4", "5", "6", "8", "10"], 190)
        self.size_widget.grid(row=1, column=1, sticky="w")
        self.update_size(self.tipo.get())
        self.button(box, "＋  Gerar problema", self.preview_problem, True).pack(anchor="w", pady=(12, 5))
        result = self.card("Área de exibição")
        self.problem_area = self.textbox(result, 8)
        self.problem_area.pack(fill="both", expand=True, pady=(7, 0))
        self.footer()

    def update_size(self, choice):
        if hasattr(self, "size_widget"):
            self.size_widget.configure(state="disabled" if choice == "Fixa" else "normal")

    def preview_problem(self):
        self.problem_area.delete("1.0", "end")
        self.problem_area.insert("end",
            f"Tipo de execução: {self.tipo.get()}\n"
            f"Tamanho do problema: {self.tamanho.get()}")

    def local(self):
        self.clear()
        self.header("Busca Local", "Selecione um método e visualize a área de resultados.")
        box = self.card("Parâmetros de execução", "Os campos são habilitados conforme o método escolhido.")
        row = self.frame(box)
        row.pack(fill="x")
        self.label(row, "Método", 12).grid(row=0, column=0, sticky="w", padx=(0, 20), pady=7)
        self.option(row, self.metodo,
            ["Subida de Encosta", "Subida de Encosta com Tentativas", "Têmpera Simulada"],
            310, self.update_params).grid(row=0, column=1, sticky="w")
        self.lbl_attempt = self.label(row, "Total de tentativas", 12)
        self.lbl_attempt.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=7)
        self.ent_attempt = self.entry(row, self.tentativas)
        self.ent_attempt.grid(row=1, column=1, sticky="w")
        self.lbl_tini = self.label(row, "Temperatura inicial", 12)
        self.lbl_tini.grid(row=2, column=0, sticky="w", padx=(0, 20), pady=7)
        self.ent_tini = self.entry(row, self.tini)
        self.ent_tini.grid(row=2, column=1, sticky="w")
        self.lbl_tfim = self.label(row, "Temperatura final", 12)
        self.lbl_tfim.grid(row=3, column=0, sticky="w", padx=(0, 20), pady=7)
        self.ent_tfim = self.entry(row, self.tfim)
        self.ent_tfim.grid(row=3, column=1, sticky="w")
        self.lbl_factor = self.label(row, "Fator redutor", 12)
        self.lbl_factor.grid(row=4, column=0, sticky="w", padx=(0, 20), pady=7)
        self.ent_factor = self.entry(row, self.fator)
        self.ent_factor.grid(row=4, column=1, sticky="w")
        self.button(box, "▶  Executar", self.gerar_relatorio_pdf, True).pack(anchor="w", pady=(12, 3))
        self.update_params(self.metodo.get())
        results = self.card("Resultados")
        self.local_area = self.textbox(results, 8)
        self.local_area.pack(fill="both", expand=True, pady=(7, 0))
        self.footer()

    def update_params(self, method):
        if not hasattr(self, "ent_attempt"):
            return
        self.ent_attempt.configure(state="normal" if method == "Subida de Encosta com Tentativas" else "disabled")
        state = "normal" if method == "Têmpera Simulada" else "disabled"
        for w in (self.ent_tini, self.ent_tfim, self.ent_factor):
            w.configure(state=state)

    def genetico(self):
        self.clear()
        self.header("Algoritmos Genéticos", "Parâmetros previstos para a segunda avaliação.")
        box = self.card("Parâmetros do algoritmo")
        row = self.frame(box)
        row.pack(fill="x")
        for i, (name, var) in enumerate([
            ("Tamanho da população", self.pop),
            ("Número de gerações", self.ger),
            ("Taxa de cruzamento", self.cruz),
            ("Taxa de mutação", self.mut),
            ("Intervalo de geração", self.intervalo),
        ]):
            self.label(row, name, 12).grid(row=i, column=0, sticky="w", padx=(0, 25), pady=7)
            self.entry(row, var, 180).grid(row=i, column=1, sticky="w", pady=7)
        actions = self.frame(box)
        actions.pack(fill="x", pady=(12, 2))
        self.button(actions, "▶  Executar AG", self.preview_ag, True).pack(side="left", padx=(0, 9))
        self.button(actions, "Análise comparativa", self.preview_ag).pack(side="left")
        result = self.card("Resultados")
        self.ag_area = self.textbox(result, 8)
        self.ag_area.pack(fill="both", expand=True, pady=(7, 0))
        self.footer()

    def preview_ag(self):
        self.ag_area.delete("1.0", "end")
        self.ag_area.insert("end",
            "Parâmetros informados:\n"
            f"• População: {self.pop.get()}\n"
            f"• Gerações: {self.ger.get()}\n"
            f"• Cruzamento: {self.cruz.get()}\n"
            f"• Mutação: {self.mut.get()}\n"
            f"• Intervalo: {self.intervalo.get()}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ReBikeApp().run()