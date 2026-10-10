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

# ---------- Page 3: wiring diagram (pictorial, Visio-like) ----------
w = Page("Монтажна схема")
w.box(30, -30, 700, 26, "Монтажна схема щита (вигляд спереду, з'єднання — за однолінійною схемою)", TITLE)
w.box(20, 0, 730, 830, "", "fillColor=#ffffff;strokeColor=#999999;strokeWidth=2;rounded=1;arcSize=2;")
T = {}

def term(key, x, y):
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

RED, BLUE, BRN, ORG, PEC = "#e02020", "#1f5fd0", "#8b4513", "#ff8c00", "#4caf50"
def wire(a, b, color, pts=None, extra=""):
    st = f"edgeStyle=none;strokeColor={color};strokeWidth=3;jumpStyle=arc;jumpSize=10;" + extra
    w.edge(a, b, style=st, pts=pts)

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
w.box(30, 600, 640, 20, "", "fillColor=#c8c8c8;strokeColor=#888888;")
w.box(100, 520, 120, 180, "", "rounded=1;arcSize=4;fillColor=#eeeeee;strokeColor=#555555;")
w.box(120, 570, 80, 80, "", "ellipse;shape=ellipse;fillColor=#ffffff;strokeColor=#777777;strokeWidth=2;")
sock = w.box(137, 587, 46, 46, "", "ellipse;shape=ellipse;fillColor=#dddddd;strokeColor=#777777;")
w.box(102, 652, 116, 40, "<b>XS1</b> SN016<br>розетка щита", "fillColor=none;strokeColor=none;fontSize=9;")
term("XS1t1", 140, 540); term("XS1t2", 180, 540)
groups3 = [("QF4", "MCN 110<br>C10"), ("QF5", "MCN 110<br>C10"), ("QF6", "MCN 116<br>C16"),
           ("QF7", "MCN 116<br>C16"), ("QF8", "MCN 120<br>C20")]
for k, (tag, model) in enumerate(groups3):
    device(220 + k * 40, 520, 1, 180, [(tag + "t", 20)], [(tag + "b", 20)], model, tag)

# mains input (right) and station input (top-left)
inL, inN, inPE = pt(740, 150), pt(740, 160), pt(740, 75)
w.box(680, 112, 70, 30, "Мережа<br>230 В", "fillColor=none;strokeColor=none;fontSize=10;fontStyle=1;align=right;")
stL, stN = pt(120, 20), pt(160, 20)
w.box(30, 4, 85, 30, "Від зарядної<br>станції", "fillColor=none;strokeColor=none;fontSize=10;fontStyle=1;align=right;")

wire(inPE, pe, PEC, extra="dashed=1;dashPattern=8 4;")
wire(inL, T["QF1t1"], RED, [(520, 150)])
wire(inN, T["QF1t2"], BLUE, [(560, 160)])
wire(stL, T["QF2t1"], ORG)
wire(stN, T["QF2t2"], BLUE)
# QF1 -> KV1 -> QD1 (via right gap)
wire(T["QF1b1"], T["KV1t1"], RED, [(520, 405), (610, 405), (610, 185), (440, 185)])
wire(T["QF1b2"], T["KV1t2"], BLUE, [(560, 395), (600, 395), (600, 195), (480, 195)])
wire(T["KV1b1"], T["QD1t1"], RED, [(440, 421), (630, 421), (630, 167), (360, 167)])
wire(T["KV1b2"], T["QD1t2"], BLUE, [(480, 413), (620, 413), (620, 176), (400, 176)])
# QD1 -> SA1 position I
wire(T["QD1b1"], T["SA1b2"], RED, [(360, 432), (190, 432)])
wire(T["QD1b2"], T["SA1b6"], BLUE, [(400, 440), (230, 440)])
# QD1 N -> busbar N1 (around the right side)
wire(T["QD1b2"], n1, BLUE, [(400, 448), (645, 448), (645, 105), (380, 105)], "entryX=0.8;entryY=1;")
# QF3 (socket) from mains after RCD
wire(T["QD1b1"], T["QF3t1"], RED, [(360, 456), (60, 456), (60, 125), (280, 125)])
wire(T["QF3t2"], n1, BLUE, extra="entryX=0.2;entryY=1;")
wire(T["QF3b1"], T["XS1t1"], RED, [(280, 480), (140, 480)])
wire(T["QF3b2"], T["XS1t2"], BLUE, [(320, 490), (180, 490)])
# QF8 — mains only
wire(T["QD1b1"], T["QF8t"], RED, [(360, 466), (425, 466), (425, 526), (400, 526)])
# station -> SA1 position II
wire(T["QF2b2"], T["SA1b8"], BLUE, [(160, 400), (250, 400)])
wire(T["QF2b1"], T["SA1b4"], ORG, [(120, 410), (210, 410)])
# SA1 common -> N2 and group comb
wire(T["SA1t5"], n2, BLUE, extra="entryX=0.5;entryY=1;")
wire(T["SA1t1"], T["QF4t"], BRN, [(200, 137), (48, 137), (48, 512), (240, 512)])
for a, b in [("QF4t", "QF5t"), ("QF5t", "QF6t"), ("QF6t", "QF7t")]:
    wire(T[a], T[b], BRN, [(240 + 40 * int(a[2]) - 160, 512), (240 + 40 * int(b[2]) - 160, 512)])

# outgoing lines
loads = [("QF4b", 240, "Світло<br>дитяча", BRN), ("QF5b", 280, "Світло<br>зала", BRN),
         ("QF6b", 320, "Розетки<br>дитяча", BRN), ("QF7b", 360, "Розетки<br>зала", BRN),
         ("QF8b", 400, "Холодильник<br>Кондиціонер", RED)]
for k, (key, x, text, col) in enumerate(loads):
    lab = w.box(x - 19, 740 + (k % 2) * 42, 38, 0, "", "fillColor=none;strokeColor=none;")
    wire(T[key], lab, col, extra="endArrow=block;endFill=1;endSize=4;")
    w.box(x - 30, 742 + (k % 2) * 42, 60, 36, text, "fillColor=none;strokeColor=none;fontSize=9;")
plug = pt(80, 745)
w.edge(sock, plug, style="edgeStyle=none;strokeColor=#bbbbbb;strokeWidth=7;endArrow=block;endFill=1;endSize=3;", pts=[(80, 610)])
w.box(36, 750, 100, 32, "кабель до зарядної<br>станції (заряд)", "fillColor=none;strokeColor=none;fontSize=9;")

# legend
w.box(770, 60, 260, 230,
      "<b>Умовні позначення</b><br>"
      "<font color='#e02020'>━━</font> L — мережа<br>"
      "<font color='#ff8c00'>━━</font> L — зарядна станція<br>"
      "<font color='#8b4513'>━━</font> L — після SA1 (групи QF4–QF7)<br>"
      "<font color='#1f5fd0'>━━</font> N<br>"
      "<font color='#4caf50'>╍╍</font> PE<br><br>"
      "N1 — нейтраль мережі після ПЗВ (QF8, XS1)<br>"
      "N2 — нейтраль після SA1 (QF4–QF7)<br>"
      "PE — до всіх ліній<br><br>"
      "<i>Розташування клем і трасування дротів умовні.</i>", NOTE)

out = ('<mxfile host="app.diagrams.net" type="device">' + p.xml("sld") + q.xml("layout") + w.xml("wiring") + '</mxfile>')
open(sys.argv[1], "w", encoding="utf-8").write(out)
