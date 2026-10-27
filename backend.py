# Back-end do trabalho de Rebalanceamento de Bicicletas
# Funcoes principais (iguais aos slides): GerarProblema, SolInicial, Avalia, Sucessores
import math
import random
import time


# ---------------- dados ----------------

def DadosFixos():
    # estacoes fixas da cidade (TROCAR pelos dados reais)
    # cada estacao: x, y, tem agora, meta, capacidade
    estacoes = [
        [2, 8, 2, 7, 10],
        [8, 9, 12, 6, 14],
        [9, 4, 1, 5, 8],
        [7, 1, 9, 4, 10],
        [3, 2, 3, 8, 12],
        [1, 5, 11, 5, 12],
        [5, 9, 0, 4, 8],
        [9, 7, 10, 6, 12],
        [4, 4, 4, 7, 10],
    ]
    return {"deposito": [5, 5], "Q": 10, "L0": 4, "estacoes": estacoes}


def DadosAleatorios(N):
    estacoes = []
    for _ in range(N):
        cap = random.randint(8, 15)
        tem = random.randint(0, cap)
        meta = random.randint(0, cap)
        while meta == tem:
            meta = random.randint(0, cap)
        estacoes.append([random.randint(0, 10), random.randint(0, 10), tem, meta, cap])
    return {"deposito": [5, 5], "Q": 10, "L0": 5, "estacoes": estacoes}


def GerarProblema(dados, alfa, beta):
    pontos = [dados["deposito"]] + [[e[0], e[1]] for e in dados["estacoes"]]
    n = len(pontos)

    # matriz C: distancia em linha reta entre todos os pontos (0 = deposito)
    C = []
    for i in range(n):
        linha = []
        for j in range(n):
            linha.append(round(math.dist(pontos[i], pontos[j]), 1))
        C.append(linha)

    s = [0] + [e[2] for e in dados["estacoes"]]    # estoque atual
    t = [0] + [e[3] for e in dados["estacoes"]]    # alvo (meta)
    cap = [0] + [e[4] for e in dados["estacoes"]]  # capacidade
    d = [t[i] - s[i] for i in range(n)]            # demanda: + entregar, - coletar

    return {
        "C": C, "pontos": pontos, "s": s, "t": t, "cap": cap, "d": d,
        "Q": dados["Q"], "L0": dados["L0"], "alfa": alfa, "beta": beta,
        "estacoes": [i for i in range(1, n) if d[i] != 0],  # so as que precisam de ajuste
    }


# ---------------- funcoes dos slides ----------------

def SolInicial(P, modo="Aleatória"):
    sol = list(P["estacoes"])
    if modo == "Aleatória":
        random.shuffle(sol)
        return sol

    # gulosa: vai na estacao mais proxima onde o caminhao consegue operar
    rota = []
    atual = 0
    carga = P["L0"]
    while sol:
        pode = [i for i in sol if (P["d"][i] > 0 and carga > 0) or (P["d"][i] < 0 and carga < P["Q"])]
        if not pode:
            pode = sol
        prox = min(pode, key=lambda i: P["C"][atual][i])
        carga, _ = Operar(P, prox, carga)
        rota.append(prox)
        sol.remove(prox)
        atual = prox
    return rota


def Operar(P, i, carga):
    # entrega ou coleta na estacao i, devolve (nova carga, quantidade movida)
    if P["d"][i] > 0:
        q = min(P["d"][i], carga)
        return carga - q, q
    q = min(-P["d"][i], P["Q"] - carga)
    return carga + q, q


def Simular(sol, P):
    rota = [0] + sol + [0]
    dist = 0
    for k in range(len(rota) - 1):
        dist += P["C"][rota[k]][rota[k + 1]]

    carga = P["L0"]
    sobra = 0
    passos = []
    for i in sol:
        carga, q = Operar(P, i, carga)
        sobra += abs(P["d"][i]) - q
        acao = "entrega" if P["d"][i] > 0 else "coleta"
        passos.append(f"E{i}: precisava {abs(P['d'][i])}, {acao} {q}, caminhao fica com {carga}")

    f = P["alfa"] * dist + P["beta"] * sobra
    return round(f, 2), round(dist, 1), sobra, passos


def Avalia(sol, P):
    # min f = alfa * distancia + beta * desequilibrio residual
    return Simular(sol, P)[0]


def Sucessores(sol, P):
    # vizinho = trocar duas estacoes de lugar; devolve o melhor e a nota dele
    melhor = None
    f_melhor = math.inf
    for i in range(len(sol) - 1):
        for j in range(i + 1, len(sol)):
            viz = sol[:]
            viz[i], viz[j] = viz[j], viz[i]
            f = Avalia(viz, P)
            if f < f_melhor:
                melhor, f_melhor = viz, f
    return melhor, f_melhor


# ---------------- metodos ----------------

def SubidaEncosta(P, sol, log=None):
    f = Avalia(sol, P)
    it = 0
    while True:
        viz, f_viz = Sucessores(sol, P)
        if viz is None or f_viz >= f:
            return sol, f
        sol, f = viz, f_viz
        it += 1
        if log is not None:
            log.append(f"it {it:3d}   f = {f:<8g}  {sol}")


def SubidaEncostaTentativas(P, sol, tentativas, log=None):
    # repete a subida de encosta partindo de solucoes diferentes e fica com a melhor
    melhor, f_melhor = None, math.inf
    for k in range(tentativas):
        if k > 0:
            sol = SolInicial(P, "Aleatória")
        s, f = SubidaEncosta(P, sol)
        if log is not None:
            log.append(f"tentativa {k + 1:3d}   f = {f:<8g}  {s}")
        if f < f_melhor:
            melhor, f_melhor = s, f
    return melhor, f_melhor


def TemperaSimulada(P, sol, Tini, Tfim, fator, log=None):
    f = Avalia(sol, P)
    melhor, f_melhor = sol, f
    T = Tini
    it = 0
    while T > Tfim:
        viz = sol[:]
        if len(viz) > 1:
            i, j = random.sample(range(len(viz)), 2)
            viz[i], viz[j] = viz[j], viz[i]
        f_viz = Avalia(viz, P)
        delta = f_viz - f
        # melhor: aceita sempre / pior: aceita com chance e^(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / T):
            sol, f = viz, f_viz
            if f < f_melhor:
                melhor, f_melhor = sol, f
        it += 1
        if log is not None:
            log.append(f"it {it:4d}   T = {T:8.3f}   f = {f:<8g}  melhor = {f_melhor:g}")
        T = T * fator
    return melhor, f_melhor


def Executar(P, metodo, sol, tentativas, Tini, Tfim, fator, log=None):
    if metodo == "Subida de Encosta":
        return SubidaEncosta(P, sol, log)
    if metodo == "Subida de Encosta com Tentativas":
        return SubidaEncostaTentativas(P, sol, tentativas, log)
    return TemperaSimulada(P, sol, Tini, Tfim, fator, log)


# ---------------- analise comparativa ----------------

METODOS = ["Subida de Encosta", "Subida de Encosta com Tentativas", "Têmpera Simulada"]


def Analise(P, modo, tentativas, Tini, Tfim, fator, execucoes=10):
    # cada execucao parte de uma solucao inicial diferente,
    # e os tres metodos usam a mesma solucao inicial naquela execucao
    iniciais = [SolInicial(P, modo) for _ in range(execucoes)]
    resultado = []
    for metodo in METODOS:
        finais, ganhos, tempos = [], [], []
        melhor, f_melhor = None, math.inf
        for sol0 in iniciais:
            f0 = Avalia(sol0, P)
            inicio = time.perf_counter()
            sol, f = Executar(P, metodo, sol0[:], tentativas, Tini, Tfim, fator)
            tempos.append((time.perf_counter() - inicio) * 1000)
            finais.append(f)
            ganhos.append(100 * (f0 - f) / f0 if f0 else 0)
            if f < f_melhor:
                melhor, f_melhor = sol, f
        if metodo == "Subida de Encosta":
            config = "-"
        elif metodo == "Subida de Encosta com Tentativas":
            config = f"{tentativas} tentativas"
        else:
            config = f"T0={Tini:g} Tf={Tfim:g} fator={fator:g}"
        resultado.append({
            "metodo": metodo, "config": config,
            "f_medio": sum(finais) / len(finais), "f_melhor": f_melhor,
            "ganho": sum(ganhos) / len(ganhos), "tempo": sum(tempos) / len(tempos),
            "rota": [0] + melhor + [0],
        })
    return resultado


# ---------------- PDF (feito na mao, sem biblioteca) ----------------

def GerarPDF(caminho, textos, linhas):
    # textos: (x, y, tamanho, negrito, texto)   linhas: (x1, y1, x2, y2)
    ops = ["0.5 w"]
    for x1, y1, x2, y2 in linhas:
        ops.append(f"{x1} {y1} m {x2} {y2} l S")
    for x, y, tam, negrito, txt in textos:
        txt = str(txt).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        fonte = "/F1" if negrito else "/F2"
        ops.append(f"BT {fonte} {tam} Tf {x} {y} Td ({txt}) Tj ET")
    dados = "\n".join(ops).encode("cp1252", "replace")

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(dados)).encode() + b" >>\nstream\n" + dados + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
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
    saida += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{inicio}\n%%EOF".encode()
    with open(caminho, "wb") as arq:
        arq.write(saida)


def RelatorioPDF(caminho, P, resultado, modo, execucoes):
    textos, linhas = [], []
    y = 800
    textos.append((40, y, 15, True, "Rebalanceamento de Bicicletas - Análise comparativa"))
    y -= 20
    textos.append((50, y, 10, False, f"Gerado em {time.strftime('%d/%m/%Y %H:%M')}"))
    y -= 28
    n = len(P["pontos"]) - 1
    textos.append((50, y, 10, False,
                   f"Problema: {n} estações ({len(P['estacoes'])} precisam de ajuste), "
                   f"caminhão Q = {P['Q']}, sai com L0 = {P['L0']}"))
    y -= 15
    textos.append((50, y, 10, False,
                   f"f = {P['alfa']:g} x distância + {P['beta']:g} x desequilíbrio residual"))
    y -= 15
    textos.append((50, y, 10, False,
                   f"{execucoes} execuções por método, solução inicial {modo}, "
                   f"a mesma para os três métodos em cada execução"))
    y -= 30

    cols = [40, 195, 320, 380, 440, 500, 560]
    cab = ["Método", "Configuração", "f médio", "Melhor f", "Ganho %", "Tempo ms"]
    alt = 20
    total = len(resultado) + 1
    for k in range(total + 1):
        linhas.append((cols[0], y - k * alt, cols[-1], y - k * alt))
    for x in cols:
        linhas.append((x, y, x, y - total * alt))
    for x, c in zip(cols, cab):
        textos.append((x + 4, y - 14, 9, True, c))
    for k, r in enumerate(resultado, 1):
        valores = [r["metodo"], r["config"], f"{r['f_medio']:.1f}", f"{r['f_melhor']:g}",
                   f"{r['ganho']:.1f}", f"{r['tempo']:.1f}"]
        for x, v in zip(cols, valores):
            tam = 7 if x in (cols[0], cols[1]) else 9
            textos.append((x + 4, y - k * alt - 14, tam, False, v))
    y -= total * alt + 30

    textos.append((50, y, 11, True, "Melhor rota encontrada por método"))
    y -= 18
    for r in resultado:
        rota = " - ".join(map(str, r["rota"]))
        textos.append((50, y, 9, True, r["metodo"]))
        y -= 13
        textos.append((60, y, 9, False, f"{rota}   (f = {r['f_melhor']:g})"))
        y -= 18

    GerarPDF(caminho, textos, linhas)


if __name__ == "__main__":
    # teste com o exemplo do slide: tem que dar 18 e 15
    P = {"C": [[0, 4, 5], [4, 0, 6], [5, 6, 0]], "d": [0, 4, -5], "Q": 6, "L0": 4,
         "alfa": 1, "beta": 1}
    print("0-2-1-0:", Avalia([2, 1], P))
    print("0-1-2-0:", Avalia([1, 2], P))