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
    
    file_name = 'data_feed.txt' 

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
        region_name='ap-northeast-1' # 日本（東京）リージョンを指定
    )
    
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=tsv_content,
        ContentType='text/plain'
    )
    print("S3へのアップロードが完了しました！")

if __name__ == "__main__":
    main()
