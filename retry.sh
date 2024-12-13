#!/bin/bash

# Pythonスクリプトのパスを指定
PYTHON_SCRIPT="./markers_udp.py"

# 無限ループで再試行
while true; do
    echo "Starting Python script: $PYTHON_SCRIPT"
    
    # Pythonスクリプトを実行
    python3 $PYTHON_SCRIPT
    
    # 実行結果を取得
    RESULT=$?
    
    # 正常終了ならスクリプトを終了
    if [ $RESULT -eq 0 ]; then
        echo "Python script finished successfully."
        break
    else
        echo "Python script failed with exit code $RESULT. Restarting..."
    fi
    
    # 再試行間隔を設定（必要に応じて調整、例: 5秒待機）
    sleep 1
done

