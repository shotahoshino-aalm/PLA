import os
import json
import gspread
import ftplib
import io
import csv

def main():
    # 1. 環境変数の取得
    gcp_sa_json = os.environ['GCP_SA_JSON']
    spreadsheet_id = os.environ['SPREADSHEET_ID']
    
    ftp_host = os.environ['FTP_HOST']
    ftp_port = int(os.environ.get('FTP_PORT', 21))
    ftp_user = os.environ['FTP_USER']
    ftp_pass = os.environ['FTP_PASS']
    
    # サーバーに保存するファイル名（必要に応じてディレクトリパスを追加: 'public_html/data_feed.txt'など）
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
    tsv_content = output.getvalue().encode('utf-8')

    # 4. FTPサーバーへアップロード
    print(f"FTPサーバー ({ftp_host}) へ接続中...")
    with ftplib.FTP() as ftp:
        ftp.connect(ftp_host, ftp_port)
        ftp.login(ftp_user, ftp_pass)
        
        # バイナリモードでアップロード
        with io.BytesIO(tsv_content) as bio:
            ftp.storbinary(f'STOR {file_name}', bio)
            
    print("FTPサーバーへのアップロードが完了しました！")

if __name__ == "__main__":
    main()
