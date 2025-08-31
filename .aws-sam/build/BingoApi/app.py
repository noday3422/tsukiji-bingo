import os, json, time
import boto3
from decimal import Decimal
import random

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['TABLE_NAME'])

'''
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
DEFAULT_LABELS = [
    "スカイツリーを遠くに発見する",
    "山手線の新型車両E235系を見かける",
    "路地裏で寝ている猫を見つける",
    "昭和の看板建築を見かける",
    "カフェでパソコンを開いて作業している人を見る",
    "外国人が地図アプリを見ながら歩いている",
    "シャッター商店街を通りかかる",
    "自販機でご当地っぽい飲み物を見つける",
    "線路沿いで写真を撮っている人を見る",
    "タワーマンション建設現場を見かける",
    "レトロな銭湯の煙突を見つける",
    "電動キックボードに乗っている人を見る",
    "大きな公園で大道芸をしているのを見かける",
    "長い行列のラーメン店を発見する",
    "ビルの隙間に小さな神社を見つける",
    "自転車でUberEatsのバッグを背負った人を見かける",
    "古い公衆電話を発見する",
    "商店街で路上飲みをしている人を見る",
    "赤提灯が出ている横丁を見つける",
    "海外チェーン店の新店舗を見かける",
    "壁にスプレーアート（落書き）を発見する",
    "団地のベランダに大量の洗濯物が干されているのを見る",
    "お祭り太鼓の練習音を耳にする",
    "銅像やモニュメントを見つける",
    "交差点でパフォーマンスしている人を見る",
]
'''
DEFAULT_LABELS = [
    "マグロのせりを見学した",
    "巨大な冷蔵庫の説明を聞いた",
    "豊洲市場で寿司を食べた",
    "外国人観光客が写真を撮っているのを見る",
    "「豊洲市場」という看板を撮影",
    "マグロの頭を展示で発見",
    "青果棟で珍しい野菜を見つける",
    "水産棟の競り場で大声を聞く",
    "卵焼き専門店を見つける",
    "高級包丁を試しに持ってみる",
    "1万円以上する海鮮丼を発見",
    "冷凍マグロの塊を見た",
    "ターレ（小型運搬車）が走り抜けるのを目撃",
    "豊洲市場からレインボーブリッジを眺める",
    "市場で働く人に威勢よく声をかけられる",
    "カニやエビが山積みになっている",
    "「中落ち」の文字を発見",
    "外国人が大量にお土産を買っている",
    "寿司ネタの産地を学べるパネルを見る",
    "豊洲市場限定グルメを食べる",
    "高級海苔を発見する",
    "テレビや漫画で見た市場シーンを思い出す",
    "市場の屋上緑化エリアに行く",
    "場内で猫ではなくカモメを見つける",
    "豊洲市場PRキャラクターを発見する",
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

    # シャッフル
    if method == "POST" and game_id and path.endswith("/shuffle"):
        item = _get_or_init(game_id)
        labels = list(item["labels"])
        marks = list(item["marks"])
        
        # ラベルとマークをペアにしてシャッフル
        combined = [{"label": l, "mark": m} for l, m in zip(labels, marks)]
        random.shuffle(combined)
        
        labels = [c["label"] for c in combined]
        marks = [c["mark"] for c in combined]

        ts = int(time.time())
        table.update_item(
            Key={"gameId": game_id},
            UpdateExpression="SET labels=:l, marks=:m, updatedAt=:t",
            ExpressionAttributeValues={":l": labels, ":m": marks, ":t": ts},
        )
        return _resp(200, {"labels": labels, "marks": marks, "updatedAt": ts})

    # リセット（初期labelsと空のmarksに戻す）
    if method == "POST" and game_id and path.endswith("/reset"):
        item = _get_or_init(game_id)
        cur_labels = list(item["labels"])
        cur_marks  = list(item["marks"])

        # いまの「お題→丸」の対応を作る
        mark_by_label = {lbl: mk for lbl, mk in zip(cur_labels, cur_marks)}

        # デフォルト順に並べ替え。該当が無ければ0
        labels = DEFAULT_LABELS
        marks  = [mark_by_label.get(lbl, 0) for lbl in labels]

        ts = int(time.time())
        table.update_item(
            Key={"gameId": game_id},
            UpdateExpression="SET labels=:l, marks=:m, updatedAt=:t",
            ExpressionAttributeValues={":l": labels, ":m": marks, ":t": ts},
        )
        return _resp(200, {"labels": labels, "marks": marks, "updatedAt": ts})