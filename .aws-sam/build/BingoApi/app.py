import os, json, time
import boto3
from decimal import Decimal

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['TABLE_NAME'])

DEFAULT_LABELS = [
    "マグロの解体を見た",
    "包丁5万円以上を発見",
    "外国人観光客に話しかけられる",
    "「豊洲」という単語を耳にする",
    "変な魚の漢字を見つける",
    "海鮮丼の呼び込みに声をかけられる",
    "築地本願寺で仏像や建物を撮る",
    "波除神社の狛犬を見つける",
    "卵焼き専門店を発見",
    "「市場価格○○円」看板を見つける",
    "干物や乾物を冷やかす",
    "巨大なマグロの頭に遭遇",
    "「場外市場」の文字を撮る",
    "漆器や食器の店を発見",
    "築地でサウナ関連ワードを見つける",
    "昭和感あるおじさんを目撃",
    "カニやエビが山積みになっている",
    "「マグロの中落ち」という文字を発見",
    "カツオ節を削る実演を見る",
    "外国人が爆買いしているのを見る",
    "魚以外の変なグルメ（土産用もんじゃ煎餅など）",
    "1万円以上の海苔を発見",
    "漫画やテレビで見たことあるキャラに似た観光客",
    "市場で猫を見つける",
    "魚屋の兄ちゃんに威勢よく声をかけられる",
]

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Content-Type": "application/json; charset=utf-8",
}

def to_py(x):
    if isinstance(x, list):
        return [to_py(i) for i in x]
    if isinstance(x, dict):
        return {k: to_py(v) for k, v in x.items()}
    if isinstance(x, Decimal):
        # 整数ならint、そうでなければfloat
        return int(x) if x == x.to_integral_value() else float(x)
    return x

def _resp(code, body):
    return {"statusCode": code, "headers": HEADERS, "body": json.dumps(body, ensure_ascii=False)}


def _get_or_init(game_id):
    r = table.get_item(Key={"gameId": game_id})
    if "Item" in r:
        return r["Item"]
    # init with defaults
    item = {
        "gameId": game_id,
        "labels": DEFAULT_LABELS,
        "marks": [0] * 25,
        "updatedAt": int(time.time()),
    }
    table.put_item(Item=item)
    return item


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("requestContext", {}).get("http", {}).get("path")
    params = event.get("pathParameters") or {}
    game_id = params.get("id")

    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    if method == "GET" and game_id:
        item = _get_or_init(game_id)
        p = to_py(item)   # ←ここでDecimalを変換
        return _resp(200, {
            "labels": p["labels"],
            "marks": p["marks"],
            "updatedAt": p["updatedAt"]
        })

    if method == "POST" and game_id and path.endswith("/toggle"):
        try:
            body = json.loads(event.get("body") or "{}")
            idx = int(body.get("index"))
            if idx < 0 or idx >= 25:
                return _resp(400, {"error": "index out of range"})
        except Exception:
            return _resp(400, {"error": "invalid body"})

        item = _get_or_init(game_id)
        marks = list(item.get("marks", [0]*25))
        marks[idx] = 0 if marks[idx] == 1 else 1
        ts = int(time.time())
        table.update_item(
            Key={"gameId": game_id},
            UpdateExpression="SET marks = :m, updatedAt = :t",
            ExpressionAttributeValues={":m": marks, ":t": ts},
        )
        return _resp(200, {"marks": marks, "updatedAt": ts})

    return _resp(404, {"error": "not found"})