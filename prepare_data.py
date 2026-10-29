import json
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_FILE = Path('data.csv')
OUT = Path('data/bert')

def main():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.read_csv('https://huggingface.co/datasets/Johnson8187/Chinese_Multi-Emotion_Dialogue_Dataset/resolve/main/data.csv')
    if not {'text', 'emotion'}.issubset(df.columns):
        raise ValueError(f'需要 text, emotion 欄位，實際為 {list(df.columns)}')
    df = df[['text', 'emotion']].dropna().copy()
    df['text'] = df['text'].astype(str).str.strip()
    df['emotion'] = df['emotion'].astype(str).str.strip()
    df = df[(df.text != '') & (df.emotion != '')].drop_duplicates()
    labels = sorted(df.emotion.unique().tolist())
    label2id = {name: i for i, name in enumerate(labels)}
    df['labels'] = df.emotion.map(label2id).astype(int)
    train, valid = train_test_split(df, test_size=.2, random_state=42, stratify=df.labels)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, part in [('train', train), ('valid', valid)]:
        with (OUT / f'{name}.jsonl').open('w', encoding='utf-8') as f:
            for row in part.itertuples():
                f.write(json.dumps({'sentences': row.text, 'labels': int(row.labels)}, ensure_ascii=False) + '\n')
    (OUT / 'label2id.json').write_text(json.dumps(label2id, ensure_ascii=False, indent=2), encoding='utf-8')
    print('類別對照:', label2id)
    print('訓練筆數:', len(train), '驗證筆數:', len(valid))

if __name__ == '__main__':
    main()
