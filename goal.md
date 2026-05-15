# Formål

Formålet er at gøre det let at lave et Python-script, som genererer figurer til et kursusmateriale, ved at lave et begrænset sæt af figurer som funktioner.

## Afgrænsning

- Vi vil ikke lave figurer, vi ikke kan se en konkret anvendelse af.
- Perfektion er fjenden. Det skal ikke være fint, det skal være færdigt.
- Vi skal ikke lave figurer til ting, vi lige så let kan lave med drawsvg's eget bibliotek
- Vi skal ikke lave et nyt "domænesprog". Det nærmeste bliver at lave figurerne så ensartede at bruge, som praktisk muligt.

## Status

- Der er lavet et antal klasser til at repræsenterer de grundlæggende byggesten
- Der er lavet et `Fig`-namespace, som kan lave trivielle figurer
- Der er lavet et omrids af et eksempel

## Koordinatsystem og grid

- Vi holder os til drawsvg's koordinatsystem.
- `x` vokser mod højre.
- `y` vokser nedad.
- "Grid-baseret" betyder et fælles geometrisk målesystem, ikke et automatisk layoutsystem.
- Figurer placeres med eksplicitte koordinater i Python-kode, men koordinaterne må gerne udtrykkes relativt til anchors på andre figurer.
- Alle størrelser og afstande angives i grid-enheder.
- Grid-enheder er abstrakte model-enheder, ikke direkte pixels eller SVG-renderstørrelser.
- Den konkrete rendering skalerer grid-enheder til output-enheder.
- Hver figur har et veldefineret origo i øverste venstre hjørne og en veldefineret størrelse.
- Det skal være let at regne punkter ud direkte ud fra figurens origo og størrelse.
- Figurer skal kunne placeres frit i tegningen uden hensyn til den samlede visuelle balance under opbygningen.
- Når en tegning renderes, beregnes bounds for figurer og connections, og output-canvas tilskæres med en lille margin.
- Halve grid-enheder er acceptable, når det gør forbindelser eller tekstplacering naturlige.
- Typisk er en anchor-celle `1.0 x 1.0`, mens en tekstcelle ofte er bredere, f.eks. `3.0 x 1.0`.
- `Point` er basis for alle koordinater i den offentlige model.
- Løsrevne `x` og `y` bruges kun, når der konstrueres nye punkter, regnes konkret, eller kaldes videre ned i drawsvg.
- Eksempel: Et simpelt objekt kan placeres ved `(10.0, 10.0)` med bredde `3.0` og højde `2.0`.
  Så er top-venstre hjørne `(10.0, 10.0)`, bund `(10.0, 12.0)`, højre side `x = 13.0`, top-midt `(11.5, 10.0)` og bund-midt `(11.5, 12.0)`.

## Aktuelle designvalg

- Figurer udstiller et katalog af navngivne anchors.
- Anchors er steder, hvor det er naturligt at trække forbindelser fra eller til.
- Anchors er `Point`-værdier.
- Forbindelser beskrives direkte som en eksplicit liste af `Point`-koordinater og marker-typer.
- Der er ikke en router. Det er designerens ansvar at vælge den præcise rute.
- Ruter må gerne bygges af anchors, offsets og eksplicitte punktkonstruktioner.
- Hvis forbindelsen skal gå via et sted uden anchor, udtrykkes stedet ad hoc, f.eks. med et offset fra et anchor eller med `Point(...)`.
- Placering af figurer bør så vidt muligt beskrives relativt til andre figurer, når det gør tegningen mere robust og lettere at læse.
- Figurernes geometri skal holdes grid-fast. Et simpelt objekt er `2.0` højt. En symboltabel med tre rækker er `4.0` høj: `1.0` for titel og `1.0` per række.
- Teksthierarkiet er enkelt:
  - `Text` repræsenterer en enkelt tekstlinje.
  - `TextBody` repræsenterer en eller flere tekstlinjer.
  - `TextBody` må konstrueres fra `str`, `Text` eller en sekvens af `str | Text`.
  - `TextBody` normaliserer input til `tuple[Text, ...]` i `__post_init__`.
  - `str` omsættes automatisk til `Text`.
  - `Text` kan være fed, kursiv og venstre-, center- eller højrejusteret.
  - `Text.size` er også en abstrakt, enhedsorienteret størrelse.
  - `Text.size=1.0` betyder normal tekststørrelse, som senere skaleres til konkret rendering.
  - Ved normal størrelse renderes teksten med en højde på ca. `0.4` grid-enheder.
  - Fonten skal være en sans serif, som kan forventes at findes på Ubuntu Linux eller tilsvarende distributioner.
  - Standard font-family er en fallback-kæde med `DejaVu Sans`, `Ubuntu`, `Arial` og `sans-serif`.
  - `TextBody` beregner linjeafstand ud fra den største tekststørrelse blandt linjerne.
  - `Text` og `TextBody` kender ikke feltets størrelse.
  - Placering af venstre-, center- og højrejusteret tekst sker derfor i den figur, der ejer feltets geometri.
  <!-- - Meta-properties som `id`, `rc` og `mark` er mindre.
  - `text_box()` bruger samme tekststørrelse som udgangspunkt, men kan skaleres med `scale=...`.
  - `dict_object()` følger samme idé som `symbol_table()`: keys til venstre, values til højre, og tomme value-felter kan bruges sammen med connectors. -->

## Point, anchors og forbindelser

`Point` er den primære måde at udtrykke koordinater på.
`Offset` er den relative søster til `Point` og repræsenterer en forskydning, ikke et sted.
For at holde brugen let kan man også skrive en forskydning direkte som `(dx, dy)`.

De grundlæggende regler er:

- `Point + Offset -> Point`
- `Point + (dx, dy) -> Point`
- `Point - Offset -> Point`
- `Point - (dx, dy) -> Point`
- `Point - Point -> Offset`
- `Offset + Offset -> Offset`
- `Offset + (dx, dy) -> Offset`
- `Offset * scale -> Offset`

`Point + Point` er ikke en del af modellen, fordi det blander to steder sammen.

Eksempel på en manuel retvinklet forbindelse:

```python
start = obj1.anchors["xxx"]
target = obj2.anchors["yyy"]
bend = start + (2.0, 0.0)

connection = Connection([
    start,
    bend,
    Point(bend.x, target.y),
    target,
])
```

Eksemplet betyder:

- start ved `obj1`'s anchor `xxx`
- gå vandret to grid-enheder mod højre
- gå lodret til samme `y`-værdi som `obj2`'s anchor `yyy`
- gå til sidst direkte til `obj2`'s anchor `yyy`

Det er bevidst, at det tredje punkt skrives som `Point(bend.x, target.y)`.
Det gør det synligt, at punktets `x` kommer fra det første knæk, og punktets `y` kommer fra målet.

Der skal ikke indføres en path-builder eller en orthogonal router for denne type ruter.
Den offentlige model bør hellere have få primitive ting:

- `Point(x, y)`
- `Offset(dx, dy)`
- `point + offset`
- `point + (dx, dy)`
- `figure.anchors[name] -> Point`
- `Connection([point1, point2, ...])`

`Offset` findes for de steder, hvor det gør hensigten tydeligere.
Tuple-formen findes for de små ad hoc-forskydninger, hvor `Offset(...)` ville gøre ruten tungere at læse.

## Box-geometri

`Box` er den grundlæggende tabel-lignende figur.

En `Box` består af:

- en valgfri header
- en body med et antal rækker og kolonner
- et sæt navngivne anchors

Headeren fylder hele boxens bredde.
Hvis `header is None`, bruges headeren ikke og bidrager ikke til boxens højde.
Hvis headeren er en `TextBody`, er den tekstindhold.
Hvis headeren er en `Anchor`, registreres anchor-navnet som et punkt i midten af headerfeltet.

Body består af celler, hvor hver celle kan være:

- `TextBody`
- `Anchor`
- `None`

Hvis en celle er en `Anchor`, registreres anchor-navnet som et punkt i midten af cellen.
Det er dette punkt, der kan bruges i en `Connection`.
Midten beregnes ud fra de faktiske kolonnebredder og rækkehøjder.
Det er vigtigt for figurer som dictionaries, hvor key-kolonnen typisk kan være bredere end value-kolonnen.

Som udgangspunkt er alle body-celler `1.0 x 1.0` grid-enheder.
Cellestørrelser kan sættes med `grid_size=(col_spec, row_spec)`.
Hver spec kan være:

- `None`, som betyder `1.0` for alle kolonner/rækker
- en enkelt `float`, som bruges for alle kolonner/rækker
- en liste/tuple af `float`, som angiver størrelsen for hver kolonne/række

Eksempel:

```python
box = Box(
    10.0,
    20.0,
    header=Anchor("header"),
    grid=[[TextBody("name"), Anchor("value")]],
    grid_size=([2.0, 3.0], 1.5),
)
```

Her bliver boxens bredde `5.0`, body-rækkens højde `1.5`, og headeren bidrager med `header_height`.
`box.anchors["value"]` er midten af anden celle i første række.

Et dictionary-lignende eksempel:

```python
box = Box(
    10.0,
    20.0,
    grid=[
        [TextBody("name"), Anchor("name_value")],
        [TextBody("age"), Anchor("age_value")],
    ],
    grid_size=([3.0, 1.0], [1.0, 2.0]),
)
```

Her ligger value-anchors i anden kolonne.
Deres `x`-koordinat er `10.0 + 3.0 + 1.0 / 2`, fordi key-kolonnen er `3.0` bred og value-kolonnen er `1.0` bred.
Rækkehøjderne bruges tilsvarende til `y`-koordinaterne.

Box registrerer også generelle geometri-anchors:

- `top_left`, `top_center`, `top_right`
- `center_left`, `center`, `center_right`
- `bottom_left`, `bottom_center`, `bottom_right`
- `header_left`, `header_center`, `header_right`, når headeren bruges

Når en `Box` renderes:

- headerfeltet renderes med stroke, hvis headeren bruges
- alle body-felter renderes med stroke, også tomme felter og anchor-felter
- boxens outer border renderes også med stroke
- tekst placeres ud fra feltets faste geometri
- venstrejusteret tekst placeres ved feltets venstre kant plus padding
- højrejusteret tekst placeres ved feltets højre kant minus padding
- centreret tekst placeres ved feltets midterlinje
- tekst må ikke placeres ved individuel bounding-box-centrering, fordi venstrejusterede tekster så kan hoppe afhængigt af tekstens egen bredde

## Drawing-geometri

`Drawing` er containeren for en færdig tegning.
Den indeholder en ordnet liste af figurer og connections.
Placering og routing er stadig designerens ansvar.

`Drawing` er selvdimensionerende ved render-time:

- bounds beregnes ud fra alle figurers `x`, `y`, `xr` og `yb`
- bounds beregnes også ud fra alle punkter i alle connections
- output-canvas får `origin=(x_min - margin, y_min - margin)`
- output-canvas får bredde og højde svarende til indholdets bounds plus margin på begge sider
- default margin er `1.0` grid-enhed
- default baggrund er hvid, så SVG'er er læsbare i mørke viewers
- transparent baggrund kan vælges med `background=None`
- viewBox/canvas-koordinater holdes i grid-enheder
- konkret output-størrelse beregnes med `scale`, hvor `scale` angiver hvor mange render-enheder en grid-enhed svarer til
- default `scale` er `100.0`

`Drawing` skal ikke flytte figurer eller routes.
Den tilpasser kun output-canvas til det eksisterende indhold.

## CLI-helper

Eksempelscripts skal kunne slutte med et enkelt kald som:

```python
px.cli.render(drawing)
```

Default-navnet på outputfilerne kommer fra scriptets filnavn.
Et script med navnet `example_001.py` skriver derfor som udgangspunkt:

- `example_001.png`
- `example_001.svg`

CLI-helperen skal være egnet til Makefile-rules og understøtte de mest basale overrides:

- `--name`, som vælger output-basename
- `--destdir`, som vælger output-directory
- `--png` / `--no-png`
- `--svg` / `--no-svg`
- `--scale`, som sætter `Drawing.scale`

Hvis både PNG og SVG slås fra, er det en fejl.

## Følgende vides at være relevante:

* En symboltabel for et namespace:
    - To kolonner, en til symbolet (navnet) og en til objektet.
    - Objektet skal kunne vises som bare en værdi, når tabellen skal være kompakt
    - Objektet skal kunne vises som en reference (pil) til en objekt-figur
    - Objektet skal kunne udelades
    - Over tabellen skal stå navnet eller beskrivelsen på det namespace symboltabellen repræsenterer: "math", "__main__ (Global)", "local"
    - Symboltabellen skal kunne "ghostes", hvis den ikke længere er tilgængelig eller er gledet ud af scope.
    - Den skal være nem at oprette som `Fig.symbol_table(...)`.
    - Den bruger spidse hjørner.

* Et simpelt objekt:
    - En kasse med runde hjørner.
    - Todelt, hvor typen står i den øverste halvdel ("int", "str", "bool") og værdien står i den nederste del ("42", "Apples", "True")
    - Det skal være muligt at vise et felt for reference count og marked i forbindelse med mark/sweep garbage collection
    - Det skal være muligt at vise et felt for id

* En liste/tuple:
    - Det samme som det simple objekt, bortset fra, at i stedet for værdien er en vandret rækkke af felter (med streger i mellem)
    - Værdier skal enten kunne vises en simpel streng ("Andrew", "Ben", "Charlie"), eller som en reference (pil) til et andet objekt

* En dictionary:
    - Det samme som det simple objekt, bortset fra, at i stedet for værdien er en lodret tabel med keys til venstre og værdier til højre
    - Værdier skal enten kunne vises en simpel streng ("Andrew", "54", "1.82"), eller som en reference (pil) til et andet objekt
    - Den skal være nem at oprette som `Fig.dict_box(...)`.
    - Den bruger tydeligt runde hjørner, aktuelt radius `0.3` grid-enheder.

* En class:
    - Det samme som det simple objekt, bortset fra, at i stedet for værdien er der to kasser: en liste af attributter og en liste af metoder.
    - Størrelsen af de to kasser kan skaleres, så kassen med attributter er 2 grid-enheder, og kassen med metoder er 3 grid-enheder
    - Det er op til en selv at sikre sig, at teksten kan være i kassen.


* En forbindelse:
    - Et antal linjer forbundet mellem et variabelt antal `Point`-koordinater
    - Ruten angives eksplicit af designeren.
    - Ruten kan bygges ud fra anchors, offsets og konkrete `Point(...)`-udtryk.
    - Rendering er en simpel polyline med stroke.
    - For hver ende kan vælges et antal pilehoveder:
        - Ingen pil
        - Lukket cirkel/dot
        - Smalt åbent pilehoved
        - Smalt lukket/fyldt pilehoved
        - Smalt lukket pilehoved (reference til)
        - Lukket cirkel (reference fra)
        - Bredt lukket pilehoved (arve-relation)
        - Bredt åbent pilehoved (namespace søgning)
    - De første konkrete marker-typer er implementeret nu: `DOT`, `NARROW`, `NARROW_FILLED`.
    - De øvrige marker-typer er reserveret i enum'en og skal implementeres senere.

* En generel tekstboks:
    - En kasse med spidse eller runde hjørner
    - En liste af tekstlinjer, der skal være i kassen

* En generel tabel:
    - En kasse med spidse eller runde hjørner
    - Et et antal rækker og kolonner
    - En dictionary af (x, y) tupler associeret med liste af tekstlinjer, der skal være i felterne:
```python
text = {
    (0, 0): ["This", "That"],
    (1, 0): ["Other", "Text"],
    (0, 1): ["Lower", "Left"],
    (1, 1): ["Right", "Corner"],
}
```
    - Ellers som generel tekstboks


* Generelt:
    - Alle figurer er grid-baserede, så det er let at vide, hvor man kan tegne pilene fra og til
    - Alle figurer har origo i øverste venstre hjørne
    - Alle længder er grid-baserede, så et simpelt objekt kan være 2.0 højt og have en bredde på f.eks. 3.0
    - En pil kan gå til en figur ved direkte `Point`-koordinater, udregnet ud fra figurens origo, størrelse og anchors
    - Placering af figurer under opbygningen og tilskæring af den færdige tegning er to separate trin
    - Det skal være let at lade en pil gå fra midt i et felt i en symboltabel eller en værdi i en liste
    - Tekst skal primært være i samme størrelse.

## Seneste ændringer

- Geometrien er ændret til `x`, `y`, `w` og `h`.
- Der er properties for `xr = x + w` og `yb = y + h`.
- Parametre, der har med geometri at gøre, står forrest i de offentlige figurfunktioner.
- `symbol_table()` har default `w=4.0`.
- `symbol_table(name_col_width=None)` betyder `name_col_width = w - 1`.
- `simple_object()` har default `w=3.0`.

## Måske ...

- Hver af de nævnte objekter (bortset fra forbindelser) er specialisering af tabeller af tekst med en header.
- Måske skulle de generaliseres til en generisk basisklasse, og de navngivne typer er bare applikeringer
- Hvis det er rigtigt, kan en klasse-baseret model med nedarvning være mere naturlig end flere og flere metoder på `Scene`.
- Det kunne også åbne for naturlige kombinationer som:
  - lodret liste
  - vandret dict/mapping
  - klassefigur som `header + 1*2` felter med multiline-indhold for hhv. attributter og metoder

## Ikke afklaret eller inkonsistent

Dette dokument er delvist overtaget fra et tidligere projekt.
Følgende punkter er ikke nødvendigvis konsistente med de aktuelle designvalg:

- Den primære offentlige konstruktionsform er `Fig` som namespace for konkrete figurbyggere.
  `Factory` kan findes som kompatibilitetsalias, men har ikke selvstændig designmæssig betydning.
- Dokumentet nævner `x`, `y`, `w` og `h` som geometri.
  Det aktuelle design ønsker samtidig, at `Point` er basis for koordinater.
  En mulig løsning er, at en figurs origo er et `Point`, men at `x`, `y`, `w` og `h` stadig findes som bekvemme properties.
- Dokumentet nævner properties for `xr = x + w` og `yb = y + h`.
  Det er ikke besluttet, om de skal returnere rå tal, eller om flere afledte steder skal returneres som `Point`-anchors.
- `Offset` findes nu som en selvstændig relativ koordinattype, men `(dx, dy)` er stadig accepteret som en bekvem ad hoc-forskydning.
- Det er ikke afklaret, om `anchors` skal være et offentligt dictionary-felt, en metode som `anchor(name)`, eller begge dele.
- Det er ikke afklaret, hvor meget `drawsvg` skal skjules.
  Intentionen er, at brugeren tænker i pixbox-figurer og `Point`s, men implementationen må gerne være tæt på drawsvg.
- Det er ikke afklaret, om generelle tabeller skal være den interne basismodel for symboltabeller, lister, dicts, classes og simple objekter.
- Det er stadig designerens ansvar, at tekst kan være i felterne, og at figurer og forbindelser ikke overlapper uhensigtsmæssigt.
  Projektet skal ikke forsøge at løse dette med automatisk layout.
