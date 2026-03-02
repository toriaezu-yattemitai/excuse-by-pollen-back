# 花粉症・限界突破エクスキュース(言い訳)ジェネレーター Backend
- ドキュメント最終更新 : 2026/03/01

## Get started
- macOS / Linux
1. 仮想環境の構築
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. `.env` を作成
```bash
cp .env.sample .env
```
3. 開発サーバーの起動
```bash
PYTHONPATH=src uvicorn app.main:app --reload --host 0.0.0.0
```

- Windows (PowerShell)
1. 仮想環境の構築
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. `.env` を作成
```powershell
Copy-Item .env.sample .env
```
3. 開発サーバーの起動
```powershell
$env:PYTHONPATH="src"
uvicorn app.main:app --reload --host 0.0.0.0
```



## エンドポイント
- `GET /` -> `{"message":"Hello World"}`
