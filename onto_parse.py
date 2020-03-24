#coding=utf-8
from rdflib import Graph, URIRef, BNode
import rdflib.extras.infixowl as rdfin


#解析类，输入测试用例的数字，如 101
#获取classes，properties以及参考结果
class Parse():
    def __init__(self, path):
        try:
            self.graph = Graph().parse("benchmarks/{}/onto.rdf".format(path))
        except:
            self.graph = Graph().parse("benchmarks/{}/test.rdf".format(path))
        self.par = Graph().parse("benchmarks/{}/refalign.rdf".format(path))

    #五元列表，获取所有class，对应的lable，comment，父节点，子节点 返回二维列表
    def getClasses(self):
        classes = [[] for i in range(len(self.graph))]
        # sub 为了获取父节点和子节点的谓语
        sub  = URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")
        for index, i in enumerate(rdfin.AllClasses(self.graph)):
            # print(str(i.identifier))
            #type <class 'rdflib.extras.infixowl.Class'>
            #303和302
            id = i.identifier
            if "rdf#" in str(id) or "ontology#" in str(id) or "owl#" in str(id):
                classes[index].append(str(id)[str(id).find('#')+1: ])
                classes[index].append(str(self.graph.label(id)))
                classes[index].append(str(self.graph.comment(id)))
                # 父节点 用空格切分
                parents = ""
                for j in list(self.graph.objects(id, sub)):
                    if "#" in str(j):
                        parents += str(j)[str(j).find("#")+1:] + " "
                parents = parents.strip()
                classes[index].append(parents)
                #子节点 用空格切分
                childen = ""
                for j in list(self.graph.subjects(sub, id)):
                    if "#" in str(j):
                        childen += str(j)[str(j).find("#")+1:] + " "
                childen = childen.strip()
                classes[index].append(childen)
        return [i for i in classes if i]

    #解析对齐文件 返回二维列表
    def getParsealign(self):
        #谓语
        align1 = URIRef("http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity1")
        align2 = URIRef("http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity2")
        median = URIRef("http://knowledgeweb.semanticweb.org/heterogeneity/alignmentmeasure")
        bnodes = []
        for i in self.par.subjects(median):
            bnodes.append(i)
        mix = [[] for i in range(len(self.par))]
        for index, i in enumerate(bnodes):
            a = list(self.par.objects(i, align1))[0]
            b = list(self.par.objects(i, align2))[0]
            onto1 = str(a)[str(a).find("#")+1:]
            onto2 = str(b)[str(b).find("#")+1:]
            mix[index].append(onto1)
            mix[index].append(onto2)

        return [i for i in mix if i]

    # 获取所有property，对应的label，comment，domain，range 返回二维列表
    def getProperty(self):
        ran = URIRef("http://www.w3.org/2000/01/rdf-schema#range")
        dom = URIRef("http://www.w3.org/2000/01/rdf-schema#domain")
        #谓语
        unionof = URIRef("http://www.w3.org/2002/07/owl#unionOf")
        # 谓语
        first = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first")
        # 谓语
        rest = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest")
        properties = [[] for i in range(len(self.graph))]
        for index, i in enumerate(rdfin.AllProperties(self.graph)):
            id = i.identifier
            str_id = str(id)
            #调试用
            # if str_id[str_id.find('#') + 1:] == "publisher":
            #     print(123)
            if "rdf#" in str_id or "ontology#" in str_id or "owl#" in str_id:
                properties[index].append(str_id[str_id.find('#') + 1:])
                try:
                    properties[index].append(str(list(i.label)[0]))
                except:
                    properties[index].append(None)
                try:
                    properties[index].append(str(list(i.comment)[0]))
                except:
                    properties[index].append(None)

                domains = list(i.domain)
                if domains:
                    test = str(domains[0].identifier)
                    if "Some Class" in str(domains[0]):
                        test2 = str(domains[0]).split("'")
                        try :
                            properties[index].append(test2[1] + "," + test2[3] + "," + test2[5])
                        except:
                            try:
                                properties[index].append(test2[1] + "," + test2[3])
                            except:
                                properties[index].append(test2[1])
                    else:
                        properties[index].append(test[test.find('#') + 1:])
                else:
                    properties[index].append(None)
                try:
                    r = list(self.graph.objects(id, ran))[0]
                    properties[index].append(str(r)[str(r).find('#') + 1:])
                except:
                    properties[index].append(None)
        return [i for i in properties if i]

    # 获取所有dataproperty，对应的label，comment，domain，range 返回二维列表
    def getDataproperties(self):
        typ = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        dataP = URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")
        allP = self.getProperty()
        dataProperties = [[] for i in range(len(allP))]
        for i in list(self.graph.subjects(typ, dataP)):
            for j in allP:
                stri = str(i)
                if "rdf#" in stri or "ontology#" in stri or "owl#" in stri:
                    if stri[stri.find("#") + 1:] == j[0]:
                        dataProperties.append(j)
        dataProperties = [i for i in dataProperties if i]
        return dataProperties

    # 获取所有ObjectProperty，对应的label，comment，domain，range 返回二维列表
    def getObjectProperties(self):
        typ = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        objectP = URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")
        allP = self.getProperty()
        ObjectProperty = [[] for i in range(len(allP))]
        for i in list(self.graph.subjects(typ, objectP)):
            for j in allP:
                stri = str(i)
                if "rdf#" in stri or "ontology#" in stri or "owl#" in stri:
                    if stri[stri.find("#") + 1:] == j[0]:
                        ObjectProperty.append(j)
        ObjectProperty = [i for i in ObjectProperty if i]
        return ObjectProperty

#三元组 主谓宾
def triple(g):
    for i, j, k in g:
        # print(i,j,k)
        print(type(i), i)
        print(type(j), j)
        print(type(k), k)
        print("~~~")

if __name__ =="__main__":
    #类的属性
    # onProperty = URIRef("http://www.w3.org/2002/07/owl#onProperty")
    # gragh = Graph().parse("benchmarks/205/test.rdf")
    # triple(gragh)

    onto1 = Parse(301)
    #打印参考匹配对、类、属性
    print(onto1.getParsealign())
    print(onto1.getClasses())
    print(onto1.getObjectProperties())
    print(onto1.getDataproperties())

