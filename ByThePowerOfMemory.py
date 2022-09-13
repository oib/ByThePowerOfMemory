import random
import PySimpleGUI as sg
import time
import csv
import os.path
from os import path
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

def create_layout_game():
    LAYOUT_GAME = [
        [
            # sg.Text("match:"),
            sg.Button(
                "Position [a])", key="position", disabled=True, font=("Ubuntu", 16)
            ),
            sg.Button("Color [s]", key="color", disabled=True, font=("Ubuntu", 16)),
            sg.Button("Shape [d]", key="shape", disabled=True, font=("Ubuntu", 16)),
            sg.Button("Number [f]", key="number", disabled=True, font=("Ubuntu", 16)),
        ],
        [
            sg.Graph(
                canvas_size=(620, 620),
                graph_bottom_left=(-1, -1),
                graph_top_right=(1, 1),
                key="canvas",
                background_color="#bbb",
            )
        ],
        [
            sg.Button("Cancel"),
            sg.Text("0", key="time"),
            sg.Text("Game round: 1/12", key="game_round"),
            sg.Text("hits: 0", key="hits", font=("Ubuntu", 20)),
            sg.Text("fails: 0", key="fails", font=("Ubuntu", 20)),
        ],
    ]
    return sg.Window("ByThePowerOfMemory", layout=LAYOUT_GAME,  finalize=True,  return_keyboard_events=True, use_default_focus=False)

def create_layout_settings():

    LAYOUT_SETTING = [
        [sg.Text("Your name:"), sg.Input(default_text="Write your name here!", key="name", enable_events=True)],
        [
            sg.Text("Select your difficulty level:"),
            sg.Combo(
                values=["Beginner", "Veteran", "Elite", "custom"],
                default_value="xxx",
                key="difficulty",
                enable_events=True,
            ),
        ],
        [
            sg.Text("Select extra probability for nomatch:"),
            sg.Combo(
                values=[0.0, .1, 0.25, .5, .75, .9, 1.0],
                default_value=-99,
                key="nomatch",
                enable_events=True,
                disabled=True,  # if Game.difficulty != "custom" else False,
            ),
        ],
        [
            sg.Text("grid size:"),
            sg.Combo(
                values=["2x2", "3x3", "4x4"],
                # default_value="999x999",
                disabled=True,  # if Game.difficulty != "custom" else False,
                # tooltip="size of playfield",
                key="gridsize",
            ),
        ],
        [
            sg.Text("number of colors:"),
            sg.Combo(
                values=[3, 6, 9, 12],
                # default_value=Game.colorsize,
                disabled=True,  # if Game.difficulty != "custom" else False,
                key="colorsize",
            ),
        ],
        [
            sg.Text("number of shapes:"),
            sg.Combo(
                values=[2, 4, 8],
                # default_value=Game.shapesize,
                disabled=True,  # if Game.difficulty != "custom" else False,
                key="shapesize",
            ),
        ],
        [
            sg.Text("speed (time for each round):"),
            sg.Combo(
                values=(2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0),
                disabled=True,  # if Game.difficulty != "custom" else False,
                # default_value=Game.timesize,
                # resolution=0.5,
                # tick_interval=1.0,
                # orientation="h",
                # size=(30,10),
                key="timesize",
            ),
        ],
        [
            sg.Text("numbers:"),
            sg.Combo(
                values=[2, 3, 4, 5, 6, 7, 8, 9, 10],
                key="numbersize",
                # default_value=Game.numbersize,
                disabled=True,  # if Game.difficulty != "custom" else False,
            ),
        ],
        [sg.Text("Game duration: 60 seconds")],
        [sg.Button("Start", disabled=False),  # if Game.filename is None else False,
         # bind_return_key=True),
         sg.Button("Cancel")],
        [sg.Canvas(key="statboard1"), sg.Canvas(key="statboard2")],
    ]
    return sg.Window("Game Settings", layout=LAYOUT_SETTING)

sg.theme("DarkGreen")


class Game:
    nomatch = 0.5  #chance (betwwen 0 and 1) that a nomatch is allowed
    play = False
    playername = None
    filename = None
    alle_zahlen = [0,1,2,3,4,5,6,7,8,9]
    alle_farben = [
        "red",
        "orange",
        "yellow",
        "blue",
        "aquamarine",
        "cyan",
        "gold",
        "green",
        "pink",
        "purple",
        "brown",
        "grey",
        "white",
    ]
    fieldnames = [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "week",
        "gridsize",
        "shapesize",
        "colorsize",
        "timesize",
        "nomatch",
        "hits",
        "fails",
        "avghittime",
    ]
    rounds = None  # 60/5
    all_shapes = [
        "circle",
        "box",
        "rhombus",
        "pyramide",
        "triangle",
        "arrow_up",
        "arrow_down",
        "tri_r",
        "tri_l",
    ]
    gridsize = "2x2"
    shapesize = 2
    colorsize = 3
    timesize = 5
    numbersize = 10
    difficulty = "Beginner"
    defaults = {
        "Beginner": {
            "gridsize": "2x2",
            "shapesize": 2,
            "colorsize": 3,
            "timesize": 4.0,
            "numbersize": 3,
            "nomatch": 1,
        },
        "Veteran": {
            "gridsize": "3x3",
            "shapesize": 4,
            "colorsize": 6,
            "timesize": 3.0,
            "numbersize": 6,
            "nomatch": 0.5,
        },
        "Elite": {
            "gridsize": "4x4",
            "shapesize": 9,
            "colorsize": 12,
            "timesize": 2.0,
            "numbersize": 10,
            "nomatch": 0.25,
        },
    }


class RoundSet:
    set_farben = []
    set_mitten = []
    set_zahlen = []
    set_shapes = []
    line_width = 3
    line_color = "black"

    def __init__(self):
        self.farbe = random.choice(RoundSet.set_farben)
        self.shape = random.choice(RoundSet.set_shapes)
        self.mitte = random.choice(RoundSet.set_mitten)
        self.zahl = random.choice(RoundSet.set_zahlen)

    def draw(self, widget):
        x,y = self.mitte
        match self.shape:

            case "circle":
                widget.draw_circle(
                    self.mitte,
                    radius=0.5,
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )

            case "box":
                widget.draw_rectangle(
                    top_left=(x - 0.5, y + 0.5),
                    bottom_right=(x + 0.5, y - 0.5),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "pyramide":
                widget.draw_polygon(
                    points=(
                        (x + 0.5, y - 0.5),
                        (x - 0.5, y - 0.5),
                        (x, y + 0.5),
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "triangle":
                widget.draw_polygon(
                    points=(
                        (x + 0.5, y + 0.5),
                        (x - 0.5, y + 0.5),
                        (x, y - 0.5),
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "rhombus":
                widget.draw_polygon(
                    points=(
                        (x, y + 0.5),
                        (x - 0.5, y),
                        (x, y - 0.5),
                        (x + 0.5, y),
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "arrow_up":
                widget.draw_polygon(
                    points=(
                        (x, y + 0.5),
                        (x - 0.5, y),
                        (x - 0.25, y),
                        (x - 0.25, y - 0.5),
                        (x, y - 0.25),
                        (x + 0.25, y - 0.5),
                        (x + 0.25, y),
                        (x + 0.5, y),
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "tri_r":
                widget.draw_polygon(
                    points=(
                        (x - .5, y + .5),
                        (x + .5, y),
                        (x - .5, y - .5)
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "tri_l":
                widget.draw_polygon(
                    points=(
                        (x - .5, y),
                        (x + .5, y + .5),
                        (x + .5, y - .5)
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
            case "arrow_down":
                widget.draw_polygon(
                    points=(
                        (x, y + 0.25),
                        (x + .25, y + .5),
                        (x + .25, y - .25),
                        (x + .5, y - .25),
                        (x, y - .5),
                        (x - .5, y - .25),
                        (x - .25, y - .25),
                        (x - .25, y + .5)
                    ),
                    fill_color=self.farbe,
                    line_color=RoundSet.line_color,
                    line_width=RoundSet.line_width,
                )
        # ---- draw the number inside the shape ------
        widget.draw_text(
            str(self.zahl), location=self.mitte, font=("Arial", 20, "bold")
        )


def statistic():
    hits = []
    times = []
    weeks = []
    if Game.playername is None:
        return
    if not path.exists(Game.filename):
        sg.popup_error("no stats exists now")
        return
    with open(Game.filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        number_of_lines = 0
        for row in reader:
            number_of_lines +=1
            # print(row)
            hits.append(float("{:.2f}".format(float(row["hits"]))))
            times.append(
                "{}-{}-{} {}:{}".format(
                    row["year"], row["month"], row["day"], row["hour"], row["minute"]
                )
            )
        #----- we only want the last 7 games
        if len(hits)> 7:
            hits = hits[-7:]
            times = times[-7:]


    fig, ax = plt.subplots(figsize=(5, 4), layout="constrained")
    #runden = list(range(1, len(times) + 1))

    ax.bar(times, hits)
    if number_of_lines != 0:
        ax.annotate(
            "This Game",
            xy=(times[-1], 80),
            xytext=(-100, -50),  # xytext=(times[len(times)//2], 50),
            textcoords="offset pixels",
            arrowprops=dict(
                facecolor="black",
                shrink=0.2,
            ),
        )
    ax.set_title("Your last (7) Games")
    ax.set_xlabel("Date of Game")
    ax.set_ylabel("Score in %")
    plt.setp(ax.get_xticklabels(), rotation=50, ha="right")

    # plt.show()
    return fig

def statistic_week():
    data = []
    weeknumbers = []
    if Game.playername is None:
        return
    if not path.exists(Game.filename):
        sg.popup_error("no stats exists now")
        return
    with open(Game.filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print(row)
            score = float("{:.2f}".format(float(row["hits"])))
            week = "{:02}".format(row["week"])
            if week not in weeknumbers:
                weeknumbers.append(week)
            data.append([week, score])
    #### pandas group by week
    #df = pd.DataFrame(data)
    #y_values = []
    #x_values = []
    datapoints = {}
    for (week, score) in data:
        if week in datapoints:
            datapoints[week].append(score)
        else:
            datapoints[week] = []
            datapoints[week].append(score)
    averages = {}
    for week in datapoints.keys():
        averages[week]= sum(datapoints[week])/len(datapoints[week])

    x_values = weeknumbers
    y_values = [averages[week] for week in weeknumbers]

    fig, ax = plt.subplots(figsize=(5, 4), layout="constrained")
    ax.bar(x_values,y_values)
    ax.set_title("Your weekly Scores")
    ax.set_xlabel("Week")
    ax.set_ylabel("Average Score in %")
    #plt.setp(ax.get_xticklabels(), rotation=50, ha="right")
    return fig


def settings():
    #local_layout = LAYOUT_SETTING[:]
    #window = sg.Window(layout=local_layout, title="Settings for Memory Game")
    window = create_layout_settings()
    window.finalize()
    # set up disabled attributes
    window["name"].update(value=Game.playername)
    window["difficulty"].update(value=Game.difficulty)
    window["nomatch"].update(value=Game.nomatch)
    window["gridsize"].update(value=Game.gridsize)
    window["colorsize"].update(value=Game.colorsize)
    window["shapesize"].update(value=Game.shapesize)
    window["timesize"].update(value=Game.timesize)
    window["numbersize"].update(value=Game.numbersize)
    window["nomatch"].update(disabled=True if Game.difficulty != "custom" else False)
    window["gridsize"].update(disabled=True if Game.difficulty != "custom" else False)
    window["colorsize"].update(disabled=True if Game.difficulty != "custom" else False)
    window["shapesize"].update(disabled=True if Game.difficulty != "custom" else False)
    window["timesize"].update(disabled=True if Game.difficulty != "custom" else False)
    window["numbersize"].update(disabled=True if Game.difficulty != "custom" else False)

   # play = False
    if Game.playername is not None:
        #        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        #        t = np.arange(0, 3, .01)
        #        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        fig1 = statistic()
        fig2 = statistic_week()
        draw_figure(window["statboard1"].TKCanvas, fig1)
        draw_figure(window["statboard2"].TKCanvas, fig2)
    while True:
        event, values = window.read()
        if event in ("Cancel", sg.WINDOW_CLOSED):
            Game.play = False
            break
        if event == "name":
        #
        #    #if len(values["name"].strip()) > 0:
        #    #    window["Start"].update(disabled=False)
        #    #else:
        #    #    window["Start"].update(disabled=True)
            validname = ""
            for char in values["name"]:
                if char.isalnum():
                    print(char, end='')
                    validname += char
            window["name"].update(validname)
            print("validname:", validname)
            if len(validname) > 0:
                window["Start"].update(disabled=False)
            else:
                window["Start"].update(disabled=True)

        if event == "Start":
            validname = ""
            for char in values["name"]:
                if char.isalnum():
                    print(char, end='')
                    validname += char
            print("validname (from start button:", validname)
            if len(validname) == 0:
                sg.PopupError(f"name must be a vaild filename, not {values['name']}")
                continue

           # play = True
            Game.play = True
            Game.difficulty = values["difficulty"]
            Game.gridsize = values["gridsize"]
            Game.colorsize = values["colorsize"]
            Game.shapesize = values["shapesize"]
            Game.timesize = values["timesize"]
            Game.numbersize = values["numbersize"]
            Game.nomatch = values["nomatch"]
            # print("values:", values["timesize"], values["colorsize"])
            break
        if event == "difficulty":
            d = values["difficulty"]
            for k in ("gridsize", "colorsize", "shapesize", "timesize", "numbersize", "nomatch"):
                if d == "custom":
                    window[k].update(disabled=False)
                else:
                    if k == "gridsize":
                        window[k].update(disabled=True, value=Game.defaults[d][k])
                    elif k == "timesize":
                        window[k].update(disabled=True, value=float(Game.defaults[d][k])) # TODO float() ?
                    else:
                        window[k].update(disabled=True, value=int(Game.defaults[d][k]))
    # try:
    # print("timesize, colorsize values:", values["timesize"], values["colorsize"])

    Game.rounds = int(60 / float(values["timesize"]))
    Game.playername = values["name"]
    # except:
    # print("konnte auf values nicht mehr zugreifen----")
    window.close()


    Game.filename = "{}_{}_{}_{}_{}_{}.csv".format(Game.playername,
                                       Game.gridsize,
                                        Game.colorsize,
                                        Game.timesize,
                                        Game.numbersize,
                                        Game.nomatch)

    if not path.exists(Game.filename):
        with open(Game.filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=Game.fieldnames)
            writer.writeheader()
    return #play


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def calculate_grid():
    match Game.gridsize:
        case "2x2":
            RoundSet.set_mitten = ((-0.5, 0.5), (0.5, 0.5), (-0.5, -0.5), (-0.5, 0.5))
            bl = (-1.5, -1.5)  # bl = bottom_left
            tr = (1.5, 1.5)  # tr = top_right
        case "4x4":
            RoundSet.set_mitten = (
                (-1.5, 1.5),
                (-0.5, 1.5),
                (0.5, 1.5),
                (1.5, 1.5),
                (-1.5, 0.5),
                (-0.5, 0.5),
                (0.5, 0.5),
                (1.5, 0.5),
                (-1.5, -0.5),
                (-0.5, -0.5),
                (0.5, -0.5),
                (1.5, -0.5),
                (1.5, -1.5),
                (-0.5, -1.5),
                (0.5, -1.5),
                (1.5, -1.5),
            )
            bl = (-2.5, -2.5)
            tr = (2.5, 2.5)
        case "3x3":
            RoundSet.set_mitten = (
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 0),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            )
            bl = (-2, -2)
            tr = (2, 2)
    return bl, tr

def game():
    #local_layout = LAYOUT_GAME[:]
    # create valid colors for this game
    random.shuffle(Game.alle_farben)
    RoundSet.set_farben = Game.alle_farben[: Game.colorsize]
    # create valid numbers for this game
    random.shuffle(Game.alle_zahlen)
    RoundSet.set_zahlen = Game.alle_zahlen[: Game.numbersize]
    # create valid shapes for this game
    random.shuffle(Game.all_shapes)
    RoundSet.set_shapes = Game.all_shapes[: int(Game.shapesize)]
    bl, tr = calculate_grid() # set RoundSet.set_mitten

    # -----------------------------------
    # Create the Window
    #window = sg.Window(
    #    "Memory Trainer",
    #    layout=local_layout,
    #    finalize=True,
    #    return_keyboard_events=True,
    #    use_default_focus=False,
    #)
    window = create_layout_game()
    window["canvas"].change_coordinates(bl, tr)
    # Event Loop to process "events" and get the "values" of the inputs
    #stoppuhr = time.time()
    #print(Game.timesize,type(Game.timesize)),
    Game.timesize = float(Game.timesize)
    moment = time.time() - Game.timesize
    anzeigedauer = 0
    # phase = 2
    farbe1 = None
    shape1 = None
    mitte1 = None
    number1 = None
    myset = None
    #farbe = None
    #shape = None
    #number = None
    #mitte = None
    hits = 0
    fails = 0
    max_punkte = 0
    performance_hit = {}
    performance_fail = {}

    game_round = 0
    while game_round <= Game.rounds:
        event, values = window.read(timeout=10)
        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break
        # keyboard event
        if ":" in event:
            print(event)
        if event == sg.EVENT_TIMEOUT:
            anzeigedauer = time.time() - moment
            window["game_round"].update(f"Game round: {game_round}/{Game.rounds}")
            window["time"].update(f"{anzeigedauer:.2f} Sekunden")
            # anzeigedauer += 0.1
            window["hits"].update(f"hits: {hits}")
            window["fails"].update(f"fails: {fails}")
            # ------ grauwert für canvas hintegrund ändern in Abhängigkeit von anzeigedauer
            # anzeigedauer ist ein wert zwischen 0 und Game.timesize (5) sekunden
            # mein grauwert soll schwanken zwischen 64 - 191
            # grau prozent = prozent wieveil zeit der maximalen anzeigdauer (Game.timesize) schon vergangen sind
            anzeigedauerprozent = (
                anzeigedauer / Game.timesize
            )  ## ergibt einen wert zwischen 0 und 1  (= 0%...100%)
            grauwert = int(
                96 + anzeigedauerprozent * 96
            )  # erste zahl: dunkler grauwert, zweite zahl: heller grauwert
            # in hex umrechnen (nur die letzten 2 stellen sind interessant, das 0x prefix kann ich ignorieren
            hexgrau = hex(grauwert)[-2:]
            farbwert = f"#{hexgrau}{hexgrau}{hexgrau}"
            window["canvas"].update(background_color=farbwert)
            if anzeigedauer > Game.timesize:
                # ========== new turn ==================
                game_round += 1
                # anzeigedauer = 0
                moment = time.time()

                if game_round > 0:
                    window["position"].update(disabled=False)
                    window["color"].update(disabled=False)
                    window["shape"].update(disabled=False)
                    window["number"].update(disabled=False)
                    #window["nomatch"].update(disabled=False)
                window["canvas"].erase()
                # ------- paint grid lines --------------------
                x = bl[0] - 0.5
                while x <= tr[0]:
                    window["canvas"].draw_line(
                        point_from=(x, bl[1]), point_to=(x, tr[1])
                    )
                    x += 1
                y = bl[1] - 0.5
                while y <= tr[1]:
                    window["canvas"].draw_line(
                        point_from=(bl[0], y), point_to=(tr[0], y)
                    )
                    y += 1
                # ----- grid finish ---
                if myset is not None:
                    farbe1 = myset.farbe
                    mitte1 = myset.mitte
                    shape1 = myset.shape
                    number1 = myset.zahl

                while True:
                    myset = RoundSet()
                    #farbe = random.choice(farben)
                    ##print("--shapesize-", Game.shapesize, type(Game.shapesize))
                    #shape = random.choice(Game.shapes[: int(Game.shapesize)])
                    #mitte = random.choice(mitten)
                    #number = random.choice(numbers)
                    #print("i rolled the dice, i got: ", farbe, shape, mitte, number)
                    # no match erlauben?
                    if farbe1 is None:
                        break
                    if (farbe1 != myset.farbe) and (mitte1 != myset.mitte) and (shape1 != myset.shape) and (number1 != myset.zahl):
                        print("natural nomatch")
                        if random.random() > Game.nomatch:
                            continue # nochmal zurück zum while True
                    break # verlasse die schleife
                        #if random.random() < Game.nomatch:
                        #    break
                        #else:
                        #    continue
                    #break
                # --- hier gehts weiter nach dem break
                #x, y = myset.mitte
                if myset.farbe == farbe1:
                    max_punkte += 1
                if myset.mitte == mitte1:
                    max_punkte += 1
                if myset.shape == shape1:
                    max_punkte += 1
                if myset.zahl == number1:
                    max_punkte += 1
                myset.draw(window["canvas"])

        if event in ("position", "a:38"):
            window["position"].update(disabled=True)
            if mitte1 == myset.mitte:
                hits += 1
                performance_hit[game_round] = time.time() - moment
            else:
                fails += 1
                performance_fail[game_round] = time.time() - moment
        if event in ("color", "s:39"):
            window["color"].update(disabled=True)
            if farbe1 == myset.farbe:
                hits += 1
                performance_hit[game_round] = time.time() - moment
            else:
                fails += 1
                performance_fail[game_round] = time.time() - moment
        if event in ("shape", "d:40"):
            window["shape"].update(disabled=True)
            if shape1 == myset.shape:
                hits += 1
                performance_hit[game_round] = time.time() - moment
            else:
                fails += 1
                performance_fail[game_round] = time.time() - moment
        if event in ("number", "f:41"):
            window["number"].update(disabled=True)
            if number1 == myset.zahl:
                hits += 1
                performance_hit[game_round] = time.time() - moment
            else:
                fails += 1
                performance_fail[game_round] = time.time() - moment

    window.close()
    max_fails = game_round * 3 - max_punkte
    if len(performance_hit) == 0:
        sg.PopupOK("you did not score any hits, this game will NOT be written into the statistic file")
        return
    avg_hittime = sum(performance_hit.values()) / len(performance_hit)
    max_hittime = max(performance_hit.values())
    min_hittime = min(performance_hit.values())
    text = "Your score:\nHits: {} of {} ({:.2f}%)\nFails:  {} of {} ({:.2f}%)\nFinal score: {:.2f}%\nperformance hits:{}\nperformance fails: {}\navg_hittime{:.4f}\nmax_hittime{:.4f}\nmin_hittime{:.4f}".format(
        hits,
        max_punkte,
        hits / max_punkte * 100,
        fails,
        max_fails,
        fails / max_fails * 100,
        (hits / max_punkte - fails / max_fails) * 100,
        performance_hit,
        performance_fail,
        avg_hittime,
        max_hittime,
        min_hittime,
    )

    sg.PopupOK(text, title="Game Over")
    # csv data
    now = datetime.datetime.now()

    with open(Game.filename, "a", newline="") as csvfile:
        # fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=Game.fieldnames)
        # writer.write_header()
        writer.writerow(
            {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "week": now.isocalendar()[1], # number of week
                "gridsize": Game.gridsize,
                "shapesize": Game.shapesize,
                "colorsize": Game.colorsize,
                "timesize": Game.timesize,
                "nomatch": Game.nomatch,
                "hits": hits / max_punkte * 100,
                "fails": fails / max_fails * 100,
                "avghittime": avg_hittime,
            }
        )


if __name__ == "__main__":
    settings()
    while Game.play:
        game()
        print("--------------- game fertig ---------------")
        settings()
