from sklearn.model_selection import train_test_split
from main import TRAIN_FILE_NAME
import pandas as pd
import numpy as np
import operator
from collections import Counter


def split_dataset(filename):
    with open(filename, "r"):
        dataset = pd.read_csv(filename, header=0, sep=';')
    wine = np.array(dataset, dtype=float)
    data, label = np.hsplit(wine, [11, 12])[0], np.hsplit(wine, [11, 12])[1]
    return data, label


class DecisionTree(object):
    def __init__(self, max_depth):
        self.features = [None for _ in range(2 ** (max_depth - 1) - 1)]
        self.values = [None for _ in range(2 ** (max_depth - 1) - 1)]
        self.labels = [None for _ in range(2 ** max_depth - 1)]
        self.max_depth = max_depth

    def set_root(self, feature, value):
        self.features[0] = feature
        self.values[0] = value

    def set_left_child(self, parent_index, feature, value):
        self.features[(2 * parent_index) + 1] = feature
        self.values[(2 * parent_index) + 1] = value

    def set_right_child(self, parent_index, feature, value):
        self.features[(2 * parent_index) + 2] = feature
        self.values[(2 * parent_index) + 2] = value

    def fit(self, _X_train, _y_train):
        def gini_impurity(ds, index):
            orderedbycolumnds = ds[np.array(ds[:, index]).argsort()]
            ts, l = np.hsplit(orderedbycolumnds, [11, 12])[0], np.hsplit(orderedbycolumnds, [11, 12])[1]
            distinct = list(set(list(orderedbycolumnds[:, index])))
            distinct.sort()
            distinctlabels = list(set(list(l[:, 0])))
            med = [(distinct[i] + distinct[i + 1]) / 2 for i in range(len(distinct) - 1)]
            gini = []
            for m in med:
                rows = max([i for i, row in zip(range(ts.shape[0]), ts) if row[index] <= m]) + 1
                impurityleaftrue = 1 - sum([(list(l[:rows, 0]).count(i) / rows) ** 2 for i in distinctlabels])
                impurityleaffalse = 1 - sum(
                    [(list(l[rows:, 0]).count(i) / (len(l) - rows)) ** 2 for i in distinctlabels])
                gini.append([(rows / len(l)) * impurityleaftrue + ((len(l) - rows) / len(l)) * impurityleaffalse, m])
            return gini[list(np.array(gini)[:, 0]).index(min(np.array(gini)[:, 0]))]
        _x, _y = _X_train, _y_train
        subdatasets = [None for _ in range(2 ** self.max_depth - 1)]
        subdatasets[0] = np.hstack((_x, _y))
        for j, d in zip(range(2 ** (self.max_depth - 1) - 1), subdatasets):
            g = [gini_impurity(d, i) for i in range(_X_train.shape[1])]
            m = g[list(np.array(g)[:, 0]).index(min(np.array(g)[:, 0]))]
            self.features[j] = list(g).index(m)
            self.values[j] = m[1]
            subdatasets[2 * j + 1] = np.array([list(rows) for rows in subdatasets[j] if operator.le(rows[self.features[j]], self.values[j])])
            subdatasets[2 * j + 2] = np.array([list(rows) for rows in subdatasets[j] if operator.gt(rows[self.features[j]], self.values[j])])

        for i in range(2 ** (self.max_depth - 1) - 1, 2 ** self.max_depth - 1):
            self.labels[i], _ = Counter(list((np.hsplit(subdatasets[i], [11, 12])[1])[:, 0])).most_common(1)[0]

    def predict(self, _x_test):
        labels = []
        for j in range(len(_x_test)):
            i = 0
            while self.labels[i] is None:
                i = 2 * i + 2 if operator.le(_x_test[j][self.features[i]], self.values[i]) else 2 * i + 1
            labels.append(self.labels[i])
        return labels

    def precision_score(self, _x_test, _y_test):
        # Precision = (TruePositives_1 + TruePositives_2) / ((TruePositives_1 + TruePositives_2) + (FalsePositives_1
        # + FalsePositives_2) )
        return [i == j for i, j in zip(self.predict(_x_test), _y_test)].count(True) / len(_y_test)

    def recall_score(self, _x_test, _y_test):
        # Recall = (TruePositives_1 + TruePositives_2) / ((TruePositives_1 + TruePositives_2) + (FalseNegatives_1 +
        # FalseNegatives_2))
        return [i == j for i, j in zip(self.predict(_x_test), _y_test)].count(True) / len(_y_test)

    def f_measure_score(self, _x_test, _y_test):
        precision, recall = self.precision_score(_x_test, _y_test), self.recall_score(_x_test, _y_test)
        return (2 * precision * recall) / (precision + recall)


if __name__ == '__main__':
    df, label = split_dataset(TRAIN_FILE_NAME)
    X_train, X_test, y_train, y_test = train_test_split(df, label, test_size=0.20, random_state=101)
    t = DecisionTree(max_depth=4)
    t.fit(X_train, y_train)
    print(t.features)
    print(t.values)
    print(t.labels)

    # print(t.predict(X_test))
    # print(t.f_measure_score(X_test, list(int(i) for i in y_test[:, 0])))
