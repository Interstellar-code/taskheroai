import os
import sys
import time
from typing import List

from colorama import Fore, Style, init

init()


def display_animated_banner(
    frames: List[str] = None,
    frame_delay: float = 0.5,
    color: str = Fore.CYAN,
    clear_screen: bool = True,
) -> None:
    """Display an animated ASCII art banner.

    Args:
        frames (List[str], optional): List of ASCII art frames to display.
            Defaults to ANIMATION_FRAMES.
        frame_delay (float, optional): Delay between frames in seconds.
            Defaults to 0.5.
        color (str, optional): Color to use for the banner.
            Defaults to Fore.CYAN.
        clear_screen (bool, optional): Whether to clear the screen before displaying.
            Defaults to True.
    """
    if frames is None:
        frames = ANIMATION_FRAMES

    if clear_screen:
        os.system("cls" if os.name == "nt" else "clear")

    for frame in frames:
        sys.stdout.write("\033[H")
        sys.stdout.write(f"{color}{Style.BRIGHT}{frame}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(frame_delay)

    print()


TASK_HERO_AI = r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
"""

ANIMATION_FRAMES = [
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [⣾]
    > Initializing AI engine...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [⣽]
    > Initializing AI engine...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [⣻]
    > Initializing AI engine...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [⢿]
    > Initializing AI engine...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [⡿]
    > Initializing AI engine...
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [DONE]
    > Initializing AI engine... [DONE]
    """,
    r"""
 _______         _    _    _                  ___    _____
|__   __|       | |  | |  | |                / _ \  |_   _|
   | | __ _ ___| | _| |__| | ___ _ __ ___   | |_| |   | |
   | |/ _` / __| |/ /  __  |/ _ \ '__/ _ \  |  _  |   | |
   | | (_| \__ \   <| |  | |  __/ | | (_) | | | | |  _| |_
   |_|\__,_|___/_|\_\_|  |_|\___|_|  \___/  |_| |_| |_____|
    > AI Assistant for Project Management & Code
    > Analyzing your codebase... [DONE]
    > Initializing AI engine... [DONE]
    > Ready to help with your questions!
    """,
]