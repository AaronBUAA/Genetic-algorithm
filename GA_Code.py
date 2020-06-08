import datetime
import random
from math import exp
from statistics import mean


def init(k, filename):
    """
    初始化函数，包括读取数据、定义参数等
    :param k: 初始个体数量，可以自行设定，选定不同个数的初始个体构成第一代种群
    :param filename: 读入数据文件名，这里是txt类型文件
    :return: Y, n, c, p, init_population分别对应 补贴上限、企业个数、企业成本、企业间收益和初始种群
    """
    def Read_list():
        """
        从txt文件格式下读取数据并将其转化为二维列表
        数据文件第一行是补贴上限Y，第二行是企业数量n，后面是对应的n个成本，以及p矩阵nxn。收益率ri都取0.1。
        :return:  按照上述格式返回数据
        """
        file = open(filename, "r")
        list_row = file.readlines()
        list_source = []
        for i in range(len(list_row)):
            column_list = list_row[i].strip().split("\t")  # 每一行split后是一个列表
            list_source.append(column_list)  # 在末尾追加到list_source
        for i in range(len(list_source)):  # 行数
            for j in range(len(list_source[i])):  # 列数
                list_source[i][j] = float(list_source[i][j])
        file.close()

        return list_source

    temp_data = Read_list()
    Y = temp_data[0][0]  # 企业补贴的上限值
    n = int(temp_data[1][0])  # 企业的个数
    init_population = []  # 初始种群
    temp = []
    c = []  # 每个企业加入平台的成本
    p = []  # 企业i从企业j获得的信息共享收益
    count = 0  # 生成初始个体的循环计数变量

    for i in range(2, 2 + n):  # 读取企业成本
        c.append(temp_data[i][0])

    for i in range(2 + n, len(temp_data)):  # 读取企业间的收益关系
        p.append(temp_data[i])

    while count < k:  # 生成目标函数满足一定要求的初始解，构成初代种群
        for j in range(n):
            temp.append(random.randint(0, 1))

        fx, _ = total_benefit(temp, n, p, c, Y)
        if fx > 10:
            init_population.append(temp)
            print(count + 1)
            count += 1

        temp = []

    return Y, n, c, p, init_population


def total_benefit(individual, n, p, c, Y):
    """
    计算目标函数，也就是平台的收益和补贴之和
    :param individual: 输入个体，这里注意是每一个的个体，不是种群
    :param n: 企业个数，也就是每个个体的长度
    :param p: 企业间的收益情况
    :param c: 企业加入平台的成本
    :param Y: 平台补贴的上限
    :return: 返回计算后的目标函数（平台收益）
    """
    company_index = [i for i in range(len(individual)) if individual[i] == 1]
    benefit = [0] * n  # 每个公司从其他公司获得的收益
    zy = [0] * n  # 平台对各个企业的收费/补贴情况，其中正数代表收费、负数代表补贴。

    for i in company_index:
        for j in company_index:
            benefit[i] += p[i][j]

        if benefit[i] >= c[i] * 1.1:
            zy[i] = (benefit[i] / 1.1) - c[i]
        else:
            zy[i] = benefit[i] - c[i] * 1.1

    total_b = sum([x for x in zy])
    temp = sum([i for i in zy if i < 0])

    if temp < -Y:  # 加入惩罚项，如果补贴超过最大上限，那么以十倍的代价进行补偿
        total_b += 10 * (temp + Y)

    return total_b, zy


def crossover_or_mutation(population, n, p, c, Y):
    """
    交叉或变异函数，即新个体产生方式。可以通过以上两种方式产生、随机选取，概率为50％。通过轮盘赌博方式选取父母，然后生成两个新个体
    :param population: 输入种群，这里注意是种群不是个体
    :param n: 企业的个数
    :param p: 企业间的收益情况
    :param c: 企业加入平台的成本
    :param Y: 补贴上限
    :return: 返回繁衍后的两个新个体
    """
    def choose_male_and_female(population, n, p, c, Y):
        """
        生成进行交叉/变异的父代和母代个体，利用轮盘赌博的形式选择概率较大的个体作为父母
        :param population: 输入种群
        :param n: 企业的个数
        :param p: 企业间的收益情况
        :param c: 企业加入平台的成本
        :param Y: 补贴上限
        :return: 返回选中的父母
        """
        fitness_distribution = []  # 适应度分布列表
        male = []
        female = []
        fx, fitness = metropolis(population, n, p, c, Y)  # 计算当前种群的适应度函数
        sum_fitness = sum(fitness)

        for i in range(len(fitness)):
            fitness_distribution.append(sum(fitness[:i]) / sum_fitness)
        fitness_distribution.append(1)  # 得到适应度值的分布函数

        rand_index = random.uniform(0, 1)
        for i in range(len(fitness)):
            if fitness_distribution[i] < rand_index < fitness_distribution[i + 1]:
                male = population[i]  # 生成父亲

        rand_index = random.uniform(0, 1)
        for i in range(len(fitness)):
            if fitness_distribution[i] < rand_index < fitness_distribution[i + 1]:
                female = population[i]  # 生成母亲

        return male, female

    male_individual, female_individual = choose_male_and_female(population, n, p, c, Y)

    tou_zi = random.randint(0, 1)  # 骰子，随机生成0/1

    if tou_zi == 0:  # 如果骰子为0，则通过交叉产生下一代
        temp = random.randint(0, n)
        new_individual1 = male_individual[:temp] + female_individual[temp:]
        new_individual2 = female_individual[:temp] + male_individual[temp:]
    else:  # 如果骰子为1，则通过变异产生下一代
        a, b = random.randint(0, n), random.randint(0, n)
        random_left, random_right = min(a, b), max(a, b)
        rever = male_individual[random_left:random_right]
        new_individual1 = male_individual[:random_left] + rever + male_individual[random_right:]

        a, b = random.randint(0, n), random.randint(0, n)
        random_left, random_right = min(a, b), max(a, b)
        rever = female_individual[random_left:random_right]
        new_individual2 = female_individual[:random_left] + rever + female_individual[random_right:]

    return new_individual1, new_individual2


def metropolis(population, n, p, c, Y):
    """
    适应度函数，构建目标函数和适应度值成正比的函数
    :param population: 输入种群
    :param n: 企业的个数
    :param p: 企业间的收益情况
    :param c: 企业加入平台的成本
    :param Y: 补贴上限
    :return: 返回种群的目标函数和适应度值
    """
    fx = [0] * len(population)  # 个体的目标函数值
    fitness = []  # 个体的适应度

    for i in range(len(population)):
        fx[i], _ = total_benefit(population[i], n, p, c, Y)

    max_fx = max(fx)  # 适应度值最大值
    avg_fx = mean(fx)  # 适应度均值

    for i in range(len(fx)):
        fitness.append(exp((fx[i] - max_fx) / (max_fx - avg_fx)))

    return fx, fitness


def GA():
    k = 5  # k的初始种群的个体数，设置为1000
    Y, n, c, p, init_population = init(k, "data_100.txt")
    best_fx = []  # 保存最大的目标函数值
    best_answer = []  # 保存最优解对应的企业情况
    gen = 0  # 遗传算法循环的代数
    next_population = init_population

    while gen < 60:  # 遗传60代
        while len(next_population) < 60:  # 每一代种群的个体数控制在60以内
            new_list = []
            new_individual1, new_individual2 = crossover_or_mutation(next_population, n, p, c, Y)
            next_population.append(new_individual1)
            next_population.append(new_individual2)

            for i in next_population:  # 保证种群中的个体没有重复
                if i not in new_list:
                    new_list.append(i)
            next_population = new_list

        count = 0
        del_index = []
        fx, fitness = metropolis(next_population, n, p, c, Y)

        while count < 30:  # 随机选取种群中的个体，与随机生成的适应度进行比较，如果小于就淘汰，重复30次
            rand = random.randint(0, len(next_population) - 1)
            rand_index = random.uniform(0, 0.8)

            if fitness[rand] < rand_index:
                del_index.append(rand)

            count += 1

        temp = []

        for i in range(len(next_population)):
            if i not in del_index:
                temp.append(next_population[i])

        next_population = temp
        fx = [0] * len(next_population)

        for i in range(len(next_population)):
            fx[i], _ = total_benefit(next_population[i], n, p, c, Y)
        best_fx.append(max(fx))

        print('当前的最优结果为', max(fx))
        for i in range(len(fx)):
            if fx[i] == max(fx):
                best_answer.append(next_population[i])
                print('此时的加入企业为：', next_population[i])
                _, temp = total_benefit(next_population[i], n, p, c, Y)
                print('对应的收费/补贴情况为：', temp)

        gen += 1
        print('代数', gen)

    return best_fx, best_answer


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    n = 10
    avg_fx = [0] * n
    best_fx = [0] * n
    for i in range(10):
        temp_best_fx, temp_best_answer = GA()
        best_fx[i] = max(temp_best_fx)
        avg_fx[i] = mean(temp_best_fx)

    print('遗传算法计算10次的平均解分别为：')
    for i in range(len(avg_fx)):
        print(avg_fx[i])

    print('遗传算法计算10次的最好解分别为：')
    for i in range(len(best_fx)):
        print(best_fx[i])

    end_time = datetime.datetime.now()
    print('遗传算法计算10次的计算时间为：', end_time - start_time)
