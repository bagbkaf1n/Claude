import sys
from xml.sax.saxutils import escape

class Page:
    def __init__(self, name):
        self.name, self.cells, self.n = name, [], 2
    def _id(self):
        self.n += 1
        return f"c{self.n}"
    def box(self, x, y, w, h, text, style=""):
        i = self._id()
        st = "rounded=0;whiteSpace=wrap;html=1;fontSize=11;" + style
        self.cells.append(f'<mxCell id="{i}" value="{escape(text, {chr(34): "&quot;"})}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def edge(self, a, b, label="", style="", pts=None):
        i = self._id()
        st = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=2;fontSize=10;" + style
        geo = '<mxGeometry relative="1" as="geometry">'
        if pts:
            geo += '<Array as="points">' + "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts) + '</Array>'
        geo += '</mxGeometry>'
        self.cells.append(f'<mxCell id="{i}" value="{escape(label)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}">{geo}</mxCell>')
        return i
    def xml(self, pid):
        return (f'<diagram id="{pid}" name="{escape(self.name)}"><mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" '
                f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.cells)}</root></mxGraphModel></diagram>')

MCB = "fillColor=#f5f5f5;strokeColor=#333333;"
RCD = "fillColor=#dae8fc;strokeColor=#6c8ebf;"
SW  = "fillColor=#fff2cc;strokeColor=#d6b656;"
REL = "fillColor=#f8cecc;strokeColor=#b85450;"
SRC = "ellipse;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;"
BUS = "fillColor=#333333;strokeColor=none;fontColor=#ffffff;fontSize=10;"
NOTE = "shape=note;size=14;fillColor=#ffffcc;strokeColor=#999999;align=left;verticalAlign=top;spacingLeft=6;fontSize=10;"
TITLE = "text;fontSize=16;fontStyle=1;align=left;strokeColor=none;fillColor=none;"
GEN_EDGE = "strokeColor=#2e7d32;"
DASH = "dashed=1;strokeColor=#888888;"

# ---------- Page 1: single-line diagram ----------
p = Page("Однолінійна схема")
p.box(40, 10, 700, 30, "Однолінійна схема щита (1ф, 230 В)", TITLE)
grid = p.box(110, 50, 120, 50, "Мережа<br>~230 В, L+N", SRC)
gen  = p.box(470, 50, 140, 50, "Зарядна станція<br>(вихід ~230 В)", SRC)

qf1 = p.box(100, 130, 140, 55, "<b>QF1</b> MCN 225<br>C25, 2P<br>вступний", MCB)
kv  = p.box(100, 215, 140, 55, "<b>KV1</b> ZUBR D2-40red<br>реле напруги 40 А", REL)
rcd = p.box(100, 300, 140, 55, "<b>QD1</b> CDA 240D<br>ПЗВ 40 А / 30 мА, тип A", RCD)
qf2 = p.box(470, 300, 140, 55, "<b>QF2</b> MBN 210<br>B10, 2P<br>ввід від станції", MCB)
sa  = p.box(250, 400, 200, 70, "<b>SA1</b> SFT 225<br>перемикач I–0–II, 25 А<br>I – мережа / II – зарядна станція", SW)

p.edge(grid, qf1); p.edge(qf1, kv); p.edge(kv, rcd)
p.edge(rcd, sa, "I")
p.edge(gen, qf2, style=GEN_EDGE); p.edge(qf2, sa, "II", style=GEN_EDGE)

qf3 = p.box(-110, 300, 140, 55, "<b>QF3</b> MCN 210<br>C10, 2P", MCB)
p.edge(rcd, qf3, pts=[(70, 327)])
xs1 = p.box(-110, 400, 140, 55, "<b>XS1</b> SN016<br>розетка щитка<br>(зарядка станції)", "fillColor=#e1d5e7;strokeColor=#9673a6;")
p.edge(qf3, xs1)
p.edge(xs1, gen, style="dashed=1;strokeColor=#9673a6;endArrow=block;", label="заряд", pts=[(-140, 427), (-140, -10), (540, -10)])

bus = p.box(60, 520, 470, 14, "шина L після SA1", BUS)
p.edge(sa, bus)

groups = [("QF4", "MCN 110", "C10", "Світло<br>дитяча"), ("QF5", "MCN 110", "C10", "Світло<br>зала"),
          ("QF6", "MCN 116", "C16", "Розетки<br>дитяча"), ("QF7", "MCN 116", "C16", "Розетки<br>зала"),
          ("QF8", "MCN 120", "C20", "Холодильник (кухня)<br>Кондиціонер (зала)")]
for k, (tag, model, rating, name) in enumerate(groups):
    x = 60 + k * 95
    b = p.box(x, 580, 85, 60, f"<b>{tag}</b> {model}<br>{rating}, 1P", MCB)
    p.edge(bus, b)
    ln = p.box(x, 680, 85, 60, name, "fillColor=none;")
    p.edge(b, ln)

p.box(780, 60, 340, 270,
      "<b>Примітки</b><br>• Два джерела: мережа (положення I) та зарядна станція (положення II), "
      "перемикаються SA1 — паралельна робота неможлива.<br>"
      "• ПЗВ QD1 стоїть лише в колі мережі (до SA1), тому при живленні від станції "
      "групи працюють без ПЗВ.<br>"
      "• XS1 живиться від мережі (через QF3) — для зарядки станції; "
      "точка підключення QF3 (до/після ПЗВ) — уточнити.<br>"
      "• N — через сині шини N, PE — через зелену шину PE (на схемі не показані).", NOTE)

# ---------- Page 2: front-view layout ----------
q = Page("Розміщення в щиті")
q.box(40, 10, 700, 30, "Розміщення апаратів у щиті (вигляд спереду), 1 модуль = 18 мм", TITLE)
q.box(40, 50, 760, 640, "", "fillColor=#fafafa;strokeColor=#666666;strokeWidth=2;rounded=1;arcSize=2;")
# busbars
q.box(60, 70, 120, 40, "Шина N", "fillColor=#9cc3e6;strokeColor=#2f5597;")
q.box(185, 70, 120, 40, "Шина N", "fillColor=#9cc3e6;strokeColor=#2f5597;")
q.box(330, 70, 80, 40, "Клема N", "fillColor=#9cc3e6;strokeColor=#2f5597;")
q.box(430, 70, 350, 40, "Шина PE", "fillColor=#a9d18e;strokeColor=#548235;")

M = 50  # px per module
def row(page, y, items, x0=70, h=150):
    x = x0
    page.box(60, y + h / 2 - 8, 720, 16, "", "fillColor=#bfbfbf;strokeColor=#7f7f7f;")  # DIN rail
    for mods, text, style in items:
        if text:
            page.box(x, y, mods * M, h, text, style + "verticalAlign=middle;")
        x += mods * M

row(q, 160, [
    (2, "<b>QF2</b><br>MBN 210<br>B10", MCB),
    (2, "<b>SA1</b><br>SFT 225<br>25 A<br>I–0–II", SW),
    (2, "<b>QF3</b><br>MCN 210<br>C10", MCB),
    (2, "<b>QD1</b><br>CDA 240D<br>40 A<br>30 мА", RCD),
    (2, "<b>KV1</b><br>ZUBR<br>D2-40red", REL),
    (2, "<b>QF1</b><br>MCN 225<br>C25", MCB),
])
row(q, 420, [
    (3, "<b>XS1</b><br>SN016<br>розетка<br>(зарядка станції)", "fillColor=#e1d5e7;strokeColor=#9673a6;"),
    (1, "<b>QF4</b><br>MCN<br>110<br>C10<br><i>світло дит.</i>", MCB),
    (1, "<b>QF5</b><br>MCN<br>110<br>C10<br><i>світло зала</i>", MCB),
    (1, "<b>QF6</b><br>MCN<br>116<br>C16<br><i>роз. дит.</i>", MCB),
    (1, "<b>QF7</b><br>MCN<br>116<br>C16<br><i>роз. зала</i>", MCB),
    (1, "<b>QF8</b><br>MCN<br>120<br>C20<br><i>холод./конд.</i>", MCB),
    (6, "вільно", "fillColor=none;dashed=1;strokeColor=#999999;fontColor=#999999;"),
])

out = ('<mxfile host="app.diagrams.net" type="device">' + p.xml("sld") + q.xml("layout") + '</mxfile>')
open(sys.argv[1], "w", encoding="utf-8").write(out)
