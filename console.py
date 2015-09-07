import os
import urwid
import multiprocessing
import time

import cognise

urwid.set_encoding("UTF-8")

COGNISE_LOG_LINES = 100
log_counter = 0
palette = [
    ('whitebg', '', '', '', '#000', '#fff'),
    ('bg', '', '', '', '#000', '#AAA'),
    ('blackbg', '', '', '', '#FFF', '#000'),
]

header = urwid.Text(('headfoot', " R E C O N "))
footer = urwid.Text("- Idle -")

interactive = urwid.Text("Hello world! Lorem ipsum dolor sit amet futuris decant sipur.")
interactivefill = urwid.Filler(interactive, 'bottom')

lines = [urwid.Text("Line %d" % i) for i in xrange(COGNISE_LOG_LINES)]

pile = urwid.Pile(lines)
fill = urwid.Filler(pile, 'top')

columns = urwid.Columns([
    (74, interactivefill),
    fill
    ], dividechars=2)
columns = urwid.AttrMap(columns, '')

frame = urwid.AttrMap(urwid.Frame(columns, header=header, footer=footer), 'bg')

loop = urwid.MainLoop(frame, palette)
loop.screen.set_terminal_properties(colors=256)


# Cognise log pipe allows cognise to write onto the screen.
def log_from_cognise(msg):
    global log_counter
    msgs = msg.split("\n")
    for msg in msgs:
        if len(msg):
            lines[log_counter].set_text(msg)
            log_counter += 1
            log_counter %= COGNISE_LOG_LINES
            lines[log_counter].set_text("")

cognise_log_pipe = loop.watch_pipe(log_from_cognise)


# The cognise process entrypoint
def cognise_process(log_pipe):
    def log(msg):
        os.write(log_pipe, msg + "\n")
    log("Initialising cognise...")
    time.sleep(1)
    cognise.cognise(log)


p = multiprocessing.Process(target=cognise_process, args=(cognise_log_pipe,))
p.start()

loop.run()
