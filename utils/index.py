
def outputCleaner(output):

    # clean unicode characters
    output = output.encode('ascii', 'ignore').decode('ascii')

    # clean think tags
    if "</think>" in output:
        output = output.split("</think>")[1]
    
    # clean json tags
    if "```json" in output:
        output = output.split("```json")[1].split("```")[0]
    
    #clean \n
    output = output.replace("\n", "")

    output = output.strip()
    return output

export = {
    "outputCleaner": outputCleaner
}