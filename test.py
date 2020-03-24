#测试用的

# a = [1,2,3,4]
# for i in range(5):
#     for j in range(5):
#         try:
#             print(a[j])
#         except IndexError:
#             print("55555")
# print(bool(""))

# a = 8
# print(sum(map(int, a)))
test = {"domain":3,'range':5}
a = "domain"
test[a] +=1

# print(test["domain"]+1)
# 查找是否有相应的domain
print(test.get("domain",'nothing'))

test.update({"age":12})
print(test)