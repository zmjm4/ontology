import onto_parse


class Ontology():
    def __init__(self, path):
        parse = onto_parse.Parse(path)
        self.classes = parse.getClasses()
        self.dataproperties = parse.getDataproperties()
        self.objectproperties = parse.getObjectProperties()

if __name__=="__main__":
    onto1 = Ontology(101)
    print(onto1.classes)