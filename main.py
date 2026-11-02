import os
import json
import gspread
import boto3
import io
import csv

def main():
    # 1. 環境変数の取得
    gcp_sa_json = os.environ['GCP_SA_JSON']
    spreadsheet_id = os.environ['SPREADSHEET_ID']
    
    # 登録済みのFTP情報をAWS認証情報として流用
    aws_access_key = os.environ['FTP_USER']
    aws_secret_key = os.environ['FTP_PASS']
    host_string = os.environ['FTP_HOST']
    
    # S3バケット名をホスト名から自動抽出 (例: my-bucket.s3.amazonaws.com -> my-bucket)
    bucket_name = host_string.split('.s3.')[0] if '.s3.' in host_string else host_string
    
    file_name = 'app/cdn.3ple.jp/webroot/3ple/merchantcenter/Google PLA広告配信商品エントリーシート.txt' 

    # 2. Google Sheetsからデータ取得
    print("Google Sheetsからデータを取得中...")
    credentials = json.loads(gcp_sa_json)
    gc = gspread.service_account_from_dict(credentials)
    worksheet = gc.open_by_key(spreadsheet_id).sheet1
    data = worksheet.get_all_values()

    # 3. タブ区切りテキスト（TSV）の生成
    print("タブ区切りテキストに変換中...")
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', lineterminator='\n')
    writer.writerows(data)
    tsv_content = output.getvalue()

# 4. Amazon S3 API (ポート443) へアップロード
    print(f"Amazon S3 (バケット: {bucket_name}) へ接続中...")
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name='ap-northeast-1' # 日本リージョン
    )
    
    try:
        # サーバーからの応答（レスポンス）を受け取る
        response = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=tsv_content,
            ContentType='text/plain'
        )
        
        # --- ログ出力エリア ---
        print("="*50)
        print("✅ アップロード処理が完了しました")
        print(f"▶ アップロード先バケット : {bucket_name}")
        print(f"▶ 保存されたファイルパス : {file_name}")
        print(f"▶ サーバーからの応答番号 : {response.get('ResponseMetadata', {}).get('HTTPStatusCode')} (200なら正常)")
        print(f"▶ 推定されるファイルURL  :")
        print(f"  https://{bucket_name}.s3.ap-northeast-1.amazonaws.com/{file_name}")
        print("="*50)
        
    except Exception as e:
        # 万が一エラーが隠れていた場合は強制的に表示させてJobを失敗させる
        print("="*50)
        print("❌ アップロード中にエラーが発生しました")
        print(f"エラー詳細: {e}")
        print("="*50)
        raise e
        
if __name__ == "__main__":
    main()
