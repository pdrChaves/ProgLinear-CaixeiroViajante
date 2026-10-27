# backend - rebalanceamento de bicicletas
import math
import random
import time


def DadosFixos():
    # x, y, tem, meta, capacidade
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
    # diferenca entre coletar e entregar no maximo 10 (capacidade do caminhao)
    while True:
        d = [random.choice([-1, 1]) * random.randint(1, 6) for _ in range(N)]
        if abs(sum(d)) <= 10:
            break

    # sem repetir coordenada
    livres = [(x, y) for x in range(11) for y in range(11) if (x, y) != (5, 5)]
    pontos = random.sample(livres, N)

    estacoes = []
    for (x, y), dem in zip(pontos, d):
        cap = random.randint(max(8, abs(dem)), 15)
        tem = random.randint(max(0, -dem), min(cap, cap - dem))
        estacoes.append([x, y, tem, tem + dem, cap])
    return {"deposito": [5, 5], "Q": 10, "L0": 5, "estacoes": estacoes}


def GerarProblema(dados, alfa, beta):
    pontos = [dados["deposito"]] + [[e[0], e[1]] for e in dados["estacoes"]]
    n = len(pontos)

    # matriz de distancias, 0 = deposito
    C = []
    for i in range(n):
        linha = []
        for j in range(n):
            linha.append(round(math.dist(pontos[i], pontos[j]), 1))
        C.append(linha)

    s = [0] + [e[2] for e in dados["estacoes"]]
    t = [0] + [e[3] for e in dados["estacoes"]]
    cap = [0] + [e[4] for e in dados["estacoes"]]
    d = [t[i] - s[i] for i in range(n)]  # positivo entrega, negativo coleta

    return {
        "C": C, "pontos": pontos, "s": s, "t": t, "cap": cap, "d": d,
        "Q": dados["Q"], "L0": dados["L0"], "alfa": alfa, "beta": beta,
        "estacoes": [i for i in range(1, n) if d[i] != 0],
    }


def SolInicial(P):
    sol = list(P["estacoes"])
    random.shuffle(sol)
    return sol


def Operar(P, i, carga):
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
    anterior = 0
    for i in sol:
        nome = "Dep" if anterior == 0 else f"E{anterior}"
        km = P["C"][anterior][i]
        carga, q = Operar(P, i, carga)
        sobra += abs(P["d"][i]) - q
        acao = "entrega" if P["d"][i] > 0 else "coleta"
        passos.append(f"{nome} -> E{i}: {km:g} km | precisava {abs(P['d'][i])}, {acao} {q}, caminhao fica com {carga}")
        anterior = i
    if sol:
        passos.append(f"E{anterior} -> Dep: {P['C'][anterior][0]:g} km | volta ao deposito")

    f = P["alfa"] * dist + P["beta"] * sobra
    return round(f, 2), round(dist, 1), sobra, passos


def Avalia(sol, P):
    # f = alfa*distancia + beta*desequilibrio
    return Simular(sol, P)[0]


def Sucessores(sol, P, pos):
    # troca a posicao pos com as outras (n-1 vizinhos)
    vizinhos = []
    for j in range(len(sol)):
        if j != pos:
            viz = sol[:]
            viz[pos], viz[j] = viz[j], viz[pos]
            vizinhos.append((viz, Avalia(viz, P)))
    return vizinhos


def SubidaEncosta(P, sol, log=None):
    f = Avalia(sol, P)
    it = 0
    while len(sol) > 1:
        it += 1
        pos = random.randrange(len(sol))
        vizinhos = Sucessores(sol, P, pos)
        viz, f_viz = min(vizinhos, key=lambda v: v[1])
        if log is not None:
            notas = ", ".join(f"{fv:g}" for _, fv in vizinhos)
            log.append(f"it {it:3d}  posicao {pos + 1}  vizinhos: {notas}")
        if f_viz >= f:
            if log is not None:
                log.append(f"        nenhum vizinho melhor que f = {f:g}, para aqui")
            break
        sol, f = viz, f_viz
        if log is not None:
            log.append(f"        melhor vizinho: {sol}  f = {f:g}")
    return sol, f


def SubidaEncostaTentativas(P, sol, tmax, log=None):
    # para depois de tmax tentativas seguidas sem melhorar
    f = Avalia(sol, P)
    t = 0
    it = 0
    while t < tmax and len(sol) > 1:
        it += 1
        pos = random.randrange(len(sol))
        vizinhos = Sucessores(sol, P, pos)
        viz, f_viz = min(vizinhos, key=lambda v: v[1])
        if f_viz < f:
            sol, f = viz, f_viz
            t = 0
            if log is not None:
                log.append(f"it {it:3d}  posicao {pos + 1}  melhorou: {sol}  f = {f:g}")
        else:
            t += 1
            if log is not None:
                log.append(f"it {it:3d}  posicao {pos + 1}  sem melhora ({t}/{tmax})")
    return sol, f


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
        if delta < 0 or random.random() < math.exp(-delta / T):
            sol, f = viz, f_viz
            if f < f_melhor:
                melhor, f_melhor = sol, f
        it += 1
        if log is not None:
            log.append(f"it {it:4d}   T = {T:8.3f}   f = {f:<8g}  melhor = {f_melhor:g}")
        T = T * fator
    return melhor, f_melhor


def Executar(P, metodo, sol, tmax, Tini, Tfim, fator, log=None):
    if metodo == "Subida de Encosta":
        return SubidaEncosta(P, sol, log)
    if metodo == "Subida de Encosta com Tentativas":
        return SubidaEncostaTentativas(P, sol, tmax, log)
    return TemperaSimulada(P, sol, Tini, Tfim, fator, log)


METODOS = ["Subida de Encosta", "Subida de Encosta com Tentativas", "Têmpera Simulada"]


def Analise(P, tmax, Tini, Tfim, fator, execucoes=10):
    # os 3 metodos comecam da mesma solucao em cada execucao
    iniciais = [SolInicial(P) for _ in range(execucoes)]
    resultado = []
    for metodo in METODOS:
        finais, ganhos, tempos = [], [], []
        melhor, f_melhor = None, math.inf
        for sol0 in iniciais:
            f0 = Avalia(sol0, P)
            inicio = time.perf_counter()
            sol, f = Executar(P, metodo, sol0[:], tmax, Tini, Tfim, fator)
            tempos.append((time.perf_counter() - inicio) * 1000)
            finais.append(f)
            ganhos.append(100 * (f0 - f) / f0 if f0 else 0)
            if f < f_melhor:
                melhor, f_melhor = sol, f
        if metodo == "Subida de Encosta":
            config = "-"
        elif metodo == "Subida de Encosta com Tentativas":
            config = f"TMAX={tmax}"
        else:
            config = f"T0={Tini:g} Tf={Tfim:g} fator={fator:g}"
        resultado.append({
            "metodo": metodo, "config": config,
            "f_medio": sum(finais) / len(finais), "f_melhor": f_melhor,
            "ganho": sum(ganhos) / len(ganhos), "tempo": sum(tempos) / len(tempos),
            "rota": [0] + melhor + [0],
        })
    return resultado


# pdf gerado na mao
def GerarPDF(caminho, textos, linhas):
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


def RelatorioPDF(caminho, P, resultado, execucoes):
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
                   f"{execucoes} execuções por método, solução inicial aleatória, "
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
    # exemplo do slide (18 e 15)
    P = {"C": [[0, 4, 5], [4, 0, 6], [5, 6, 0]], "d": [0, 4, -5], "Q": 6, "L0": 4,
         "alfa": 1, "beta": 1}
    print("0-2-1-0:", Avalia([2, 1], P))
    print("0-1-2-0:", Avalia([1, 2], P))
    
