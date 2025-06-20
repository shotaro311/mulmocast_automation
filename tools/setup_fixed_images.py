#!/usr/bin/env python3
"""
固定画像を事前生成して保存するセットアップスクリプト
一度実行すれば、以降は画像生成APIを呼ばずに済みます
"""

import json
import os
import subprocess
import sys

def setup_fixed_images():
    """固定画像を事前生成"""
    
    print("🖼️  Fixed Images Setup")
    print("=====================")
    print("固定画像を事前生成して、今後のtoken消費を削減します")
    
    # 固定画像用のスクリプト作成
    fixed_images_script = {
        "$mulmocast": {
            "version": "1.0"
        },
        "title": "固定画像生成用",
        "description": "オープニング・クロージング画像の事前生成",
        "lang": "ja",
        "speechParams": {
            "speakers": {
                "Presenter": {
                    "voiceId": "shimmer",
                    "displayName": {
                        "ja": "プレゼンター"
                    }
                }
            }
        },
        "imageParams": {
            "style": "professional financial news graphics"
        },
        "beats": [
            {
                "speaker": "Presenter",
                "text": "オープニング画像生成用",
                "imagePrompt": "professional news studio background with financial charts and graphs, morning news setting, clean and modern design",
                "duration": 1
            },
            {
                "speaker": "Presenter", 
                "text": "クロージング画像生成用",
                "imagePrompt": "YouTube channel subscribe button and like button with financial news channel branding, call-to-action graphics",
                "duration": 1
            }
        ]
    }
    
    # スクリプトファイル保存
    script_file = "fixed_images_setup.json"
    with open(script_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_images_script, f, ensure_ascii=False, indent=2)
    
    print(f"✅ セットアップ用スクリプト作成: {script_file}")
    
    # 画像のみ生成
    print("🎨 固定画像を生成中...")
    result = subprocess.run(['mulmo', 'images', script_file], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 固定画像生成完了！")
        
        # 生成された画像ファイルを確認
        output_dir = "output/images/fixed_images_setup"
        if os.path.exists(output_dir):
            image_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            print(f"📁 生成された画像: {len(image_files)}枚")
            for img in image_files:
                print(f"   - {img}")
            
            # 固定画像の設定を保存
            fixed_images_config = {
                "opening_image": os.path.join(output_dir, image_files[0]) if len(image_files) > 0 else None,
                "closing_image": os.path.join(output_dir, image_files[1]) if len(image_files) > 1 else None,
                "created_at": subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
            }
            
            with open("config/fixed_images_config.json", 'w', encoding='utf-8') as f:
                json.dump(fixed_images_config, f, ensure_ascii=False, indent=2)
            
            print("💾 固定画像設定を保存しました: config/fixed_images_config.json")
            print("🎉 セットアップ完了！今後は画像生成APIの消費が削減されます")
            
        else:
            print("❌ 画像出力ディレクトリが見つかりません")
            return False
            
    else:
        print(f"❌ 画像生成に失敗しました: {result.stderr}")
        return False
    
    # クリーンアップ
    os.remove(script_file)
    print("🧹 一時ファイルを削除しました")
    
    return True

def check_fixed_images():
    """固定画像の設定状況をチェック"""
    
    if not os.path.exists("config/fixed_images_config.json"):
        print("❌ 固定画像が設定されていません")
        print("setup_fixed_images.py を実行してセットアップしてください")
        return False
    
    with open("config/fixed_images_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("✅ 固定画像設定済み")
    print(f"📁 オープニング画像: {config.get('opening_image', 'なし')}")
    print(f"📁 クロージング画像: {config.get('closing_image', 'なし')}")
    print(f"📅 作成日時: {config.get('created_at', '不明')}")
    
    # ファイルの存在確認
    opening_exists = config.get('opening_image') and os.path.exists(config['opening_image'])
    closing_exists = config.get('closing_image') and os.path.exists(config['closing_image'])
    
    if opening_exists and closing_exists:
        print("✅ 全ての固定画像ファイルが存在します")
        return True
    else:
        print("❌ 一部の画像ファイルが見つかりません")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_fixed_images()
    else:
        setup_fixed_images() 