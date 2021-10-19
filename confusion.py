tp = [14, 9, 9, 9, 9, 19, 11, 11, 11, 11, 7, 24]
fp = [0, 0, 0, 3, 0, 0, 1, 0, 0, 1, 0, 0]
fn = [0, 0, 2, 0, 4, 0, 0, 0, 1, 0, 0, 0]
tn = [12, 9, 9, 6, 4, 0, 8, 8, 7, 9, 7, 0]


def precision(tp, fp):
    return (tp / (tp+fp)) * 100


def recall(tp, fn):

    return (tp / (tp+fn)) * 100


def accuracy(tp, fp, fn, tn):
    return ((tp+tn) / (tp+fp+fn+tn)) * 100


total = 0
for i in range(0, 12):
    # print("{}. Precision : {}%".format(i+1, precision(tp[i], fp[i])))
    # print("{}. recall : {}%".format(i+1, recall(tp[i], fn[i])))
    print("{}. accurary : {}%".format(
        i+1, accuracy(tp[i], fp[i], fn[i], tn[i])))
    total += accuracy(tp[i], fp[i], fn[i], tn[i])

print(total)
