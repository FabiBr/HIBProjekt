def get_party(name):
    file = open('bundestagKurz.csv', "r")
    for line in file:
        line = line.replace('GR\x9aNE', 'GRUENE')
        if name.lower() == line.split(';')[-1].strip()[1:].lower():
            file.close()
            return line.split(';')[1]
        file.close()
    return 'UNBEKANNT'
