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
        st = "rounded=0;whiteSpace=wrap;html=1;fontSize=11;fontColor=#000000;" + style
        self.cells.append(f'<mxCell id="{i}" value="{escape(text, {chr(34): "&quot;"})}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def edge(self, a, b, label="", style="", pts=None):
        i = self._id()
        st = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeWidth=2;strokeColor=#000000;fontSize=12;fontStyle=1;labelBackgroundColor=#ffffff;" + style
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
SRC = "ellipse;shape=ellipse;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;"
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
sa  = p.box(250, 420, 200, 70, "<b>SA1</b> SFT 225<br>перемикач I–0–II, 25 А<br>I – мережа / II – зарядна станція", SW)

p.edge(grid, qf1); p.edge(qf1, kv); p.edge(kv, rcd)
mbus = p.box(-280, 380, 520, 14, "шина L мережі (після QD1)", BUS)
p.edge(rcd, mbus, style="exitX=0.5;exitY=1;entryX=0.865;entryY=0;")
p.edge(mbus, sa, "I", style="exitX=1;exitY=0.5;entryX=0.25;entryY=0;", pts=[(300, 387)])
p.edge(gen, qf2, style=GEN_EDGE); p.edge(qf2, sa, "II", style=GEN_EDGE + "exitX=0.5;exitY=1;entryX=0.75;entryY=0;", pts=[(540, 395), (400, 395)])

qf3 = p.box(-110, 430, 140, 55, "<b>QF3</b> MCN 210<br>C10, 2P", MCB)
p.edge(mbus, qf3, style="exitX=0.4615;exitY=1;entryX=0.5;entryY=0;")
xs1 = p.box(-110, 520, 140, 55, "<b>XS1</b> SN016<br>розетка щитка<br>(зарядка станції)", "fillColor=#e1d5e7;strokeColor=#9673a6;")
p.edge(qf3, xs1)
p.edge(xs1, gen, style="dashed=1;strokeColor=#9673a6;endArrow=block;", label="заряд", pts=[(-40, 790), (660, 790), (660, 75)])
qf8 = p.box(-270, 430, 140, 55, "<b>QF8</b> MCN 120<br>C20, 1P", MCB)
p.edge(mbus, qf8, style="exitX=0.154;exitY=1;entryX=0.5;entryY=0;")
l8 = p.box(-270, 520, 140, 55, "Холодильник (кухня)<br>Кондиціонер (зала)<br><i>лише від мережі</i>", "fillColor=none;")
p.edge(qf8, l8)

bus = p.box(60, 520, 470, 14, "шина L після SA1 (мережа або станція)", BUS)
p.edge(sa, bus, style="exitX=0.5;exitY=1;entryX=0.617;entryY=0;")

groups = [("QF4", "MCN 110", "C10", "Світло<br>дитяча"), ("QF5", "MCN 110", "C10", "Світло<br>зала"),
          ("QF6", "MCN 116", "C16", "Розетки<br>дитяча"), ("QF7", "MCN 116", "C16", "Розетки<br>зала")]
for k, (tag, model, rating, name) in enumerate(groups):
    x = 60 + k * 95
    b = p.box(x, 580, 85, 60, f"<b>{tag}</b> {model}<br>{rating}, 1P", MCB)
    p.edge(bus, b, style=f"exitX={(x + 42.5 - 60) / 470:.4f};exitY=1;entryX=0.5;entryY=0;")
    ln = p.box(x, 680, 85, 60, name, "fillColor=none;")
    p.edge(b, ln)

p.box(780, 60, 340, 150,
      "<b>Примітки</b><br>• Два джерела: мережа (положення I) та зарядна станція (положення II), "
      "перемикаються SA1 — паралельна робота неможлива.<br>"
      "• ПЗВ QD1 стоїть лише в колі мережі (до SA1), тому при живленні від станції "
      "групи QF4–QF7 працюють без ПЗВ.<br>"
      "• QF8 (холодильник, кондиціонер) і QF3 живляться лише від мережі — до SA1.<br>"
      "• QF3 (розетка XS1 для зарядки станції) — після ПЗВ; положення I перемикача SA1 живиться перемичкою від вхідних клем QF3.<br>"
      "• N — через сині шини N, PE — через зелену шину PE (на схемі не показані).<br>"
      "• Внутрішня комутація щита — ПВ3 4 мм².", NOTE)

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

# ---------- Page 3: wiring diagram (pictorial, Visio-like) ----------
w = Page("Монтажна схема")
w.box(30, -30, 700, 26, "Монтажна схема щита (вигляд спереду, з'єднання — за однолінійною схемою)", TITLE)
w.box(20, 0, 730, 830, "", "fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;rounded=1;arcSize=2;")
T = {}

TP = {}
def term(key, x, y):
    TP[key] = (x, y)
    T[key] = w.box(x - 7, y - 7, 14, 14, "", "ellipse;shape=ellipse;fillColor=#ffffff;strokeColor=#444444;strokeWidth=1.5;")

def device(x, y, mods, h, tops, bots, model, tag, note="", kind="mcb"):
    wd = mods * 40
    w.box(x, y, wd, h, "", "rounded=1;arcSize=4;fillColor=#eeeeee;strokeColor=#555555;")
    w.box(x + 3, y + 40, wd - 6, 4, "", "fillColor=#1f6fb5;strokeColor=none;")
    w.box(x + 3, y + 46, wd - 6, 28, model, "fillColor=#ffffff;strokeColor=none;fontSize=8;verticalAlign=top;spacing=1;")
    if kind == "zubr":
        w.box(x + 8, y + 80, wd - 16, 34, "243 V", "fillColor=#111111;strokeColor=none;fontColor=#ff3333;fontSize=16;fontStyle=1;")
        w.box(x + 8, y + 118, wd - 16, 16, "–  +  ≡  i", "fillColor=#ffffff;strokeColor=#999999;fontSize=9;rounded=1;")
    elif kind == "switch":
        w.box(x + 6, y + 82, wd - 12, 34, "I – 0 – II", "fillColor=#ffffff;strokeColor=#777777;fontSize=11;fontStyle=1;")
    else:
        w.box(x + wd * 0.2, y + 82, wd * 0.6, 40, "", "fillColor=#777777;strokeColor=#444444;rounded=1;")
        if kind == "rcd":
            w.box(x + wd - 20, y + 124, 14, 12, "T", "fillColor=#3a74c4;strokeColor=none;fontColor=#ffffff;fontSize=8;fontStyle=1;")
    w.box(x + 2, y + h - 66, wd - 4, 38, f"<b>{tag}</b><br>{note}", "fillColor=none;strokeColor=none;fontSize=9;")
    for k, tx in tops:
        term(k, x + tx, y + 20)
    for k, tx in bots:
        term(k, x + tx, y + h - 20)

def bar(x, y, wd, label, fill):
    return w.box(x, y, wd, 30, label, f"fillColor={fill};strokeColor=#555555;fontSize=10;fontStyle=1;")

def pt(x, y):
    return w.box(x - 1, y - 1, 2, 2, "", "fillColor=none;strokeColor=none;")


# busbars
n2 = bar(190, 60, 100, "N2 (після SA1)", "#9cc3e6")
n1 = bar(300, 60, 100, "N1 (мережа)", "#9cc3e6")
pe = bar(600, 60, 110, "PE", "#a9d18e")

# top rail
w.box(30, 290, 640, 20, "", "fillColor=#c8c8c8;strokeColor=#888888;")
device(100, 200, 2, 200, [("QF2t1", 20), ("QF2t2", 60)], [("QF2b1", 20), ("QF2b2", 60)], "MBN 210<br>B10", "QF2", "ввід від станції")
device(180, 200, 2, 200, [("SA1t1", 20), ("SA1t5", 60)], [("SA1b2", 10), ("SA1b4", 30), ("SA1b6", 50), ("SA1b8", 70)], "SFT 225<br>25 A", "SA1", "I мережа<br>II станція", kind="switch")
device(260, 200, 2, 200, [("QF3t1", 20), ("QF3t2", 60)], [("QF3b1", 20), ("QF3b2", 60)], "MCN 210<br>C10", "QF3", "розетка щита")
device(340, 200, 2, 200, [("QD1t1", 20), ("QD1t2", 60)], [("QD1b1", 20), ("QD1b2", 60)], "CDA 240D<br>40 A / 30 mA", "QD1", "ПЗВ", kind="rcd")
device(420, 200, 2, 200, [("KV1t1", 20), ("KV1t2", 60)], [("KV1b1", 20), ("KV1b2", 60)], "ZUBR D2-40", "KV1", "реле напруги", kind="zubr")
device(500, 200, 2, 200, [("QF1t1", 20), ("QF1t2", 60)], [("QF1b1", 20), ("QF1b2", 60)], "MCN 225<br>C25", "QF1", "вступний")

# bottom rail
w.box(30, 640, 640, 20, "", "fillColor=#c8c8c8;strokeColor=#888888;")
w.box(100, 560, 120, 180, "", "rounded=1;arcSize=4;fillColor=#eeeeee;strokeColor=#555555;")
w.box(120, 610, 80, 80, "", "ellipse;shape=ellipse;fillColor=#ffffff;strokeColor=#777777;strokeWidth=2;")
sock = w.box(137, 627, 46, 46, "", "ellipse;shape=ellipse;fillColor=#dddddd;strokeColor=#777777;")
w.box(102, 692, 116, 40, "<b>XS1</b> SN016<br>розетка щита", "fillColor=none;strokeColor=none;fontSize=9;")
term("XS1t1", 140, 580); term("XS1t2", 180, 580)
groups3 = [("QF4", "MCN 110<br>C10"), ("QF5", "MCN 110<br>C10"), ("QF6", "MCN 116<br>C16"),
           ("QF7", "MCN 116<br>C16"), ("QF8", "MCN 120<br>C20")]
for k, (tag, model) in enumerate(groups3):
    device(220 + k * 40, 560, 1, 180, [(tag + "t", 20)], [(tag + "b", 20)], model, tag)

RED, BLUE, BRN, ORG, PEC = "#e02020", "#1f5fd0", "#8b4513", "#ff8c00", "#4caf50"

def vline(x, y1, y2, color, width=5):
    w.box(x - width / 2, min(y1, y2), width, abs(y2 - y1), "", f"fillColor={color};strokeColor=none;")

def ferrule(x, y, twin=False):
    d = 7 if twin else 4
    w.box(x - d, y, 2 * d, 9, "", "fillColor=#ffa31a;strokeColor=#b36b00;")

def marker(x, y, text, color):
    n = text.count("<br>") + 1
    w.box(x - 9, y, 18, 13 * n + 2, text,
          f"fillColor=#ffffff;strokeColor={color};strokeWidth=2;fontSize=9;fontStyle=1;spacing=0;rounded=1;arcSize=20;")

def stub(key, text, color, length=28, up=False):
    """Wire end with ferrule and numbered marker; the rest of the wire runs hidden behind the devices."""
    x, y = TP[key]
    h = 13 * (text.count("<br>") + 1) + 2
    twin = "<br>" in text   # two wires in one twin ferrule
    y1, y2 = (y - 7 - length, y - 7) if up else (y + 7, y + 7 + length)
    if twin:
        vline(x - 3, y1, y2, color, 3); vline(x + 3, y1, y2, color, 3)
    else:
        vline(x, y1, y2, color)
    ferrule(x, y - 16 if up else y + 7, twin)
    marker(x, y1 - h if up else y2, text, color)

def bar_stub(x, text, color, length=16):
    vline(x, 90, 90 + length, color)
    marker(x, 90 + length, text, color)

# incoming cables (visible, no crossings): mains from top to QF1, station from top to QF2
w.box(490, -2, 100, 28, "Мережа 230 В", "fillColor=none;strokeColor=none;fontSize=10;fontStyle=1;")
w.box(90, -2, 100, 28, "Зарядна станція", "fillColor=none;strokeColor=none;fontSize=10;fontStyle=1;")
for x, col, num in [(520, RED, "1"), (560, BLUE, "2"), (120, ORG, "13"), (160, BLUE, "14")]:
    vline(x, 28, 207, col)
    ferrule(x, 196)
    marker(x, 130, num, col)
w.box(640, -2, 80, 28, "PE ввід", "fillColor=none;strokeColor=none;fontSize=10;fontStyle=1;")
vline(655, 28, 60, PEC)

# numbered wire ends — top row, upper terminals
for key, num, col in [("SA1t1", "17", BRN), ("SA1t5", "18", BLUE), ("QF3t1", "7<br>10", RED), ("QF3t2", "8<br>11", BLUE),
                      ("QD1t1", "5", RED), ("QD1t2", "6", BLUE), ("KV1t1", "3", RED), ("KV1t2", "4", BLUE)]:
    stub(key, num, col, up=True)
# top row, lower terminals
for key, num, col, ln in [("QF2b1", "15", ORG, 28), ("QF2b2", "16", BLUE, 28),
                          ("SA1b2", "7", RED, 18), ("SA1b4", "15", ORG, 46), ("SA1b6", "8", BLUE, 18), ("SA1b8", "16", BLUE, 46),
                          ("QF3b1", "19", RED, 28), ("QF3b2", "20", BLUE, 28),
                          ("QD1b1", "10<br>12", RED, 28), ("QD1b2", "9<br>11", BLUE, 28),
                          ("KV1b1", "5", RED, 28), ("KV1b2", "6", BLUE, 28),
                          ("QF1b1", "3", RED, 28), ("QF1b2", "4", BLUE, 28)]:
    stub(key, num, col, length=ln)
# bottom row: socket feed on top
stub("XS1t1", "19", RED, length=24, up=True)
stub("XS1t2", "20", BLUE, length=24, up=True)
# bottom row: supply from below — wire 17 + comb QF4–QF7, wire 12 to QF8
stub("QF4b", "17", BRN, length=33)
stub("QF8b", "12", RED, length=33)
w.box(240 - 1.5, 748, 120 + 3, 5, "", f"fillColor={BRN};strokeColor=none;")
for x in (280, 320, 360):
    vline(x, 727, 751, BRN)
    ferrule(x, 727)
w.box(256, 756, 110, 16, "гребінка QF4–QF7 (знизу)", "fillColor=none;strokeColor=none;fontSize=8;fontColor=#8b4513;fontStyle=1;")
# busbars
bar_stub(340, "9", BLUE); bar_stub(240, "18", BLUE)

# outgoing lines — from the upper terminals
loads = [(240, "Світло дитяча", BRN), (280, "Світло зала", BRN),
         (320, "Розетки дитяча", BRN), (360, "Розетки зала", BRN),
         (400, "Холод. / кондиц.", RED)]
for x, text, col in loads:
    vline(x, 545, 573, col)
    ferrule(x, 564)
    w.box(x - 9, 463, 18, 84, text, f"horizontal=0;fillColor=#ffffff;strokeColor={col};strokeWidth=2;fontSize=9;fontStyle=1;spacing=0;rounded=1;arcSize=20;")
plug = pt(70, 800)
w.edge(sock, plug, style="edgeStyle=none;strokeColor=#bbbbbb;strokeWidth=7;endArrow=block;endFill=1;endSize=3;", pts=[(70, 650)])
w.box(26, 800, 100, 28, "кабель до зарядної<br>станції (заряд)", "fillColor=none;strokeColor=none;fontSize=9;")

# wire list
rows = [("1", "Мережа L", "QF1:1", RED), ("2", "Мережа N", "QF1:N", BLUE),
        ("3", "QF1:2", "KV1:L вх", RED), ("4", "QF1:N", "KV1:N вх", BLUE),
        ("5", "KV1:L вих", "QD1:1", RED), ("6", "KV1:N вих", "QD1:N", BLUE),
        ("7", "QF3:1 (вхід)", "SA1:2 (I)", RED), ("8", "QF3:N (вхід)", "SA1:6 (I)", BLUE),
        ("9", "QD1:N", "шина N1", BLUE), ("10", "QD1:2", "QF3:1", RED),
        ("11", "QD1:N", "QF3:N", BLUE), ("12", "QD1:2", "QF8 (низ)", RED),
        ("13", "Станція L", "QF2:1", ORG), ("14", "Станція N", "QF2:N", BLUE),
        ("15", "QF2:2", "SA1:4 (II)", ORG), ("16", "QF2:N", "SA1:8 (II)", BLUE),
        ("17", "SA1:1", "QF4 (низ) → гребінка", BRN), ("18", "SA1:5", "шина N2", BLUE),
        ("19", "QF3:2", "XS1 L", RED), ("20", "QF3:N", "XS1 N", BLUE)]
tr = "".join(f"<tr><td align='center' style='border:2px solid {c};font-weight:bold'>{n}</td>"
             f"<td>&nbsp;{a}</td><td>&nbsp;{b}</td></tr>" for n, a, b, c in rows)
w.box(770, 40, 300, 360,
      "<b>Таблиця з'єднань</b><table style='font-size:10px;border-collapse:collapse;margin-top:4px' cellpadding='1'>"
      "<tr><th>№</th><th align='left'>&nbsp;Звідки</th><th align='left'>&nbsp;Куди</th></tr>" + tr + "</table>",
      "fillColor=#ffffff;strokeColor=#999999;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=11;")

# legend
w.box(770, 410, 300, 195,
      "<b>Позначення</b><br>"
      "Дроти прокладені за апаратами (як у щиті); на клемах показано лише маркер з номером дроту — "
      "однаковий номер на обох кінцях. Два номери на одному маркері — два дроти в подвійному наконечнику (НШВІ).<br><br>"
      "<font color='#e02020'>■</font> L мережа &nbsp; <font color='#ff8c00'>■</font> L станція &nbsp; "
      "<font color='#8b4513'>■</font> L після SA1<br><font color='#1f5fd0'>■</font> N &nbsp; "
      "<font color='#4caf50'>■</font> PE<br><br>"
      "Внутрішня комутація — ПВ3 4 мм² (Cu, гнучкий) з НШВІ.<br>"Живлення груп — знизу (гребінка), відхідні лінії — зверху.<br>N груп QF4–QF7 — із шини N2; N холодильника/кондиціонера (QF8) — із шини N1; PE — до всіх ліній.", NOTE)

out = ('<mxfile host="app.diagrams.net" type="device">' + p.xml("sld") + q.xml("layout") + w.xml("wiring") + '</mxfile>')
open(sys.argv[1], "w", encoding="utf-8").write(out)
