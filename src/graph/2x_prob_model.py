import math
import seaborn as sns 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def R(x, height, alpha, beta):
    return math.exp(-1 * height * math.pow(x/alpha, beta))

def r(x, alpha, beta):
    return math.exp(-1 * math.pow(x/alpha, beta))

def calc_r(height, alpha, beta):
    ret = 1
    for i in range(1, height+1):
        ret *= r(math.pow(2, i)+1, alpha, beta)
    return ret

def worst_alpha_height(height, n, k, beta, alpha_max):
    ret = []
    for alpha in range(1, alpha_max):
        twice_success = R(1, height, alpha, beta)*R(2, height, alpha, beta)
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(twice_success, i) * math.pow(1 - twice_success, n-i)

        ret.append(k_access_success)
    return ret

def best_alpha_height(height, n, k, beta, alpha_max):
    ret = []
    for alpha in range(1, alpha_max):
        twice_success = calc_r(height, alpha, beta)
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(twice_success, i) * math.pow(1 - twice_success, n-i)
        ret.append(k_access_success)
    return ret

def worst_k_height(height, n, beta, alpha, k_max):
    ret = []
    for k in range(0, k_max):
        twice_success = R(1, height, alpha, beta)*R(2, height, alpha, beta)
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(twice_success, i) * math.pow(1 - twice_success, n-i)

        ret.append(k_access_success)
    return ret

def best_k_height(height, n, beta, alpha, k_max):
    ret = []
    for k in range(0, k_max):
        twice_success = calc_r(height, alpha, beta)
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(twice_success, i) * math.pow(1 - twice_success, n-i)

        ret.append(k_access_success)
    return ret

if __name__ == "__main__":
    a_max = 300
    k_max = 300
    b = 1
    a = 100
    n = 128
    k = 80

    worst = []
    best = []
    for i in range(2, 30):
        print("Calculating height ", i)
        worst.append(worst_alpha_height(height=i, n=n, k=k, beta=b, alpha_max=a_max))
        best.append(best_alpha_height(height=i, n=n, k=k, beta=b, alpha_max=a_max))

        # worst.append(worst_k_height(height=i, n=n, beta=b, alpha=a, k_max=k_max))
        # best.append(best_k_height(height=i, n=n, beta=b, alpha=a, k_max=k_max))


    worst_data = np.array(worst)
    worst_df = pd.DataFrame(worst_data)
    best_data = np.array(best)
    best_df = pd.DataFrame(best_data)

    font_path = "/Users/afiqnaufal/Library/Fonts/Oshidashi-M-Gothic-TT.ttf"
    prop = fm.FontProperties(fname=font_path)

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    sns.heatmap(worst_df)
    ax1.set_title('最悪なアクセス分布でのデュプリケート発生確率\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}', fontproperties=prop)
    ax1.set_xlabel(r'$\alpha$')

    # ax1.set_title('最悪なアクセス分布でのデュプリケート発生確率\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}', fontproperties=prop)
    # ax1.set_xlabel('k')

    ax1.set_ylabel('H')
    fig.savefig("iot prob.png")

    fig = plt.figure()
    ax2 = fig.add_subplot(1, 1, 1)
    sns.heatmap(best_df)
    ax2.set_title('ベストなアクセス分布でのデュプリケート発生確率\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}', fontproperties=prop)
    ax2.set_xlabel(r'$\alpha$')

    # ax2.set_title('ベストなアクセス分布でのデュプリケート発生確率\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}', fontproperties=prop)
    # ax2.set_xlabel('k')

    ax2.set_ylabel('H')
    fig.savefig("attacker prob.png")

    plt.show()
