# -*- coding: utf-8 -*-
"""
Green Formwork Brasil — Gerador de Orçamento (Streamlit)
Preencha o nome da obra e as quantidades; o app calcula os totais com os
valores unitários de base e gera o PDF no padrão do orçamento GFW.
"""

import streamlit as st

from pdf_generator import build_pdf, fmt_money

st.set_page_config(page_title="Orçamento GFW", page_icon="🏗️", layout="wide")

# ----------------------------------------------------------------------------
# VALORES UNITÁRIOS DE BASE (FOB China, USD)
# ----------------------------------------------------------------------------
PRECOS_BASE = {
    "painel_18x12":  204.67,
    "painel_12x12":  155.30,
    "painel_12x09":  147.75,
    "escoramento_b35": 86.87,
    "feixe_1800":     30.28,
    "feixe_1200":     23.37,
    "feixe_900":      17.44,
    "erection":       18.76,
    "hammer":          5.93,
    "transport":     131.61,
    "ld1800_escada": 197.43,
    "fita":            3.86,
    "braco_18":       51.33,
    "braco_12":       43.77,
    "reescoramento_b35": 86.87,
}

# (chave, TIPO, ESPECIFICAÇÃO, rótulo do formulário)
ITENS = [
    ("painel_18x12",   "PAINEL",          "1.8X1.2M",   "Painel 1.8 x 1.2 m"),
    ("painel_12x12",   "PAINEL",          "1.2X1.2M",   "Painel 1.2 x 1.2 m"),
    ("painel_12x09",   "PAINEL",          "1.2X0,9M",   "Painel 1.2 x 0.9 m"),
    ("escoramento_b35","ESCORAMENTO",     "B35",        "Escoramento B35"),
    ("feixe_1800",     "FEIXE PREENCHI.", "WFL_1800",   "Feixe de preenchimento WFL 1800"),
    ("feixe_1200",     "FEIXE PREENCHI.", "WFL_1200",   "Feixe de preenchimento WFL 1200"),
    ("feixe_900",      "FEIXE PREENCHI.", "WFL_900",    "Feixe de preenchimento WFL 900"),
    ("erection",       "ERECTION",        "ACESSORIO",  "Erection ladger"),
    ("hammer",         "HAMMER",          "ACESSORIO",  "Martelo para desforma"),
    ("transport",      "TRANSPORT.",      "ACESSORIP",  "Transportador de equipamentos"),
    ("ld1800_escada",  "LD 1800 ESCADA",  "ACESSORIP",  "LD 1800 escada"),
    ("fita",           "FITA",            "ACESSORIO",  "Fita de vedação"),
    ("braco_18",       "BRAÇO",           "TRAVAMENTO", "Braço de trava 1.8 m"),
    ("braco_12",       "BRAÇO",           "TRAVAMENTO", "Braço de trava 1.2 m"),
]

# Itens que aparecem na tabela "CIMBRAMENTO BASE" da página 1
ITENS_PAG1 = {"painel_18x12", "painel_12x12", "painel_12x09",
              "escoramento_b35", "feixe_1800", "feixe_1200", "feixe_900"}

# ----------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------
st.title("🏗️ Green Formwork Brasil — Gerador de Orçamento")
st.caption("Preencha os dados da obra e as quantidades. "
           "Os valores unitários de base já estão configurados.")

col_a, col_b = st.columns([2, 1])
with col_a:
    obra = st.text_input("Nome da obra / empreendimento", value="", placeholder="Ex.: SALLINAS")
with col_b:
    containers = st.number_input("Containers a serem importados", min_value=0.0, value=1.0, step=1.0)

subtitulo = st.text_input("Subtítulo do orçamento",
                          value="CIMBRAMENTO COM REESCORAMENTO")

st.subheader("Quantidades — Cimbramento")
qtds = {}
cols = st.columns(3)
for i, (key, tipo, espec, rotulo) in enumerate(ITENS):
    with cols[i % 3]:
        qtds[key] = st.number_input(
            f"{rotulo}",
            min_value=0.0, value=0.0, step=1.0, key=f"q_{key}",
            help=f"Valor unitário base: {fmt_money(PRECOS_BASE[key])}",
        )

st.subheader("Reescoramento")
c1, c2, c3 = st.columns(3)
with c1:
    tem_reesc = st.checkbox("Incluir reescoramento", value=True)
with c2:
    reesc_pct = st.number_input("Percentual do reescoramento (%)", min_value=0.0,
                                value=100.0, step=5.0, disabled=not tem_reesc)
with c3:
    reesc_qtd = st.number_input("Quantidade de escoras (B35)", min_value=0.0,
                                value=0.0, step=1.0, disabled=not tem_reesc,
                                help=f"Valor unitário base: {fmt_money(PRECOS_BASE['reescoramento_b35'])}")

st.subheader("Detalhes da execução e economia")
e1, e2, e3 = st.columns(3)
with e1:
    exec_andar = st.text_input("Andar / tipo", value="TIPO ENVIADO")
with e2:
    exec_m2_laje = st.number_input("M² de laje", min_value=0.0, value=0.0, step=1.0)
with e3:
    exec_m2_atendida = st.number_input("Quantidade atendida (m²)", min_value=0.0,
                                       value=0.0, step=1.0)

g1, g2, g3 = st.columns(3)
with g1:
    econ_sistema = st.text_input("Sistema", value="GFW")
with g2:
    econ_m2_total = st.number_input("M² de laje total (economia)", min_value=0.0,
                                    value=0.0, step=1.0)
with g3:
    econ_pct = st.number_input("Economia (%)", min_value=0.0, value=0.0, step=0.1)

with st.expander("⚙️ Valores unitários de base (avançado)"):
    st.caption("Só altere se a tabela de preços FOB mudar.")
    pc = st.columns(3)
    precos = {}
    labels = {k: r for k, _, _, r in ITENS}
    labels["reescoramento_b35"] = "Reescoramento B35"
    for i, (key, base) in enumerate(PRECOS_BASE.items()):
        with pc[i % 3]:
            precos[key] = st.number_input(labels.get(key, key), min_value=0.0,
                                          value=float(base), step=0.01,
                                          format="%.2f", key=f"p_{key}")

# ----------------------------------------------------------------------------
# Cálculos
# ----------------------------------------------------------------------------
detalhe_rows = []
total_cimbramento = 0.0
for key, tipo, espec, _ in ITENS:
    unit = precos[key]
    qtd = qtds[key]
    total = unit * qtd
    total_cimbramento += total
    detalhe_rows.append({"key": key, "tipo": tipo, "espec": espec,
                         "qtd": qtd, "unit": unit, "total": total})

base_rows = [r for r in detalhe_rows if r["key"] in ITENS_PAG1 and r["qtd"] > 0]

total_reescoramento = (precos["reescoramento_b35"] * reesc_qtd) if tem_reesc else 0.0
total_geral = total_cimbramento + total_reescoramento

st.divider()
r1, r2, r3 = st.columns(3)
r1.metric("Cimbramento base", fmt_money(total_cimbramento))
r2.metric("Reescoramento", fmt_money(total_reescoramento))
r3.metric("VALOR FOB CHINA (total)", fmt_money(total_geral))

# ----------------------------------------------------------------------------
# Geração do PDF
# ----------------------------------------------------------------------------
pct_label = f"{reesc_pct:.0f}%"

data = {
    "obra": obra.strip() or "OBRA",
    "subtitulo": subtitulo.strip() or "CIMBRAMENTO COM REESCORAMENTO",
    "total_geral": total_geral,
    "total_cimbramento": total_cimbramento,
    "total_reescoramento": total_reescoramento,
    "base_rows": base_rows,
    "detalhe_rows": detalhe_rows,
    "mostra_reescoramento": tem_reesc,
    "reesc_pct_label": pct_label,
    "reesc_espec": "B35",
    "reesc_qtd": reesc_qtd,
    "reesc_unit": precos["reescoramento_b35"],
    "containers": containers,
    "exec_andar": exec_andar,
    "exec_m2_laje": exec_m2_laje,
    "exec_m2_atendida": exec_m2_atendida,
    "econ_sistema": econ_sistema,
    "econ_m2_total": econ_m2_total,
    "econ_pct": econ_pct,
}

if st.button("📄 Gerar PDF do orçamento", type="primary", use_container_width=True):
    if not obra.strip():
        st.error("Informe o nome da obra antes de gerar o PDF.")
    else:
        pdf_bytes = build_pdf(data)
        st.success("PDF gerado com sucesso! Clique abaixo para salvar.")
        st.download_button(
            label=f"⬇️ Baixar {obra.strip().upper()}_ORÇAMENTO_GFW.pdf",
            data=pdf_bytes,
            file_name=f"{obra.strip().upper()}_ORÇAMENTO_GFW.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
