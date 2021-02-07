import token, tokenize
import fileinput

def remove_comments(fname):
    with open(fname, "r") as source:
        output = ""
        prev_toktype = token.INDENT
        last_lineno = -1
        last_col = 0

        tokgen = tokenize.generate_tokens(source.readline)
        for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
            if slineno > last_lineno:
                last_col = 0
            if scol > last_col:
                output += " " * (scol - last_col)
            if toktype == token.STRING and prev_toktype == token.INDENT:
                output += ""
            elif toktype == tokenize.COMMENT:
                output += ""
            else:
                output += ttext
            prev_toktype = toktype
            last_col = ecol
            last_lineno = elineno

        with open(fname, "w") as dest:
            dest.write(output)

        # Remove empty lines and characters
        output = ""
        for line in fileinput.FileInput(fname):
            if line.rstrip():
                output += line.replace(", ", ",").replace(": ", ":").replace(" = ", "=")
            
        with open(fname, "w") as dest:
            dest.write(output)
