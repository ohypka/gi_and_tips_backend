DEBUG_MODE = True

def debug_log(message):
    """
    Prints debug messages if DEBUG_MODE is enabled.

    Args:
        message (str): The debug message to print.
    """
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")
