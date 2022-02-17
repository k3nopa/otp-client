import math
import seaborn as sns 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

access = 1

def recv_alpha_height(height, n, k, beta, alpha_max):
    ret = []
    for alpha in range(1, alpha_max):
        first_access_success = math.exp(-1 * height * math.pow(access/alpha, beta))
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(first_access_success, i) * math.pow(1 - first_access_success, n-i)

        ret.append(k_access_success)
    return ret

def adv_alpha_height(height, n, k, beta, alpha_max):
    k = 80
    p = 1/math.pow(2, height - 1)
    ret = []
    for alpha in range(1, alpha_max):
        first_access_success = math.exp(-1 * height * math.pow(access/alpha, beta))
        k_access_success = 0
        for i in range(k, n+1):
            prob_x = math.comb(n, i) * math.pow(first_access_success, i) * math.pow(1 - first_access_success, n-i)
            prob_k = 0
            for j in range(k, i+1):
                prob_k += math.comb(i, j) * math.pow(p, j) * math.pow(1-p, i-j)
            k_access_success += prob_x * prob_k
            
        ret.append(k_access_success)
    return ret

def recv_k_height(height, n, beta, alpha, k_max):
    ret = []
    for k in range(0, k_max):
        first_access_success = math.exp(-1 * height * math.pow(access/alpha, beta))
        k_access_success = 0
        for i in range(k, n+1):
            k_access_success += math.comb(n, i) * math.pow(first_access_success, i) * math.pow(1 - first_access_success, n-i)

        ret.append(k_access_success)
    return ret

def adv_k_height(height, n, beta, alpha, k_max):
    p = 1/math.pow(2, height - 1)
    ret = []
    for k in range(0, k_max):
        first_access_success = math.exp(-1 * height * math.pow(access/alpha, beta))
        k_access_success = 0
        for i in range(k, n+1):
            prob_x = math.comb(n, i) * math.pow(first_access_success, i) * math.pow(1 - first_access_success, n-i)
            prob_k = 0
            for j in range(k, i+1):
                prob_k += math.comb(i, j) * math.pow(p, j) * math.pow(1-p, i-j)
            k_access_success += prob_x * prob_k
            
        ret.append(k_access_success)
    return ret

if __name__ == "__main__":
    a_max = 300
    k_max = 300
    b = 1
    a = 100
    n = 256
    k = 80

    recv = []
    adv = []
    for i in range(1, 30):
        print("Calculating height ", i)
        recv.append(recv_alpha_height(height=i, n=n, k=k, beta=b, alpha_max=a_max))
        adv.append(adv_alpha_height(height=i, n=n, k=k, beta=b, alpha_max=a_max))

        # recv.append(recv_k_height(height=i, n=n, beta=b, alpha=a, k_max=k_max))
        # adv.append(adv_k_height(height=i, n=n, beta=b, alpha=a, k_max=k_max))

    recv_data = np.array(recv)
    adv_data = np.array(adv)
    recv_df = pd.DataFrame(recv_data)
    adv_df = pd.DataFrame(adv_data)

    font_path = "/Users/afiqnaufal/Library/Fonts/Oshidashi-M-Gothic-TT.ttf"
    prop = fm.FontProperties(fname=font_path)
    fig = plt.figure()

    ax1 = fig.add_subplot(1, 1, 1)
    sns.heatmap(recv_df)

    # ax1.set_title('IoT 2nd success rate\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}')
    ax1.set_title('IoT側で決定木への1回目成功取得率\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}', fontproperties=prop)
    ax1.set_xlabel(r'$\alpha$')

    # ax1.set_title('IoT success rate\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}')
    # ax1.set_title('IoT側で決定木への1回目成功取得率\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}', fontproperties=prop)
    # ax1.set_xlabel('K')

    ax1.set_ylabel('H')
    fig.savefig("receiver prob.png")

    fig = plt.figure()

    ax2 = fig.add_subplot(1, 1, 1)
    sns.heatmap(adv_df)
    # ax2.set_title('Attacker 2nd success rate\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}')
    ax2.set_title('攻撃者側で決定木への1回目成功取得率\n' + r'$\beta$=' + str(b) + ' k=' + str(k) + f' N={n}', fontproperties=prop)
    ax2.set_xlabel(r'$\alpha$')

    # ax2.set_title('Attacker success rate\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}')
    # ax2.set_title('攻撃者側で決定木への1回目成功取得率\n' + r'$\beta$=' + str(b) + r' $\alpha$=' + str(a) + f' N={n}', fontproperties=prop)
    # ax2.set_xlabel('K')

    ax2.set_ylabel('H')
    fig.savefig("attacker prob.png")

    plt.show()
