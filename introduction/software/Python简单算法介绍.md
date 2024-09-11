如果输入为一行
```python
a, b = input().split()
```

如果输入为一行两个整型
```python
a, b = map(int,input().split())  
a,b = int(input().split())是不正确的
```

如果输入为一行多个整型
```python
num = [int(i.strip()) for i in input().split()]
```

变量交换
```python
int a;
int b;
a = a+b;
b = a-b;
a = a-b; 
```

输出A+B
```python
a,b = map(int,input().split())
print(a+b)
```

List删除3种方法
```python
del listname[index]
listname.pop(index)
listname.remove(value)
```

数列排序
```python
n = input()
lisa = [int(i.strip()) for i in input().split()]
lisa.sort()
for i in lisa:
    print(i,end = '')
```

列表排序如果不转化int类型，就会导致10字符串在2前面。

列表去重排序输出：
```python
temp = list(set([int(i.strip()) for i in input().split()]))
temp.sort()
for i in temp:
    print(i,end=' ')
```

数列求和
```python
n = int(input())
sum = 0
if n%2 == 0:
    sum = (n*(n+1)//2)
else:
    sum = (n* (n+1)//2) +(n+1)//2
print(sum)
```

提取字符串中的数字
```python
a = "a23aw45dxxt"
b = ''
for i in a:
    if i.isdigit():
        b = b + i 
print(b)    
```

字符串逆序
```python
temp = list(input().split())
for i in temp[::-1]:
    print(i,end=' ')
```

统计大写字母个数
```python
temp = input()
num = 0
for i in temp:
    if i.isupper():	#i == i.upper()不等价i.isupper()，后者的选择范围就是字母，前者把空格感叹也算上
        num += 1
print(num)   
```

求整数序列中出现最多的数字和次数
```python
temp = [int(i.strip()) for i in input().split()]
s2 = list()
for i in range(0,len(temp)):
    v = temp.count(temp[i])
    s2.append(v)
m = max(s2)
n = s2.index(m)
print("num:",temp[n],"time",m)  
#"{:d} {:d}".format(temp[n],m)
```

列表转换字典
```python
key_list = []
value_list = []
map = {}
for key,value in zip(key_list,value_list):
    map[key] = value
```

进制转化
```python
‘’’
bin(x)返回 2 进制字符串。
oct(x)返回 8 进制字符串。
hex(x)返回 16 进制字符串。
int(n, x) 将n转换为x进制的数
‘’’
n = int(input())
x = []
for i in range(n):
    x.append(oct(int(input(),16)))
for i in x:
    print(i[2:])
```

format用法
```python
<填充><对齐<>^><宽度> <分隔,><精度><类型e/E/F/%>
PI=3.14159265358979323
r = int(input())
s = PI*r*r
print("{0:.7f},{0},{1}".format(s,s+1))
#in:4
#out:50.2654825,50.26548245743669,51.26548245743669
```

输出内容和序号
```python
>>>seasons = ['Spring', 'Summer', 'Fall', 'Winter'] 
>>> list(enumerate(seasons)) 
[(0, 'Spring'), (1, 'Summer'), (2, 'Fall'), (3, 'Winter')] 
>>> list(enumerate(seasons, start=1)) # 下标从 1 开始 
[(1, 'Spring'), (2, 'Summer'), (3, 'Fall'), (4, 'Winter')]
>>>seq = ['one', 'two', 'three'] 
>>> for i, element in enumerate(seq): 
... print i, element 
... 
0 one 
1 two 
2 three
```

最小公倍数
```python
x = int(input())
y = int(input())
def lcm(x, y):
    a, b = x, y
    while y:
        x, y = y, x%y
    return a*b//x
print(lcm(x,y))
```

排序

归并排序
```python
def merge(s1,s2,s):
    """将两个列表是s1，s2按顺序融合为一个列表s,s为原列表"""
    # j和i就相当于两个指向的位置，i指s1，j指s2
    i = j = 0
    while i+j<len(s):        # j==len(s2)时说明s2走完了，或者s1没走完并且s1中该位置是最小的
        if j>=len(s2) or (i<len(s1) and s1[i]<s2[j]):
            s[i+j] = s1[i]
            i += 1
        else:
            s[i+j] = s2[j]
            j += 1

def merge_sort(s):
    """归并排序"""
    n = len(s)
    if n < 2:    # 剩一个或没有直接返回，不用排序
        return
    mid = n // 2      # 拆分
    s1 = s[0:mid]
    s2 = s[mid:n]
    merge_sort(s1)    # 子序列递归调用排序
    merge_sort(s2)
    merge(s1,s2,s)    # 合并

if __name__ == '__main__':
    a = input()
    s = [int(i.strip()) for i in input().split()]
    merge_sort(s)
    print(s)
```

快速排序
```python
def quick_sort(nums: list, left: int, right: int) -> None:
	if left < right:
		i = left
		j = right
		# 取第一个元素为比较量
		key = nums[left]
		while i != j:
			# 交替扫描和交换
			# 从右往左找到第一个比比较量小的元素，交换位置
			while j > i and nums[j] > key :
				j -= 1
			if j > i:
				# 如果找到了，进行元素交换
				nums[i] = nums[j]
				i += 1
			# 从左往右找到第一个比比较量大的元素，交换位置
			while i < j and nums[i] < key :
				i += 1
			if i < j:
				nums[j] = nums[i]
				j -= 1
		# 至此完成一趟快速排序，比较量的位置已经确定好了，就在i位置上（i和j)值相等
		nums[i] = key 
		# 以i为枢轴进行子序列元素交换
		quick_sort(nums, left, i-1)
		quick_sort(nums, i+1, right)		

# 测试代码
import random

data = [random.randint(-100, 100) for _ in range(10)]
quick_sort(data, 0, len(data) - 1)
print(data)
```


逆序对问题
```python
class Solution:
    def InversePairs(self, data):
        count = 0
        copy = []
        for i in data:
            copy.append(i)
        copy.sort()
        for i in range(len(copy)):
            count += data.index(copy[i])
            data.remove(copy[i])
        return count
a = int(input())        
num=[int(i.strip()) for i in input().split()]
answ = Solution().InversePairs(num)
print(answ)
```


递归：

Hanoi塔
```python
if __name__ == __main__:
    def hanoi(n,x,y,z):
        if n<0:
            print("请输入一个大于0的数！")
        elif n==1:
            print(x,"-->",z)
        else:
            hanoi(n-1,x,z,y)
            print(x,"-->",z)
            hanoi(n-1,y,x,z)
    n=int(input('请输入你想移动的柱子数n:'))
    step=2**n-1
    hanoi(n,'A','B','C')
    print("一共移动步数为：{}".format(step))
```

二分查找
```python
def binary_search(lisa,item):
    low = 0
    high = len(lisa) - 1
    
    while low <= high:
        mid = (low + high)//2
        guess = lisa[mid]
        if guess == item:
            return mid
        if guess > item:
            high = mid - 1
        else:
            low = mid + 1
    return None
'''    
my_list = [1, 3, 5, 7, 9]
print(binary_search(my_list,3))
'''
```

杨辉三角
```python
def triangle(n):
    l=[] #用来存储所有行的返回列表
    for i in range(n):
        if i==0:
            l.append([1])  # 第一行
        elif i==1:
            l.append([1,1])#第二行
        #第三行以后.....
        else:
            y = []  # 存储一行，每次清空
            for j  in range(i+1):
                if j==0 or j==i:
                    y.append(1)#行首和行末为1
                else:
                    y.append(l[i-1][j]+l[i-1][j-1])
            l.append(y)#放入所有行存储列表中
    return l
```
