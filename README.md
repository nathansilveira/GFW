# -*- coding: utf-8 -*-
"""
Gerador de PDF de orçamento — Green Formwork Brasil
Replica o layout do orçamento padrão (modelo SALLINAS), 2 páginas A4.
"""

import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------------
# Cores do modelo
# ----------------------------------------------------------------------------
GREEN_MAIN = (0.30, 0.69, 0.31)      # verde do cabeçalho
GREEN_TEXT = (0.30, 0.69, 0.31)
GREEN_LIGHT = (0.78, 0.90, 0.79)     # verde claro (cabeçalho de tabela)
GREEN_LIGHTER = (0.88, 0.95, 0.88)   # verde bem claro (linhas)
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
GRAY_BORDER = (0.65, 0.65, 0.65)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt


# ----------------------------------------------------------------------------
# Formatação de números no padrão brasileiro
# ----------------------------------------------------------------------------
def fmt_money(v, prefix="$"):
    """62368.28 -> $62.368,28"""
    s = f"{v:,.2f}"                     # 62,368.28
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{prefix}{s}"


def fmt_qty(v):
    """120 -> 120,00"""
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def fmt_pct(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s}%"


def _img(name):
    p = os.path.join(ASSETS_DIR, name)
    return ImageReader(p) if os.path.exists(p) else None


# ----------------------------------------------------------------------------
# Desenho de tabelas simples
# ----------------------------------------------------------------------------
def _table(c, x, y_top, col_widths, rows, row_h=13, header_bg=GREEN_LIGHT,
           body_bg=GREEN_LIGHTER, header_bold=True, font_size=6.5,
           title=None, title_bg=GREEN_MAIN, title_color=WHITE,
           aligns=None, last_row_bold=False, zebra=False):
    """Desenha uma tabela e devolve o y final (embaixo)."""
    total_w = sum(col_widths)
    y = y_top

    if title is not None:
        c.setFillColorRGB(*title_bg)
        c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
        c.setFillColorRGB(*title_color)
        c.setFont("Helvetica-Bold", font_size + 0.5)
        c.drawCentredString(x + total_w / 2, y - row_h + 3.5, title)
        y -= row_h

    for i, row in enumerate(rows):
        is_header = (i == 0)
        is_last = (i == len(rows) - 1)
        if is_header:
            c.setFillColorRGB(*header_bg)
        elif zebra and i % 2 == 0:
            c.setFillColorRGB(*GREEN_LIGHTER)
        else:
            c.setFillColorRGB(*(body_bg if body_bg else WHITE))
        c.rect(x, y - row_h, total_w, row_h, fill=1, stroke=0)
        c.setStrokeColorRGB(*WHITE)
        c.setLineWidth(0.7)
        c.line(x, y - row_h, x + total_w, y - row_h)

        c.setFillColorRGB(*BLACK)
        if is_header and header_bold:
            c.setFont("Helvetica-Bold", font_size)
        elif is_last and last_row_bold:
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica", font_size)

        cx = x
        for j, cell in enumerate(row):
            al = "C"
            if aligns and j < len(aligns):
                al = aligns[j]
            txt = str(cell)
            if al == "L":
                c.drawString(cx + 3, y - row_h + 3.5, txt)
            elif al == "R":
                c.drawRightString(cx + col_widths[j] - 3, y - row_h + 3.5, txt)
            else:
                c.drawCentredString(cx + col_widths[j] / 2, y - row_h + 3.5, txt)
            # separador vertical branco
            c.setStrokeColorRGB(*WHITE)
            c.line(cx, y, cx, y - row_h)
            cx += col_widths[j]
        y -= row_h
    return y


# ----------------------------------------------------------------------------
# Página 1
# ----------------------------------------------------------------------------
def _page1(c, d):
    m = 50  # margem

    # --- Cabeçalho verde -----------------------------------------------------
    header_h = 78
    c.setFillColorRGB(*GREEN_MAIN)
    c.rect(m, PAGE_H - 55 - header_h, PAGE_W - 2 * m, header_h, fill=1, stroke=0)

    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(m + 24, PAGE_H - 55 - 34, "Green Formwork Brasil")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(m + 24, PAGE_H - 55 - 60, "EMPRESA ESPECIALISTA EM CIMBRAMENTOS METÁLICOS")

    c.setFont("Helvetica-Bold", 15)
    c.drawRightString(PAGE_W - m - 30, PAGE_H - 55 - 40, d["obra"].upper())

    # --- Faixa preta: título do orçamento -----------------------------------
    y_bar = PAGE_H - 55 - header_h - 42
    bar_w = 335
    c.setFillColorRGB(*BLACK)
    c.rect(m, y_bar, bar_w, 24, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(*WHITE)
    c.drawString(m + 12, y_bar + 8, "Orçamento Prévio; ")
    w1 = c.stringWidth("Orçamento Prévio; ", "Helvetica-Bold", 10)
    c.setFillColorRGB(*GREEN_MAIN)
    c.drawString(m + 12 + w1, y_bar + 8, d["subtitulo"])

    # --- Caixa verde: valor FOB ---------------------------------------------
    box_x = m + bar_w + 5
    box_w = PAGE_W - m - box_x
    box_h = 105
    c.setFillColorRGB(*GREEN_MAIN)
    c.rect(box_x, y_bar + 24 - box_h, box_w, box_h, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-BoldOblique", 6.5)
    c.drawCentredString(box_x + box_w / 2, y_bar + 24 - 32, "VALOR FOB CHINA")
    c.setStrokeColorRGB(*WHITE)
    c.setLineWidth(0.8)
    c.line(box_x + 12, y_bar + 24 - 40, box_x + box_w - 12, y_bar + 24 - 40)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(box_x + box_w / 2, y_bar + 24 - 62, fmt_money(d["total_geral"]))

    # --- Faixa preta: demonstrativo ------------------------------------------
    y_dem = y_bar - 66
    c.setFillColorRGB(*BLACK)
    c.rect(m, y_dem, bar_w, 24, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(m + bar_w / 2, y_dem + 8, "DEMONSTRATIVO DE EQUIPAMENTOS")

    # --- Lista de equipamentos com fotos (esquerda) --------------------------
    equip = [
        ("ESCORAS B35", "equip_escora.png"),
        ("BRAÇO DE TRAVA", "equip_braco.png"),
        ("PAINEL PARA LAJE", "equip_painel.png"),
        ("FEIXE DE PREENCHIMENTO", "equip_feixe.png"),
        ("ERECTION LADGER", "equip_erection.png"),
        ("MARTELO PARA DESFORMA", "equip_martelo.png"),
        ("EQUIPAMENTO PARA\nTRANSPORTE", "equip_transporte.png"),
        ("FITA DE VEDAÇÃO", "equip_fita.png"),
    ]
    eq_x = m + 22
    eq_top = y_dem - 78
    row_h = 26
    name_w = 116
    img_w = 92
    c.setStrokeColorRGB(*GREEN_MAIN)
    c.setLineWidth(0.8)
    y = eq_top
    for i, (name, img_file) in enumerate(equip):
        # célula do nome
        c.setFillColorRGB(*(GREEN_LIGHT if i % 2 == 0 else GREEN_LIGHTER))
        c.rect(eq_x, y - row_h, name_w, row_h, fill=1, stroke=1)
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica-Bold", 6)
        lines = name.split("\n")
        if len(lines) == 1:
            c.drawString(eq_x + 4, y - row_h / 2 - 2, lines[0])
        else:
            c.drawString(eq_x + 4, y - row_h / 2 + 2, lines[0])
            c.drawString(eq_x + 4, y - row_h / 2 - 6, lines[1])
        # célula da imagem
        c.setFillColorRGB(*WHITE)
        c.rect(eq_x + name_w, y - row_h, img_w, row_h, fill=1, stroke=1)
        img = _img(img_file)
        if img is not None:
            iw, ih = img.getSize()
            scale = min((img_w - 8) / iw, (row_h - 4) / ih)
            dw, dh = iw * scale, ih * scale
            c.drawImage(img, eq_x + name_w + (img_w - dw) / 2,
                        y - row_h + (row_h - dh) / 2, dw, dh,
                        preserveAspectRatio=True, mask="auto")
        y -= row_h

    # --- CIMBRAMENTO BASE (direita) ------------------------------------------
    tx = 345
    tw = [78, 82, 82]
    ty = y_dem - 60

    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(tx, ty + 6, "CIMBRAMENTO BASE")

    rows = [["TIPO", "ESPECIFICAÇÃO", "QUANTIDADE"]]
    for item in d["base_rows"]:
        rows.append([item["tipo"], item["espec"], fmt_qty(item["qtd"])])
    rows.append(["", "VALOR FINAL", fmt_money(d["total_cimbramento"])])
    y_end = _table(c, tx, ty, tw, rows, aligns=["L", "C", "C"],
                   last_row_bold=True, zebra=True)

    # --- REESCORAMENTO 100% ---------------------------------------------------
    ty2 = y_end - 110
    if d["mostra_reescoramento"]:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*BLACK)
        c.drawString(tx, ty2 + 6, f"REESCORAMENTO {d['reesc_pct_label']}")
        rows2 = [["TIPO", "ESPECIFICAÇÃO", "QUANTIDADE"],
                 ["ESCORAMENTO", d["reesc_espec"], fmt_qty(d["reesc_qtd"])],
                 ["", "VALOR FINAL", fmt_money(d["total_reescoramento"])]]
        y_end2 = _table(c, tx, ty2, tw, rows2, aligns=["L", "C", "C"],
                        last_row_bold=True, zebra=True)
    else:
        y_end2 = ty2

    # --- Containers ------------------------------------------------------------
    ty3 = y_end2 - 55
    rows3 = [["CONTAINERS A SEREM IMPORTADOS"],
             ]
    c.setFillColorRGB(*GREEN_LIGHT)
    c.rect(tx, ty3 - 13, sum(tw), 13, fill=1, stroke=0)
    c.setFillColorRGB(0.45, 0.55, 0.45)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(tx + sum(tw) / 2, ty3 - 9.5, "CONTAINERS A SEREM IMPORTADOS")
    c.setFillColorRGB(*GREEN_LIGHTER)
    c.rect(tx, ty3 - 26, sum(tw), 13, fill=1, stroke=0)
    c.setFillColorRGB(0.45, 0.55, 0.45)
    c.drawString(tx + 3, ty3 - 22.5, "QUANTIDADE")
    c.setFillColorRGB(*BLACK)
    c.drawCentredString(tx + sum(tw) / 2 + 20, ty3 - 22.5, fmt_qty(d["containers"]))

    # --- Observações -----------------------------------------------------------
    obs = [
        "OBSERVAÇÕES SOBRE O ORÇAMENTO:",
        "* ORÇAMENTO FEITO CONFORME AS MEDIDAS DAS PLANTAS ENVIADAS.",
        "* VALOR MONETÁRIO EM DÓLAR AMERICANO.",
        "* TODOS EQUIPAMENTOS DE EXEMPLO (PARTE ESQUERDA, SÃO EXEMPLOS",
        "DE COMO SERIA UM CONTAINER DE IMPORTAÇÃO PADRAO).",
        "* ORÇAMENTO ENVIADO ESTÁ COTADO TODOS BRAÇOS DE TRAVAMENTOS",
        " E EQUIPAMENTOS ADICIONAIS ESPECIFICOS DE DESFORMA E DESLOCAMETO.",
    ]
    c.setFillColorRGB(*BLACK)
    c.setFont("Helvetica", 7)
    yo = 240
    for line in obs:
        c.drawString(m + 22, yo, line)
        yo -= 10


# ----------------------------------------------------------------------------
# Página 2
# ----------------------------------------------------------------------------
def _page2(c, d):
    m = 50

    # --- Cabeçalho verde -----------------------------------------------------
    header_h = 100
    c.setFillColorRGB(*GREEN_MAIN)
    c.rect(m, PAGE_H - 55 - header_h, PAGE_W - 2 * m, header_h, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(m + 24, PAGE_H - 55 - 48, "DETALHES GERAIS")
    c.setFont("Helvetica-Bold", 15)
    c.drawRightString(PAGE_W - m - 40, PAGE_H - 55 - 62, d["obra"].upper())

    # --- Tabela detalhes do orçamento ----------------------------------------
    tx = m + 22
    tw = [52, 50, 33, 42, 45]
    ty = PAGE_H - 55 - header_h - 40

    rows = [["TIPO", "ESPECIFICAÇÃO", "QUANT.", "VALOR UNI.", "VALOR TOTAL"]]
    for it in d["detalhe_rows"]:
        rows.append([it["tipo"], it["espec"], fmt_qty(it["qtd"]),
                     fmt_money(it["unit"]), fmt_money(it["total"])])
    _table(c, tx, ty, tw, rows, title="DETALHES DO ORÇAMENTO",
           aligns=["L", "C", "C", "C", "C"], zebra=True, font_size=6)

    y_after = ty - 13 * (len(rows) + 1)

    # --- Reescoramento ---------------------------------------------------------
    if d["mostra_reescoramento"]:
        ty2 = y_after - 45
        rows2 = [["TIPO", "ESPECIFICAÇÃO", "QUANT.", "VALOR UNI.", "VALOR TOTAL"],
                 ["REESCORAMENTO", d["reesc_espec"], fmt_qty(d["reesc_qtd"]),
                  fmt_money(d["reesc_unit"]),
                  fmt_money(d["total_reescoramento"], prefix="")]]
        _table(c, tx, ty2, tw, rows2, title=f"REESCORAMENTO {d['reesc_pct_label']}",
               aligns=["L", "C", "C", "C", "C"], zebra=True, font_size=6)
        y_after = ty2 - 13 * 3

    # --- Detalhes da execução ---------------------------------------------------
    ty3 = y_after - 45
    tw3 = [74, 74, 74]
    rows3 = [["ANDAR", "M² DE LAJE", "QUANTIDADE ATENDIDA"],
             [d["exec_andar"], f"{fmt_qty(d['exec_m2_laje']).rstrip('0').rstrip(',')}m²",
              f"{fmt_qty(d['exec_m2_atendida']).rstrip('0').rstrip(',')}m²"]]
    _table(c, tx, ty3, tw3, rows3, title="DETALHES DA EXECUÇÃO",
           aligns=["L", "C", "R"], zebra=True, font_size=6)
    y_after = ty3 - 13 * 3

    # --- Economia ---------------------------------------------------------------
    ty4 = y_after - 30
    rows4 = [["SISTEMA", "M² DE LAJE TOTAL", "ECONOMIA %"],
             [d["econ_sistema"],
              f"{fmt_qty(d['econ_m2_total']).rstrip('0').rstrip(',')}m²",
              fmt_pct(d["econ_pct"])]]
    _table(c, tx, ty4, tw3, rows4, title="ECONOMIA GERADA PELO SISTEMA GREEN FORMWORK",
           aligns=["L", "C", "C"], zebra=True, font_size=6)

    # --- Logo GFW (direita) ------------------------------------------------------
    logo = _img("logo_gfw.png")
    if logo is not None:
        iw, ih = logo.getSize()
        lw = 210
        lh = lw * ih / iw
        lx = PAGE_W - m - lw - 15
        ly = PAGE_H - 55 - header_h - 75 - lh / 2
        c.drawImage(logo, lx, ly, lw, lh, preserveAspectRatio=True, mask="auto")
        c.setFillColorRGB(*BLACK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(lx + lw / 2, ly - 14, "VENDA E LOCAÇÃO DE CIMBRAMENTO")
        c.setFillColorRGB(*GREEN_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(lx + lw / 2, ly - 30, "www.greenformwork.com.br")


# ----------------------------------------------------------------------------
# API pública
# ----------------------------------------------------------------------------
def build_pdf(data: dict) -> bytes:
    """Recebe o dicionário de dados calculados e devolve o PDF em bytes."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"ORÇAMENTO-GFW - {data['obra']}")
    _page1(c, data)
    c.showPage()
    _page2(c, data)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
