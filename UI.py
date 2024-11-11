import math
import os
import sys

UP = "\033[A"

color_dict = {
	"default"		: 	"37;1",
	"red"			: 	"31;1",
	"green"			: 	"32;1",
    "yellow"		:	"33;1",
	"cyan"			: 	"36;1"
}
style_dict = {
	"default"		: 	"0",
	"highlight"		: 	"1",
	"fade"		    : 	"2",
	"underscore"    : 	"4",
    "inverted"		: 	"7",
    "hidden"		: 	"8"
}
def color(color="default", style="default"):
    return f"\x1b[{style_dict[style]};{color_dict[color]}m"

def get_ch():
    import msvcrt
    return msvcrt.getch().decode("utf-8")

def get_input_with_prefill(prompt, text):
    import readline
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input("\033[96m" + prompt + "\033[0;0m")
    readline.set_pre_input_hook()
    return result

def print_over_line(text="", start_color="default", start_style="default", at_start_cursor_moves="\r", at_end_cursor_moves=""):
    reset_color=color()
    line = color(start_color, start_style) + text.ljust(os.get_terminal_size().columns) + reset_color

    print(f"{at_start_cursor_moves}\r{line}", end=at_end_cursor_moves)

def print_over_lines(lines=[""], start_color="default", start_style="default", at_start_cursor_moves="", at_end_cursor_moves=UP):
    reset_color=color()
    start_color_str = color(start_color, start_style)
    line_ceparator = "\n" + start_color_str

    lines = (line.ljust(os.get_terminal_size().columns) for line in lines)
    lines_string =  start_color_str + line_ceparator.join(lines) + reset_color

    print(at_start_cursor_moves + lines_string, end=at_end_cursor_moves)

def handle_input(selected_option, current_options, argument_options):
    ch = get_ch()
    if ch == "d":
        if selected_option < len(argument_options)-1:
            selected_option += 1
    elif ch == "a":
        if selected_option > 0:
            selected_option -= 1
    elif ch == "w":
        if current_options[selected_option] < len(argument_options[selected_option][1])-1:
            current_options[selected_option] += 1
    elif ch == "s":
        if current_options[selected_option] > 0:
            current_options[selected_option] -= 1
    elif ch in ("\n", "\r"):
        return -1, argument_options, current_options
    else:
        print_notification("unknown input character " + color(style="highlight") + "\"" + repr(ch).strip("'") + "\"")
    
    print_over_lines(lines=[" Use wasd to change settings and press ENTER to run the tool"], start_style="fade", at_start_cursor_moves="\n", at_end_cursor_moves = UP)

    return selected_option, argument_options, current_options

def print_notification(message):
    print_over_lines(lines=[message + color(style="fade") + " (press any key to continue)"], start_color="red", start_style="highlight", at_start_cursor_moves="\n", at_end_cursor_moves = UP)
    get_ch()
    print_over_lines(lines=["", ""], at_start_cursor_moves=UP, at_end_cursor_moves = UP)

def offset_line(selected_option, current_options, argument_options, line_num, offset, center_line):
    line = color()
    _lines_from_center = center_line-line_num
    _this_lines_argument_option_number = current_options[selected_option] + _lines_from_center
    _len_of_the_argument_options = len(argument_options[selected_option][1])

    if _this_lines_argument_option_number >= 0 and _this_lines_argument_option_number < _len_of_the_argument_options:
        x_arg_with_text = get_highlighted_arg_with_text(argument_options, selected_option, current_options, offset_selected_option=_lines_from_center, highlight_style="default", secondary_style="fade")
        line = "".ljust(offset) + x_arg_with_text
    return line

def center_line(selected_option, current_options, argument_options):
    lines = []
    for i in range(len(argument_options)):
        _highlight_style, _highlight_color = ("inverted", "green") if (i == selected_option) else ("underscore", "default")
        x_arg_with_text = get_highlighted_arg_with_text(argument_options, i, current_options, highlight_style=_highlight_style, highlight_color=_highlight_color, secondary_style="default")
        lines.append(x_arg_with_text)
    centerLine = " ".join(lines)
    return centerLine

def get_highlighted_arg_with_text(argument_options, x, current_options, offset_selected_option=0, highlight_color="default", highlight_style="underscore", secondary_color="default", secondary_style="fade"):
    x_arg_with_text = color(secondary_color, secondary_style) + argument_options[x][0] + color(highlight_color, highlight_style) + str(argument_options[x][1][current_options[x]+offset_selected_option]) + color(secondary_color, secondary_style)
    if len(argument_options[x]) == 3: x_arg_with_text += argument_options[x][2]
    return x_arg_with_text

def get_arg_with_text(argument_options, x, current_options, offset_selected_option=0):
    x_arg_with_text = argument_options[x][0] + str(argument_options[x][1][current_options[x]+offset_selected_option])
    if len(argument_options[x]) == 3: x_arg_with_text += argument_options[x][2]
    return x_arg_with_text

def get_offset(selected_option, argument_options, current_options):
    offset = 0
    for x in range(selected_option):
        x_arg_with_text = get_arg_with_text(argument_options, x, current_options)
        offset += len(x_arg_with_text) + 1
    return offset

def print_the_lines(selected_option, current_options, argument_options, old_lines):
    offset = get_offset(selected_option, argument_options, current_options)

    lines = []
    amount_of_lines = len(old_lines)
    amount_of_upper_lines = math.floor(amount_of_lines/2)

    #creates the lines
    for x in range(0, amount_of_lines):
        if x == amount_of_upper_lines:
            lines.append(center_line(selected_option, current_options, argument_options))
        else:
            lines.append(offset_line(selected_option, current_options, argument_options, x, offset, amount_of_upper_lines))

    if len(old_lines) != amount_of_lines:
        raise Exception("incorrect amount of lines!")

    #makes terminal window more wide if needed
    _width = 0
    for x in range(len(argument_options)):
        x_arg_with_text = get_arg_with_text(argument_options, x, current_options)
        _width += len(x_arg_with_text) + 1
    while _width > os.get_terminal_size().columns:
        print_notification("Please make the window wider or the text smaller!")
        #sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=_width))

    _lines_string = "\n".join(lines)
    print(_lines_string, end="\r")

    return lines

def run_command_handler(argument_options, args):
    if len(args) == 2 and args[1] == "ui":
        return run_ui(argument_options)
    elif len(args) == 1+len(argument_options):
        _options_parsed_from_args = []
        for i in range(len(argument_options)):
            if (args[i+1] in argument_options[i][1]):
                _options_parsed_from_args.append(args[i+1])
            elif (int(args[i+1]) in argument_options[i][1]):
                _options_parsed_from_args.append(int(args[i+1]))
            else:
                ### Could try and come up with good way to deal with an option like: "("and ", ["use previously queried and saved prices", "use API"])" 
                ### I want to keep this script as modular as possible, but maybe we could accept boolean args when ever there is just 2 options string to choose from. 
                print()
                print(color("red") + "INVALID ARGUMENT!\n" + args[i+1] + " NOT IN  " + str(argument_options[i][1]) + "\n" + color())
                sys.exit()
        return _options_parsed_from_args
    elif len(args) == 1:
        _default_options = []
        for i in range(len(argument_options)):
            if (str(argument_options[i][1][0]).isdigit()):
                _default_options.append(int(argument_options[i][1][0]))
            else:
                _default_options.append(argument_options[i][1][0])
        return _default_options
    else:
        print("SOMETHING WRONG WiTH THE ARGUMENTS")
        sys.exit()

_product_list = (
    "all",
    "titanium bar",
    "All potions",
    "Potion of swiftiness",
    "Potion of resurrection",
    "Potion of great sight",
    "Potion of trickery",
    "Potion of dark magic",
    "Potion of pure power"
)
#                                text1        the options as lists                                   (optional)text2
def run_ui(argument_options = (("Produce ",  _product_list                                                                           ), 
                               ("with ",     range(0, 50),                                          f"% active boost"                ), 
                               ("and with ", [10 * i for i in range(0, 5)],                         f"% chance to save the materials"), 
                               ("and ",      ["use previously queried and saved prices", "use API"]                                  )),
           number_of_lines = 9   ):
    '''
    Takes an argument_options list as input. It contains lists that always have a string of text first, and secondly a list of options, and optionally lastly a second string.\n
    argument_options( option_X( string, (x1, x2, x3, ... ), optional_string  ), \n
    _________________ option_y( string, (y1, y2, y3, ... ), optional_string  ), \n
    _________________ option_z( string, (z1, z2, z3, ... ), optional_string  ), \n
    _________________ ... )
    '''

    #linewraping might not be possible to turn off like this in all terminals
    sys.stdout.write("setterm -linewrap off")
    print(UP)

    # key 'a' moves left in and 'd' right, by decreasing and increasing this argument
    selected_option = 0

    # keys 'w' and 's' can be used to change currently selected_options values in this integer list.
    current_options = [0 for _ in range(len(argument_options))]

    _reversing_print = ""
    for i in range(number_of_lines):
        _reversing_print += UP

    lines = print_the_lines(selected_option, current_options, argument_options, ["" for _ in range(number_of_lines)])
    while True:
        sys.stdout.flush()
        print(_reversing_print)

        #Clears terminal for new prints
        _whitespaces = ""
        for _ in range(number_of_lines):
            _whitespaces += "".ljust(os.get_terminal_size().columns)
        print(_whitespaces, end="\r")
        print(_reversing_print)

        lines = print_the_lines(selected_option, current_options, argument_options, lines)

        selected_option, argument_options, current_options = handle_input(selected_option, current_options, argument_options)
        if selected_option == -1:
            print("\n")
            print("run the script")
            break
        elif selected_option == -2:
            print("save")
            #TODO save current selections to some file and also implement loading saves somehow neatly
        elif selected_option == -3:
            print("exit")
            exit()
    return return_output_values(current_options, argument_options)

def return_output_values(current_options, argument_options):
    return_values = []
    for i in range(len(argument_options)):
        return_values.append(argument_options[i][1][current_options[i]])
    print("return: " + str(return_values))
    return return_values

if __name__ == '__main__':
    # Just examples to demonstrate how this can be used through that argument_options variable
    # You run this script directly for a bit of demonstration
    o1, o2, o3, o4 = run_ui(argument_options = 
                            (
                                ("option1 ",   (123, 234, 345)                                ), 
                                ("option2 ",   range(0, 50),                          " optional extra text for option2"), 
                                ("option3 ",   [10 * i for i in range(0, 5)],         " optional extra text here too!"), 
                                ("option4 ",   ("ok", "yes", "hello", "awdawdwadaw")          )
                            )
                           )
    print(f"run_ui() returned: \"{o1}\" \"{o2}\" \"{o3}\" and \"{o4}\"")
    
    #chosen_argument_values_list = run_ui(argument_options = ( ("option1 ", (123, 234, 345, 312312)),   ("option2123 ", ("ok", "yes", "hello", "awdawdwadaw")) ))
    #print(f"run_ui() returned: {chosen_argument_values_list}")