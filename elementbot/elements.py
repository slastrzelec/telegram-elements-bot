"""Dane 118 pierwiastków: (liczba atomowa, symbol, nazwa polska, nazwa angielska)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Element:
    z: int
    symbol: str
    pl: str
    en: str

    @property
    def careful(self) -> bool:
        """Pierwiastki z małą ilością wiarygodnych źródeł: tryb ostrożny."""
        return self.z >= 99 or self.symbol in {"Pm", "At", "Fr"}

    @property
    def hazardous(self) -> bool:
        return self.symbol in HAZARDOUS


HAZARDOUS = {"U", "Pu", "Po", "Tl", "Cd", "Pb", "Be", "Np", "Am", "Cm", "Ra", "Th", "Rn", "Hg", "As"}

_RAW = """
1 H wodór hydrogen
2 He hel helium
3 Li lit lithium
4 Be beryl beryllium
5 B bor boron
6 C węgiel carbon
7 N azot nitrogen
8 O tlen oxygen
9 F fluor fluorine
10 Ne neon neon
11 Na sód sodium
12 Mg magnez magnesium
13 Al glin aluminium
14 Si krzem silicon
15 P fosfor phosphorus
16 S siarka sulfur
17 Cl chlor chlorine
18 Ar argon argon
19 K potas potassium
20 Ca wapń calcium
21 Sc skand scandium
22 Ti tytan titanium
23 V wanad vanadium
24 Cr chrom chromium
25 Mn mangan manganese
26 Fe żelazo iron
27 Co kobalt cobalt
28 Ni nikiel nickel
29 Cu miedź copper
30 Zn cynk zinc
31 Ga gal gallium
32 Ge german germanium
33 As arsen arsenic
34 Se selen selenium
35 Br brom bromine
36 Kr krypton krypton
37 Rb rubid rubidium
38 Sr stront strontium
39 Y itr yttrium
40 Zr cyrkon zirconium
41 Nb niob niobium
42 Mo molibden molybdenum
43 Tc technet technetium
44 Ru ruten ruthenium
45 Rh rod rhodium
46 Pd pallad palladium
47 Ag srebro silver
48 Cd kadm cadmium
49 In ind indium
50 Sn cyna tin
51 Sb antymon antimony
52 Te tellur tellurium
53 I jod iodine
54 Xe ksenon xenon
55 Cs cez caesium
56 Ba bar barium
57 La lantan lanthanum
58 Ce cer cerium
59 Pr prazeodym praseodymium
60 Nd neodym neodymium
61 Pm promet promethium
62 Sm samar samarium
63 Eu europ europium
64 Gd gadolin gadolinium
65 Tb terb terbium
66 Dy dysproz dysprosium
67 Ho holm holmium
68 Er erb erbium
69 Tm tul thulium
70 Yb iterb ytterbium
71 Lu lutet lutetium
72 Hf hafn hafnium
73 Ta tantal tantalum
74 W wolfram tungsten
75 Re ren rhenium
76 Os osm osmium
77 Ir iryd iridium
78 Pt platyna platinum
79 Au złoto gold
80 Hg rtęć mercury
81 Tl tal thallium
82 Pb ołów lead
83 Bi bizmut bismuth
84 Po polon polonium
85 At astat astatine
86 Rn radon radon
87 Fr frans francium
88 Ra rad radium
89 Ac aktyn actinium
90 Th tor thorium
91 Pa protaktyn protactinium
92 U uran uranium
93 Np neptun neptunium
94 Pu pluton plutonium
95 Am ameryk americium
96 Cm kiur curium
97 Bk berkel berkelium
98 Cf kaliforn californium
99 Es einstein einsteinium
100 Fm ferm fermium
101 Md mendelew mendelevium
102 No nobel nobelium
103 Lr lorens lawrencium
104 Rf rutherford rutherfordium
105 Db dubn dubnium
106 Sg seaborg seaborgium
107 Bh bohr bohrium
108 Hs has hassium
109 Mt meitner meitnerium
110 Ds darmstadt darmstadtium
111 Rg roentgen roentgenium
112 Cn kopernik copernicium
113 Nh nihon nihonium
114 Fl flerow flerovium
115 Mc moskow moscovium
116 Lv liwermor livermorium
117 Ts tenes tennessine
118 Og oganeson oganesson
"""

ELEMENTS: list[Element] = [
    Element(int(z), sym, pl, en)
    for z, sym, pl, en in (line.split() for line in _RAW.strip().splitlines())
]
