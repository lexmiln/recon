import re
import colorama


class Color(object):
    @staticmethod
    def green(txt):
        return colorama.Fore.GREEN + txt + colorama.Fore.RESET

    @staticmethod
    def red(txt):
        return colorama.Fore.RED + txt + colorama.Fore.RESET

    @staticmethod
    def blue(txt):
        return colorama.Fore.BLUE + txt + colorama.Fore.RESET

    @staticmethod
    def dim(txt):
        return colorama.Style.DIM + txt + colorama.Fore.RESET


def line_number_generator():
    x = 1
    while True:
        yield x
        x += 1


class ReconSyntaxError(Exception):
    pass


class ReconReader(object):
    @staticmethod
    def get_lines(inp):
        return ReconReader.concatenate_continuations(ReconReader.translate(inp))
    
    @staticmethod
    def translate(lines):
        """Returns an list of Line objects for every line
        in the input list"""
        g = line_number_generator()
        return [Line(line, g.next()) for line in lines]

    @staticmethod
    def concatenate_continuations(lines):
        """Scans the input list for continuation lines,
        and prepends their content to the OUT or IN line
        that preceded them. Raises a ReconSyntaxError if the
        preceding line is not an OUT or IN."""
        outlines = []
        lastline = None
        for line in lines:
            if line.type is LineType.CONTINUATION:
                if lastline is None:
                    raise ReconSyntaxError("Line %d: The line is a CONTINUATION, but there's nothing to continue from." % line.number)
                if lastline.type not in [LineType.IN, LineType.OUT]:
                    raise ReconSyntaxError("Line %d: Line is a CONTINUATION but the last non-continuation line is not OUT or IN." % line.number)
                lastline.content += "\n" + line.content
            else:
                lastline = line
                outlines.append(line)
        return outlines


class LineType(object):
    OUT = 1
    IN = 2
    BOOKMARK = 3
    JUMP = 4
    CONTINUATION = 5
    QUIT = 6

    @staticmethod
    def to_string(linetype):
        if linetype is LineType.OUT:
            return "OUT"
        if linetype is LineType.IN:
            return " IN"
        if linetype is LineType.BOOKMARK:
            return "BMK"
        if linetype is LineType.JUMP:
            return "JMP"
        if linetype is LineType.QUIT:
            return "BYE"
        if linetype is LineType.CONTINUATION:
            return "..."
        return "???"


class Line(object):
    in_pattern = re.compile(r"^([0-9]+|\-+)\> ")

    def __init__(self, line, number):
        self.source = line
        self.number = number
        self.type = Line.detect_linetype(line)
        self.indentation = 0
        self.content = line.strip()
        if self.type is not LineType.CONTINUATION:
            self.indentation = Line.detect_indentation(line)
            self.content = line.strip()[3:]

    def __str__(self):
        return "%3d %s %s %s" % (self.number, LineType.to_string(self.type), self.indentation, self.content.replace("\n", "\n      "))

    @staticmethod
    def detect_indentation(line):
        # Count the number of spaces at the start of the line.
        spaces = 0
        while spaces < len(line) and line[spaces] == " ":
            spaces += 1
        return spaces / 2

    @staticmethod
    def detect_linetype(line):
        stripped_line = line.strip()

        if stripped_line.startswith("<- "):
            return LineType.OUT
        if stripped_line.startswith("!B "):
            return LineType.BOOKMARK
        if stripped_line.startswith("!J "):
            return LineType.JUMP
        if stripped_line.startswith("!Q"):
            return LineType.QUIT
        if Line.in_pattern.match(stripped_line):
            return LineType.IN

        # If we couldn't detect a line type the line must
        # be a paragraph continuation.
        return LineType.CONTINUATION


class ReconPlayer(object):
    def __init__(self, lines):
        self.lines = lines
        self.cursor = 0

    def log(self, msg):
        print Color.red("# " + msg)

    def play(self, continuous=True, cursor=0, choice=None):
        self.cursor = cursor
        
        response = {
            "action": "input",
            "out": "",
            "in": [],
            "cursor": 0
        }
        
        while True:
            if self.cursor >= len(self.lines):
                self.log("Reached end of script - exiting.")
                break

            line = self.current_line()

            if line.type is LineType.JUMP:
                self.log("Jumping to " + line.content)
                self.move_cursor_to_bookmark(line.content)

            if line.type is LineType.OUT:
                self.log("Speech")
                print line.content, "\n"
                response["out"] += line.content + "\n";

            if line.type is LineType.IN:
                self.log("Conversation choice")
                in_lines = self.get_in_lines()

                # Print the options.
                response["in"] = []
                option_number = 0
                for line in in_lines:
                    option_number += 1
                    print "%s %s" % (Color.green(str(option_number) + ":"), line.content)
                    response["in"].append(line.content)

                # Get input.
                if continuous:
                    option_chosen = self.get_choice(option_number) - 1
                elif choice is not None:
                    # Use the choice given when the function was called
                    option_chosen = choice
                    # Now the choice has been made, erase it so it doesn't get reused.
                    choice = None
                else:
                    # Because play is non-continuous, return the available choices.
                    # The caller will call play again when a choice has been made.
                    response["cursor"] = self.cursor
                    return response

                # Move the cursor to whichever line was chosen.
                chosen_line = in_lines[option_chosen]
                self.move_cursor_to_line(chosen_line)
                print

            if line.type is LineType.QUIT:
                self.log("Quit")
                break

            if line.type is LineType.BOOKMARK:
                self.log("Bookmark " + line.content + " skipped")

            self.cursor += 1
        
        return {"action": "stop"}

    def move_cursor_forward(self):
        self.cursor += 1

    def move_cursor_to_line(self, line):
        self.cursor = self.lines.index(line)

    def move_cursor_to_bookmark(self, name):
        for line in self.lines:
            if line.type is LineType.BOOKMARK and line.content == name:
                self.move_cursor_to_line(line)
                return
        self.log("Couldn't find bookmark " + name)

    def current_line(self):
        return self.lines[self.cursor]

    def get_in_lines(self):
        """Returns a list of all IN lines that belong to the same
        set as the IN line that the cursor is on."""

        indentation = self.current_line().indentation

        in_lines = []

        for line in self.lines[self.cursor:]:
            if line.indentation < indentation:
                # A dedent implies that the IN group has ended.
                break
            if line.indentation > indentation:
                # An indent implies that this line is a child of
                # a previous IN line.
                continue
            if line.type is LineType.IN:
                # Match!
                in_lines.append(line)
            else:
                # This line is on the same indentation level
                # but is not an IN line, which implies that the
                # group has ended.
                break

        return in_lines

    def get_choice(self, max_number):
        while True:
            print ("Choose an option between 1 and %d:" % max_number),
            inp = raw_input()

            try:
                inp_int = int(inp)
            except ValueError:
                print "That's not a number!"
            else:
                if inp_int > 0 and inp_int <= max_number:
                    return inp_int
                print "That number isn't one of the available choices."


def strip_out(line):
    """Returns a string without the OUT token on the front,
    if the string has one."""
    if line.startswith("<-"):
        return line[3:]
    return line

def get_player(path):
    with open(path) as f:
        source = f.readlines()
    lines = ReconReader.get_lines(source)
    return ReconPlayer(lines)

def show_lines():
    with open("recon/test.recon") as f:
        source = f.readlines()

    lines = ReconReader.translate(source)
    lines = ReconReader.concatenate_continuations(lines)

    print ""
    print "DUMP"
    print "===="
    print

    for line in lines:
        print line

def play(script_name):
    colorama.init()
    get_player("recon/%s.recon" % script_name).play()
