import os
import json
import gspread
import paramiko
import io
import csv

def main():
    # 1. 環境変数の取得
    gcp_sa_json = os.environ['GCP_SA_JSON']
    spreadsheet_id = os.environ['SPREADSHEET_ID']
    
    sftp_host = os.environ['FTP_HOST']
    sftp_port = int(os.environ.get('FTP_PORT', 22)) # SFTPは通常22番ポートです
    sftp_user = os.environ['FTP_USER']
    sftp_pass = os.environ['FTP_PASS']
    
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

    # 4. SFTPサーバーへアップロード
    print(f"SFTPサーバー ({sftp_host}:{sftp_port}) へ接続中...")
    
    # SSHクライアントの設定
    transport = paramiko.Transport((sftp_host, sftp_port))
    try:
        transport.connect(username=sftp_user, password=sftp_pass)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # メモリ上のデータをファイルとしてアップロード
        with io.BytesIO(tsv_content) as bio:
            sftp.putfo(bio, file_name)
        
        print("SFTPサーバーへのアップロードが完了しました！")
        
    finally:
        if 'sftp' in locals():
            sftp.close()
        transport.close()

if __name__ == "__main__":
    main()
