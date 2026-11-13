"""Peças interativas do dashboard: explorador dos PRs reais, simulador de poder e navegação.

Tudo roda no navegador a partir de números já calculados em Python (embutidos como JSON),
então a página continua estática e reproduzível.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats

from lab04 import cores
from lab04.exemplo import formatar_numero as fmt

ROTULOS_GRUPO = {"sem_bot": "Sem bot", "com_bot": "Com bot"}
COR_GRUPO = {"sem_bot": cores.TINTA_SECUNDARIA, "com_bot": cores.COR_REAL}


def dados_prs(tabela: pd.DataFrame, semente: int) -> dict:
    """Cada PR com horas, posto entre os 60 e uma posição vertical fixa (jitter reproduzível)."""
    horas = tabela["horas_ate_merge"].to_numpy()
    postos = stats.rankdata(horas)
    rng = np.random.default_rng(semente + 7)
    jitter = rng.uniform(-0.26, 0.26, len(tabela))
    grupos = {}
    for indice, grupo in enumerate(("sem_bot", "com_bot")):
        filtro = (tabela["grupo"] == grupo).to_numpy()
        h, p = horas[filtro], postos[filtro]
        grupos[grupo] = {
            "rotulo": ROTULOS_GRUPO[grupo],
            "cor": COR_GRUPO[grupo],
            "y": [round(indice + j, 4) for j in jitter[filtro]],
            "horas": [round(float(v), 4) for v in h],
            "log": [round(float(np.log10(max(v, 1e-3))), 4) for v in h],
            "postos": [float(v) for v in p],
            "numeros": [int(v) for v in tabela.loc[filtro, "numero"]],
            "urls": list(tabela.loc[filtro, "url"]),
            "media": float(np.mean(h)),
            "posto_medio": float(np.mean(p)),
        }
    maior = int(np.argmax(horas))
    return {
        "n": len(tabela),
        "grupos": grupos,
        "maior": {
            "numero": int(tabela["numero"].iloc[maior]),
            "horas": float(horas[maior]),
            "grupo": tabela["grupo"].iloc[maior],
        },
    }


def textos_explorador(prs: dict) -> dict[str, str]:
    sem, com = prs["grupos"]["sem_bot"], prs["grupos"]["com_bot"]
    maior = prs["maior"]
    return {
        "horas": (
            f"<strong>O que o Welch enxerga:</strong> os valores em horas. As linhas marcam as médias "
            f"({fmt(sem['media'], 1)} h sem bot e {fmt(com['media'], 1)} h com bot). Um único PR, o #{maior['numero']}, "
            f"levou {fmt(maior['horas'], 0)} h e puxa a média e a variância do seu grupo."
        ),
        "postos": (
            f"<strong>O que o Mann-Whitney enxerga:</strong> só a ordem. Os {prs['n']} PRs são enfileirados do mais rápido "
            f"ao mais lento, e o PR #{maior['numero']} vira apenas o posto {prs['n']}: valeria o mesmo se tivesse levado "
            f"50 h. As linhas marcam o posto médio de cada grupo ({fmt(sem['posto_medio'], 1)} sem bot e "
            f"{fmt(com['posto_medio'], 1)} com bot)."
        ),
    }


def html_explorador(prs: dict) -> str:
    textos = textos_explorador(prs)
    return f"""<figure class="explorador">
  <div class="barra-controles">
    <span class="rotulo-controle" id="rotulo-escala">Ver os PRs como</span>
    <div class="segmentado" role="radiogroup" aria-labelledby="rotulo-escala" data-controle="escala">
      <button type="button" role="radio" aria-checked="true" data-valor="horas">Horas <span class="nota-botao">(Welch)</span></button>
      <button type="button" role="radio" aria-checked="false" data-valor="postos">Postos <span class="nota-botao">(Mann-Whitney)</span></button>
    </div>
  </div>
  <div id="grafico-explorador" class="grafico-js" role="img" aria-label="Os {prs['n']} PRs reais, um ponto por PR, separados em sem bot e com bot"></div>
  <figcaption id="texto-explorador" aria-live="polite">{textos['horas']}</figcaption>
  <p class="dica">Passe o mouse sobre um ponto para ver o PR; clique para abri-lo no GitHub.</p>
</figure>"""


def html_simulador(simulacoes: dict) -> str:
    situacoes = "".join(
        f'<button type="button" role="radio" aria-checked="{"true" if i == 0 else "false"}" data-valor="{i}">{s["rotulo"]}</button>'
        for i, s in enumerate(simulacoes["situacoes"])
    )
    alfas = "".join(
        f'<button type="button" role="radio" aria-checked="{"true" if i == 0 else "false"}" data-valor="{a}">{fmt(a)}</button>'
        for i, a in enumerate(simulacoes["alfas"])
    )
    maximo = len(simulacoes["reducoes"]) - 1
    passo_inicial = simulacoes["reducoes"].index(0.5) if 0.5 in simulacoes["reducoes"] else maximo
    repeticoes = f"{simulacoes['repeticoes']:,}".replace(",", ".")
    return f"""<div class="simulador" id="simulador">
  <h3>Simulador: escolha a situação, o efeito e o α</h3>
  <p class="simulador-intro">Cada combinação mostra o resultado de {repeticoes} conjuntos simulados. Com efeito zero, a barra é o erro tipo I; com efeito, é o poder.</p>
  <div class="simulador-controles">
    <div class="campo">
      <span class="rotulo-controle" id="rotulo-situacao">Situação</span>
      <div class="segmentado quebra" role="radiogroup" aria-labelledby="rotulo-situacao" data-controle="situacao">{situacoes}</div>
    </div>
    <div class="campo">
      <label class="rotulo-controle" for="controle-efeito">Redução da mediana causada pelo bot: <output id="valor-efeito">{fmt(100 * simulacoes['reducoes'][passo_inicial], 0)}%</output></label>
      <input id="controle-efeito" type="range" min="0" max="{maximo}" step="1" value="{passo_inicial}">
    </div>
    <div class="campo">
      <span class="rotulo-controle" id="rotulo-alfa">Nível de significância α</span>
      <div class="segmentado" role="radiogroup" aria-labelledby="rotulo-alfa" data-controle="alfa">{alfas}</div>
    </div>
  </div>
  <div class="placar" aria-live="polite">
    <div class="linha-placar" data-teste="mann_whitney">
      <span class="nome-teste"><span class="amostra-cor mw"></span>Mann-Whitney</span>
      <span class="trilho"><span class="barra mw" style="width:0%"></span><span class="marca-alfa"></span></span>
      <span class="valor-placar">0%</span>
    </div>
    <div class="linha-placar" data-teste="welch">
      <span class="nome-teste"><span class="amostra-cor welch"></span>t de Welch</span>
      <span class="trilho"><span class="barra welch" style="width:0%"></span><span class="marca-alfa"></span></span>
      <span class="valor-placar">0%</span>
    </div>
  </div>
  <p class="leitura-simulador" id="leitura-simulador"></p>
  <p class="descricao-situacao" id="descricao-situacao"></p>
</div>"""


def payload(prs: dict, simulacoes: dict) -> str:
    dados = {
        "prs": prs,
        "textos": textos_explorador(prs),
        "simulacoes": {
            "repeticoes": simulacoes["repeticoes"],
            "alfas": simulacoes["alfas"],
            "reducoes": simulacoes["reducoes"],
            "situacoes": [
                {"rotulo": s["rotulo"], "descricao": s["descricao"], "poder": s["poder"]}
                for s in simulacoes["situacoes"]
            ],
        },
        "cores": {
            "tinta": cores.TINTA, "sec": cores.TINTA_SECUNDARIA, "fraca": cores.TINTA_FRACA,
            "grade": cores.GRADE, "eixo": cores.EIXO,
        },
    }
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    return texto.replace("</", "<\\/")


SCRIPT = r"""
(function () {
  const dados = JSON.parse(document.getElementById('dados-dashboard').textContent);
  const reduzMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const num = (v, casas) => v.toLocaleString('pt-BR', {minimumFractionDigits: casas, maximumFractionDigits: casas});
  const pct = (v, casas = 1) => num(100 * v, casas) + '%';
  const horasTxt = (h) => {
    if (h < 1) return Math.max(1, Math.round(h * 60)) + ' min';
    if (h < 48) return num(h, 1) + ' h';
    return num(h, 0) + ' h (' + num(h / 24, 1) + ' dias)';
  };

  // ---------- controles segmentados (radiogroup com teclado) ----------
  function segmentado(raiz, aoMudar) {
    const botoes = Array.from(raiz.querySelectorAll('[role="radio"]'));
    const marcar = (alvo) => {
      botoes.forEach((b) => {
        const ativo = b === alvo;
        b.setAttribute('aria-checked', ativo ? 'true' : 'false');
        b.tabIndex = ativo ? 0 : -1;
      });
      aoMudar(alvo.dataset.valor);
    };
    botoes.forEach((b, i) => {
      b.tabIndex = b.getAttribute('aria-checked') === 'true' ? 0 : -1;
      b.addEventListener('click', () => marcar(b));
      b.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        e.stopPropagation();
        const proximo = botoes[(i + (e.key === 'ArrowRight' ? 1 : botoes.length - 1)) % botoes.length];
        proximo.focus();
        marcar(proximo);
      });
    });
  }

  const fonte = getComputedStyle(document.body).fontFamily;

  // ---------- explorador dos PRs reais ----------
  function iniciarExplorador() {
    const alvo = document.getElementById('grafico-explorador');
    if (!alvo || !window.Plotly) return;
    const {prs, textos, cores} = dados;
    const grupos = ['sem_bot', 'com_bot'];
    const nTotal = prs.n;

    const ticksHoras = {vals: [-1, 0, 1, 2, 3], txt: ['6 min', '1 h', '10 h', '100 h', '1.000 h']};
    const eixoX = (modo) => modo === 'horas'
      ? {range: [-2.2, 3.1], tickvals: ticksHoras.vals, ticktext: ticksHoras.txt, title: {text: 'Tempo até o merge (escala log)'}}
      : {range: [0, nTotal + 1], tickvals: [1, 10, 20, 30, 40, 50, nTotal], ticktext: null, title: {text: 'Posto entre os ' + nTotal + ' PRs (1 = mais rápido)'}};

    const tracos = (modo) => grupos.map((g) => {
      const d = prs.grupos[g];
      return {
        type: 'scatter', mode: 'markers', name: d.rotulo,
        x: modo === 'horas' ? d.log : d.postos, y: d.y,
        customdata: d.horas.map((h, i) => [d.numeros[i], horasTxt(h), num(d.postos[i], d.postos[i] % 1 ? 1 : 0)]),
        hovertemplate: '<b>PR #%{customdata[0]}</b><br>%{customdata[1]}<br>posto %{customdata[2]} de ' + nTotal + '<extra>' + d.rotulo + '</extra>',
        marker: {size: 11, color: d.cor, opacity: 0.85, line: {color: '#ffffff', width: 1.5}},
      };
    });

    const referencias = (modo) => {
      const formas = [], notas = [];
      grupos.forEach((g, i) => {
        const d = prs.grupos[g];
        const x = modo === 'horas' ? Math.log10(d.media) : d.posto_medio;
        formas.push({type: 'line', x0: x, x1: x, y0: i - 0.42, y1: i + 0.42, line: {color: d.cor, width: 2.5}});
        notas.push({
          x: x, y: i + 0.42, yanchor: 'bottom', showarrow: false,
          text: (modo === 'horas' ? 'média ' + num(d.media, 1) + ' h' : 'posto médio ' + num(d.posto_medio, 1)),
          font: {color: cores.tinta, size: 12},
        });
      });
      return {formas, notas};
    };

    const layout = (modo) => {
      const r = referencias(modo);
      const x = eixoX(modo);
      return {
        margin: {l: 76, r: 18, t: 18, b: 56}, height: 300,
        paper_bgcolor: '#ffffff', plot_bgcolor: '#ffffff',
        font: {family: fonte, size: 13, color: cores.sec}, separators: ',.',
        showlegend: false, hovermode: 'closest',
        hoverlabel: {bgcolor: '#ffffff', bordercolor: cores.eixo, font: {color: cores.tinta, family: fonte}},
        xaxis: Object.assign({gridcolor: cores.grade, zeroline: false, linecolor: cores.eixo, fixedrange: true}, x),
        yaxis: {tickvals: [0, 1], ticktext: ['Sem bot', 'Com bot'], range: [-0.6, 1.75], gridcolor: 'rgba(0,0,0,0)', zeroline: false, fixedrange: true},
        shapes: r.formas, annotations: r.notas,
      };
    };

    let modo = 'horas';
    Plotly.newPlot(alvo, tracos(modo), layout(modo), {displayModeBar: false, responsive: true});
    alvo.on('plotly_click', (ev) => {
      const p = ev.points && ev.points[0];
      if (!p) return;
      const g = grupos[p.curveNumber];
      window.open(prs.grupos[g].urls[p.pointIndex], '_blank', 'noopener');
    });

    const legenda = document.getElementById('texto-explorador');
    segmentado(document.querySelector('[data-controle="escala"]'), (valor) => {
      modo = valor;
      legenda.innerHTML = textos[modo];
      const novo = layout(modo);
      if (reduzMovimento) { Plotly.react(alvo, tracos(modo), novo); return; }
      Plotly.relayout(alvo, {shapes: [], annotations: []});
      Plotly.animate(alvo, {data: tracos(modo).map((t) => ({x: t.x, y: t.y, customdata: t.customdata})), layout: {xaxis: novo.xaxis}},
        {transition: {duration: 650, easing: 'cubic-in-out'}, frame: {duration: 650, redraw: false}})
        .then(() => Plotly.react(alvo, tracos(modo), novo));
    });
  }

  // ---------- simulador de poder ----------
  function iniciarSimulador() {
    const raiz = document.getElementById('simulador');
    if (!raiz) return;
    const sim = dados.simulacoes;
    const estado = {situacao: 0, efeito: Number(document.getElementById('controle-efeito').value), alfa: String(sim.alfas[0])};
    const saidaEfeito = document.getElementById('valor-efeito');
    const leitura = document.getElementById('leitura-simulador');
    const descricao = document.getElementById('descricao-situacao');
    const total = sim.repeticoes.toLocaleString('pt-BR');

    function desenhar() {
      const s = sim.situacoes[estado.situacao];
      const reducao = sim.reducoes[estado.efeito];
      const alfa = Number(estado.alfa);
      saidaEfeito.textContent = num(100 * reducao, 0) + '%';
      const valores = {};
      raiz.querySelectorAll('.linha-placar').forEach((linha) => {
        const teste = linha.dataset.teste;
        const v = s.poder[teste][estado.alfa][estado.efeito];
        valores[teste] = v;
        linha.querySelector('.barra').style.width = (100 * v).toFixed(2) + '%';
        linha.querySelector('.marca-alfa').style.left = (100 * alfa) + '%';
        linha.querySelector('.valor-placar').textContent = pct(v);
      });
      const mw = valores.mann_whitney, w = valores.welch;
      if (reducao === 0) {
        leitura.innerHTML = '<strong>Sem efeito (H₀ verdadeira), a barra é o erro tipo I.</strong> O esperado é ' + pct(alfa, 0) +
          ' (a marca fina). Mann-Whitney: ' + pct(mw) + '; Welch: ' + pct(w) + '.';
      } else {
        const lider = mw >= w ? 'Mann-Whitney' : 't de Welch';
        const razao = Math.min(mw, w) > 0 ? Math.max(mw, w) / Math.min(mw, w) : null;
        const vantagem = Math.abs(mw - w) < 0.02 ? 'Os dois testes praticamente empatam.'
          : 'O ' + lider + ' detecta o efeito com mais frequência' + (razao && razao >= 1.5 && razao <= 10 ? ' (' + num(razao, 1) + ' vezes mais)' : '') + '.';
        leitura.innerHTML = '<strong>Se o bot reduzisse a mediana em ' + num(100 * reducao, 0) + '%</strong>, em ' + total +
          ' conjuntos o Mann-Whitney rejeitaria H₀ em ' + pct(mw) + ' e o Welch em ' + pct(w) + '. ' + vantagem;
      }
      descricao.textContent = s.descricao;
    }

    segmentado(raiz.querySelector('[data-controle="situacao"]'), (v) => { estado.situacao = Number(v); desenhar(); });
    segmentado(raiz.querySelector('[data-controle="alfa"]'), (v) => { estado.alfa = String(Number(v)); desenhar(); });
    const controle = document.getElementById('controle-efeito');
    controle.addEventListener('input', () => { estado.efeito = Number(controle.value); desenhar(); });
    controle.addEventListener('keydown', (e) => e.stopPropagation());
    desenhar();
  }

  // ---------- navegação e modo apresentação ----------
  function iniciarNavegacao() {
    const secoes = Array.from(document.querySelectorAll('main > section'));
    const links = new Map(Array.from(document.querySelectorAll('.trilha a')).map((a) => [a.getAttribute('href').slice(1), a]));
    const observador = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((a) => a.removeAttribute('aria-current'));
        const ativo = links.get(e.target.id);
        if (ativo) ativo.setAttribute('aria-current', 'true');
      });
    }, {rootMargin: '-35% 0px -60% 0px'});
    secoes.forEach((s) => observador.observe(s));

    const atual = () => {
      const meio = window.innerHeight * 0.4;
      let indice = -1;
      secoes.forEach((s, i) => { if (s.getBoundingClientRect().top <= meio) indice = i; });
      return indice;
    };
    document.addEventListener('keydown', (e) => {
      const alvo = e.target;
      if (alvo.closest && alvo.closest('input, textarea, select, [role="radiogroup"], .js-plotly-plot')) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      let destino = null;
      if (e.key === 'ArrowRight') destino = Math.min(secoes.length - 1, atual() + 1);
      if (e.key === 'ArrowLeft') destino = Math.max(0, atual() - 1);
      if (destino === null) return;
      e.preventDefault();
      secoes[destino].scrollIntoView({behavior: reduzMovimento ? 'auto' : 'smooth', block: 'start'});
    });

    const botao = document.getElementById('modo-apresentacao');
    const aplicar = (ligado) => {
      document.documentElement.classList.toggle('apresentacao', ligado);
      botao.setAttribute('aria-pressed', ligado ? 'true' : 'false');
      window.dispatchEvent(new Event('resize'));
    };
    let salvo = false;
    try { salvo = localStorage.getItem('lab04-apresentacao') === '1'; } catch (erro) { salvo = false; }
    aplicar(salvo);
    botao.addEventListener('click', () => {
      const ligado = !document.documentElement.classList.contains('apresentacao');
      aplicar(ligado);
      try { localStorage.setItem('lab04-apresentacao', ligado ? '1' : '0'); } catch (erro) { /* sem armazenamento */ }
    });
  }

  iniciarExplorador();
  iniciarSimulador();
  iniciarNavegacao();
})();
"""
