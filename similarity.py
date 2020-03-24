#coding=utf-8
import Levenshtein
from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
import onto_parse

# nltk.download('wordnet')
# nlp = spacy.load("D:\en_core_web_lg-2.2.5\en_core_web_lg\en_core_web_lg-2.2.5")

#相似度类，Levenshtein distance，jaro distance和 wordnet相似度
#输入两个字符串，返回相似度值
class similirites():

    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
    #获取levensh相似度
    def Levensh(self):
        if self.s1 == "null" or self.s2 =="null":
            return 0
        if "The name of an entity" in self.s1 or "The name of an entity" in self.s2:
            return 0
        else :
            minimum = min(len(self.s1),len(self.s2))
            d = Levenshtein.distance(self.s1, self.s2)
            levensh = max(0, (minimum - d) / minimum)
            # print(minimum, d)
            return levensh

    # 获取Jaro相似度
    def Jaro(self):
        if self.s1 == "null" or self.s2 =="null":
            return 0
        else :
            return Levenshtein.jaro(self.s1, self.s2)
    # 获取wordnet相似度
    def wordnet(self):
        list1 = wn.synsets(self.s1)
        list2 = wn.synsets(self.s2)
        simi = []

        if not list1 :
            return 0
        elif not list2:
            return 0
        else:
            for i in list1:
                for j in list2:
                    if i.path_similarity(j):
                        simi.append(i.path_similarity(j))
            #去除列表 None值
            if not simi:
                return 0
            else:
                return max(simi)

#输入id，返回在矩阵中的索引
def getIndex(onto_classes, id):
    DF = pd.DataFrame(onto_classes)[0]
    return (DF[DF == id].index)[0]

#输入两个本体 path 如 101,102 , 输出classes,dataproperty, objectproperty的相似度矩阵
def similarity_flooding(onto1, onto2):
    onto1 = onto_parse.Parse(onto1)
    onto2 = onto_parse.Parse(onto2)
    onto1_classes = onto1.getClasses()
    onto2_classes = onto2.getClasses()
    onto1_dataproperties = onto1.getDataproperties()
    onto2_dataproperties = onto2.getDataproperties()
    onto1_objectproperties = onto1.getObjectProperties()
    onto2_objectproperties = onto2.getObjectProperties()

    #np.zeros二维，要两个括号
    simi_classes = np.zeros((len(onto1_classes), len(onto2_classes)))
    simi_dataproperties= np.zeros((len(onto1_dataproperties), len(onto2_dataproperties)))
    simi_objectproperties = np.zeros((len(onto1_objectproperties), len(onto2_objectproperties)))

    #先确认高度相关的类，ID或comment完全相同则相似度为 1
    for index_i, i in enumerate(onto1_classes):
        for index_j, j in enumerate(onto2_classes):
            if i[0] == j[0] or i[2] == j[2] :
                simi_classes[index_i][index_j] = 1

    # 扩散到子类
    iteration = 3
    while iteration > 0:
        for index_i, i in enumerate(onto1_classes):
            for index_j, j in enumerate(onto2_classes):
                if simi_classes[index_i][index_j]:
                    son1 = i[4]
                    son2 = j[4]
                    #有子类则给相似度
                    if son1:
                        if " " in son1:
                            subclasses1 = son1.split(" ")
                        else:
                            subclasses1 = son1
                    else:
                        continue
                    # 有子类则给相似度
                    if son2:
                        if " " in son2:
                            subclasses2 = son2.split(" ")
                        else:
                            subclasses2 = son2
                    else:
                        continue

                    for sub1 in subclasses1:
                        for sub2 in subclasses2:
                            sub1_Index = getIndex(onto1_classes, sub1)
                            sub2_Index = getIndex(onto2_classes, sub2)
                            # try:
                            # 有相似度则跳出
                            if simi_classes[sub1_Index][sub2_Index]:
                                continue
                            else:
                                #父类的相似度除以子类的个数
                                simi_classes[sub1_Index][sub2_Index] = simi_classes[index_i][index_j] / (len(list(set(subclasses1+subclasses2))))
                            # 调试用
                            # except:
                            #     print(subclasses1, subclasses2)
                            #     print(sub1_Index, sub2_Index)
        iteration -= 1

    #先确认高度相关的数据属性，ID或comment完全相同则相似度为 1
    for index_i, i in enumerate(onto1_dataproperties):
        for index_j, j in enumerate(onto2_dataproperties):
            if i[0] == j[0] or i[2] == j[2] :
                simi_dataproperties[index_i][index_j] = 1

    # 计算各个domain出现的次数
    domains1 = {}
    for index_i, i in enumerate(onto1_dataproperties):
        #没有新建，有则加 1
        if not domains1.get(i[3]):
            domains1.update({i[3]: 1})
        else:
            domains1[i[3]] += 1
    domains2 = {}
    for index_i, i in enumerate(onto2_dataproperties):
        #没有新建，有则加 1
        if not domains2.get(i[3]):
            domains2.update({i[3]: 1})
        else:
            domains2[i[3]] += 1

    # dataproperties根据domain给相似度
    for index_i, i in enumerate(onto1_dataproperties):
        for index_j, j in enumerate(onto2_dataproperties):
            if not simi_dataproperties[index_i][index_j]:
                num1 = domains1[i[3]]
                num2 = domains2[j[3]]
                try:
                    sub1_Index = getIndex(onto1_classes, i[3])
                    sub2_Index = getIndex(onto2_classes, j[3])
                except:
                    continue

                if simi_classes[sub1_Index][sub2_Index]:
                    # 父类的相似度除以相同domain的个数
                    simi_dataproperties[index_i][index_j] = simi_classes[sub1_Index][sub2_Index] / min(num1, num2)


    #先确认高度相关的数据属性，ID或comment完全相同则相似度为 1
    for index_i, i in enumerate(onto1_objectproperties):
        for index_j, j in enumerate(onto2_objectproperties):
            if i[0] == j[0] or i[2] == j[2] :
                simi_objectproperties[index_i][index_j] = 1

    # 建立字典，计算各个domain出现的次数
    domains1 = {}
    range1 = {}
    for index_i, i in enumerate(onto1_objectproperties):
        #没有新建，有则加 1
        if not domains1.get(i[3]):
            domains1.update({i[3]: 1})
        else:
            domains1[i[3]] += 1
        if not range1.get(i[4]):
            range1.update({i[4]: 1})
        else:
            range1[i[4]] += 1
    domains2 = {}
    range2 = {}
    for index_i, i in enumerate(onto2_objectproperties):
        #没有新建，有则加 1
        if not domains2.get(i[3]):
            domains2.update({i[3]: 1})
        else:
            domains2[i[3]] += 1
        if not range2.get(i[4]):
            range2.update({i[4]: 1})
        else:
            range2[i[4]] += 1

    # dataproperties根据domain和range给相似度
    for index_i, i in enumerate(onto1_objectproperties):
        for index_j, j in enumerate(onto2_objectproperties):
            if not simi_objectproperties[index_i][index_j]:
                #获取索引
                try:
                    sub1_Index_domain = getIndex(onto1_classes, i[3])
                    sub2_Index_domain = getIndex(onto2_classes, j[3])
                except:
                    continue
                try:
                    sub1_Index_range = getIndex(onto1_classes, i[4])
                    sub2_Index_range = getIndex(onto2_classes, j[4])
                except:
                    continue

                if simi_classes[sub1_Index_domain][sub2_Index_domain]:
                    # domain的相似度除以相同domain的个数
                    simi_domain = simi_classes[sub1_Index_domain][sub2_Index_domain] / min(domains1[i[3]], domains2[j[3]])
                else:
                    simi_domain = 0
                if simi_classes[sub1_Index_range][sub2_Index_range]:
                    # range的相似度除以相同 range的个数
                    simi_range = simi_classes[sub1_Index_range][sub2_Index_range] / min(range1[i[4]], range2[j[4]])
                else:
                    simi_range = 0
                # domain的相似度除以相同domain的个数加上 range的相似度除以相同 range的个数
                simi_objectproperties[index_i][index_j] = simi_domain + simi_range

    #打印类的结构相似度, 展示结果，不需要可以注释
    for index_i, i in enumerate(onto1_classes):
        for index_j, j in enumerate(onto2_classes):
            print(i[0] , j[0] , simi_classes[index_i][index_j])

    return simi_classes, simi_dataproperties, simi_objectproperties


if __name__=="__main__":
    #测试SF相似度
    similarity_flooding(101,103)

    #测试三个相似度
    simi = similirites("last", "first")

    print("similarities of last and first", simi.Levensh(), simi.Jaro(), simi.wordnet())



