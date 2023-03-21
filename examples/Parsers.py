import re
import json

"""
A file for Player utilities, focused around parsing chat and making it human readable.

The DefaultParser should be able to handle most situations currently,
however, there are known weakness's in the approach but as it stands,
it is better then other examples I have seen.

DefaultParser - Tested on mc-central, should work decent globally
"""

# TODO Parse banner messages, example:
# https://gyazo.com/c0a4cfee23a31fe8b6e4c7c7848e5e5a


def DefaultParser(data):
    """The default Player chat packet parser, designed to make chat human readable.

    Parameters
    ----------
    data : Chat Packet
        The chat packet to be parsed.

    Returns
    -------
    message : str
        The chat message in human readable form
    False : bool
        If the parser encounters an error during parsing

    """
    try:
        # Convert to valid python dict
        data = json.loads(data)

        # Create the prefix & text
        prefixing = True
        data = data["extra"]
        stringDict = {"prefix": [], "message": []}
        dm = False

        if isinstance(data[len(data) - 1], str):
            # Given the last item is a string, rather then dictionary
            # we can safely assume that this is in fact a /msg
            dm = True

        for i, item in enumerate(data):
            # Remove minecraft character stuff
            if dm and i == len(data) - 1:
                stringDict["message"].append(item)
                continue

            text = re.sub(
                r"\§c|\§f|\§b|\§d|\§a|\§1|\§2|\§3|\§4|\§5|\§6|\§7|\§8|\§9|\§0",
                "",
                item["text"],
            )

            if text.lstrip().rstrip() == ":" and prefixing:
                # No longer need to handle the before message
                prefixing = False
                continue
            elif prefixing:
                stringDict["prefix"].append(text)
            elif not prefixing:
                if "extra" in item:
                    # Chat parsing for text means this is most likely another
                    # nested dict in list situation
                    if len(item["extra"]) > 0:
                        if "text" in item["extra"][0]:
                            text = item["extra"][0]["text"]
                stringDict["message"].append(text)

        prefix = "".join(stringDict["prefix"])
        text = " ".join(stringDict["message"]).rstrip().lstrip()

        if len(prefix) > 0 and len(text) > 0:
            message = ": ".join([prefix, text])
        elif len(prefix) > 0:
            message = prefix
        elif len(text) > 0:
            message = text

        message = message.lstrip().rstrip()

        return message

    except Exception as e:
        # print(f"Unable to parse: {data}\nException: {e}")
        return False
