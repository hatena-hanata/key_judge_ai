from sklearn.datasets import load_digits
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV

import pandas as pd



def get_valiables(df):

    # 曲名削除
    df = df.drop('name', axis=1)

    # keyをラベルエンコーディング
    le = LabelEncoder()
    le.fit(df['key'])
    df['key'] = le.transform(df['key'])

    # X, yを取得
    y = df['key']
    X = df.drop('key', axis=1)
    return X, y


def get_diatonic_chord(key_str):
    chord_lst = [
        'C_Major',
        'C_minor',
        'C#/D♭_Major',
        'C#/D♭_minor',
        'D_Major',
        'D_minor',
        'D#/E♭_Major',
        'D#/E♭_minor',
        'E_Major',
        'E_minor',
        'F_Major',
        'F_minor',
        'F#/G♭_Major',
        'F#/G♭_minor',
        'G_Major',
        'G_minor',
        'G#/A♭_Major',
        'G#/A♭_minor',
        'A_Major',
        'A_minor',
        'A#/B♭_Major',
        'A#/B♭_minor',
        'B_Major',
        'B_minor',
    ]
    # ダイアトニックコード間の間隔
    Major_step = [0, 5, 4, 1, 4, 5, 4]
    # 間隔、ナチュラルマイナー・スケールで VmをVに変更（頻出なので）
    minor_step = [0, 4, 1, 5, 3, 2, 4]
    diatonic_chord_lst = []
    # 長調
    if key_str.split('_')[-1] == 'Major':
        c_index = chord_lst.index(key_str)
        for step in Major_step:
            c_index = (c_index + step) % 24
            diatonic_chord_lst.append(chord_lst[c_index])
    # 短調
    else:
        c_index = chord_lst.index(key_str)
        for step in minor_step:
            c_index = (c_index + step) % 24
            diatonic_chord_lst.append(chord_lst[c_index])

    return diatonic_chord_lst


def decrease_non_diatonic_chord(df, ratio):
    # コードのカラムリスト
    col_lst = df.columns[2:]

    # 小数に対応させる
    diatonic_col_dict = {}
    for col in col_lst:
        df[col] = df[col].astype('float')
        diatonic_col_dict[col] = get_diatonic_chord(col)

    # 行ごとに処理
    for index, row in df.iterrows():
        diatonic_chord_lst = diatonic_col_dict[row[1]]
        for col in col_lst:
            if col not in diatonic_chord_lst:
                df.at[index, col] *= ratio

    return df


def drop_sum_zero(df):
    # コードをカウントできていないもの（sum=0）をdrop
    df['sum'] = df.sum(axis=1)
    df = df[df['sum'] != 0]
    df = df.drop('sum', axis=1)
    return df


def main():
    df = pd.read_csv('./html/train.csv', encoding='shift-jis')

    # 欠損をdrop
    df = drop_sum_zero(df)

    # ダイアトニックコードじゃないコードを弱める
    # df = decrease_non_diatonic_chord(df, ratio=0.5)

    # dfから説明変数と目的変数に分ける
    X, y = get_valiables(df)

    # 訓練用分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    # グリッドサーチ
    tuned_parameters = [
        {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        {'C': [1, 10, 100, 1000], 'kernel': ['rbf'], 'gamma': [0.001, 0.0001]},
        {'C': [1, 10, 100, 1000], 'kernel': ['poly'], 'degree': [2, 3, 4], 'gamma': [0.001, 0.0001]},
        {'C': [1, 10, 100, 1000], 'kernel': ['sigmoid'], 'gamma': [0.001, 0.0001]}
    ]
    score = 'f1'
    clf = GridSearchCV(
        SVC(),  # 識別器
        tuned_parameters,  # 最適化したいパラメータセット
        cv=5,  # 交差検定の回数
        scoring='%s_weighted' % score)  # モデルの評価関数の指定
    clf.fit(X_train, y_train)

