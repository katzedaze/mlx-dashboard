from dataclasses import dataclass


DASHBOARD_PORT = 8502


@dataclass(frozen=True)
class ModelDef:
    id: str
    name: str
    description: str
    size: str


MODELS: tuple[ModelDef, ...] = (
    ModelDef("mlx-community/Llama-3.2-3B-Instruct-4bit", "Llama 3.2 3B", "軽量チャット", "3B"),
    ModelDef("mlx-community/Llama-3.1-8B-Instruct-4bit", "Llama 3.1 8B", "汎用高品質", "8B"),
    ModelDef("mlx-community/Qwen2.5-Coder-7B-Instruct-4bit", "Qwen2.5-Coder 7B", "コーディング", "7B"),
    ModelDef("mlx-community/Qwen2.5-7B-Instruct-4bit", "Qwen2.5 7B", "多言語対応", "7B"),
    ModelDef("mlx-community/DeepSeek-R1-Distill-Llama-8B-4bit", "DeepSeek-R1 8B", "推論特化", "8B"),
    ModelDef("mlx-community/Mistral-7B-Instruct-v0.3-4bit", "Mistral 7B", "汎用欧州モデル", "7B"),
)

MODEL_IDS: tuple[str, ...] = tuple(m.id for m in MODELS)


EVAL_CATEGORIES: dict[str, dict] = {
    "general_knowledge": {
        "name": "一般知識",
        "prompts": [
            "量子コンピュータの基本原理を、高校生にもわかるように500字以内で説明してください。",
            "第二次世界大戦の主要な転換点を3つ挙げ、それぞれの歴史的意義を簡潔に述べてください。",
            "光合成のプロセスを化学反応式とともに説明してください。",
        ],
    },
    "code_generation": {
        "name": "コード生成",
        "prompts": [
            "Pythonでフィボナッチ数列のメモ化再帰とイテレータの両方を実装し、パフォーマンスを比較するコードを書いてください。",
            "FastAPIを使って、SQLiteデータベースからTODOリストをCRUD操作するREST APIのコードを書いてください。",
            "Bashスクリプトで、指定ディレクトリ内の重複ファイルを検出し、一覧表示するツールを作成してください。",
        ],
    },
    "reasoning": {
        "name": "論理推論",
        "prompts": [
            "3人の裁判官がいます。Aは常に真実を言い、Bは常に嘘をつき、Cはランダムに答えます。1回の質問で、誰がAかを特定する方法を示してください。",
            "100人の囚人と100個の箱の問題：各箱にランダムに番号が入っており、各囚人は50個まで開けられます。全員が自分の番号を見つける確率を最大化する戦略を説明してください。",
            "あるカフェでは、コーヒー1杯300円、ケーキ1個500円です。10人のグループが合計5000円支払いました。コーヒーとケーキをそれぞれ何個注文したか、全パターンを求めてください。",
        ],
    },
    "creative_writing": {
        "name": "創作",
        "prompts": [
            "AIと人間の共存をテーマにした、200字以内の俳句を5つ作ってください。",
            "タイムトラベラーが江戸時代の日本に迷い込む短編小説の冒頭（500字）を書いてください。",
            "新しいプログラミング言語のキャッチーなマーケティングコピーを3案作成してください。",
        ],
    },
    "instruction_following": {
        "name": "指示遵守",
        "prompts": [
            "以下のルールに厳密に従って回答してください：1) 全て箇条書き 2) 各項目は10文字以内 3) 必ず5項目。テーマ：健康的な朝食",
            "JSONフォーマットのみで回答してください。キーは 'animal', 'color', 'number' の3つで、値はそれぞれ日本語の文字列、英語の文字列、1-100の整数です。5つの要素を持つ配列を返してください。",
            "次の文章を、1) 英語 2) フランス語 3) 中国語 に翻訳してください。各翻訳の後に信頼度（高/中/低）を付記してください。「桜の花が風に舞い散る様子は、日本の美意識の象徴です。」",
        ],
    },
}


SCORING_CRITERIA: dict[str, dict] = {
    "accuracy": {"name": "正確性", "weight": 0.25, "description": "事実の正確さ、コードの正しさ"},
    "completeness": {"name": "完全性", "weight": 0.20, "description": "質問への回答の網羅性"},
    "clarity": {"name": "明瞭性", "weight": 0.20, "description": "説明のわかりやすさ、構造の明確さ"},
    "creativity": {"name": "創造性", "weight": 0.15, "description": "独創性、表現力"},
    "code_quality": {"name": "コード品質", "weight": 0.10, "description": "コードの品質、可読性、効率性"},
    "speed": {"name": "速度", "weight": 0.10, "description": "応答速度（自動計算）"},
}

BENCHMARK_PROMPT = "Explain the concept of recursion in programming with a simple example in Python. Keep it under 200 words."
WARMUP_PROMPT = "Hello"

# Judge model for auto-scoring (use largest available MLX model)
JUDGE_MODEL = "mlx-community/Qwen2.5-32B-Instruct-4bit"

JUDGE_PROMPT_TEMPLATE = """あなたはLLMの回答品質を評価する専門家です。
以下のプロンプトに対するLLMの回答を、指定された基準で1〜5点のスコアで評価してください。

## プロンプト
{prompt}

## 回答
{response}

## 評価基準
- accuracy (正確性): 事実の正確さ、コードの正しさ (1=誤り多数, 5=完全に正確)
- completeness (完全性): 質問への回答の網羅性 (1=不十分, 5=完全に網羅)
- clarity (明瞭性): 説明のわかりやすさ、構造の明確さ (1=理解困難, 5=非常に明瞭)
- creativity (創造性): 独創性、表現力 (1=平凡, 5=非常に独創的)
- code_quality (コード品質): コードの品質、可読性、効率性。コードがない場合は3を付けてください (1=低品質, 5=高品質)

## 出力形式
必ず以下のJSON形式のみで回答してください。説明や追加テキストは不要です。
{{"accuracy": <1-5>, "completeness": <1-5>, "clarity": <1-5>, "creativity": <1-5>, "code_quality": <1-5>}}"""
