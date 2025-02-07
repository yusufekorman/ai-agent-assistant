from utils.logger import get_logger

logger = get_logger()


def outputCleaner(output: str) -> str:
    """
    Clean the output of the content
    """
    if "</think>" in output:
        output = str(output).split('</think>')[1]

    # Only get the json part of the output
    if "{" not in output or "}" not in output:
        logger.error("Output does not contain a JSON object")
        return output
    
    json_start = output.find("{")
    json_end = output.rfind("}") + 1
    output = output[json_start:json_end]

    # Remove the new line character
    output = output.replace("\n", "")

    # Remove the white spaces
    output = output.strip()

    # Return the cleaned output
    return output

# Export
export = {
    "outputCleaner": outputCleaner
}