from PIL import Image, ImageDraw

def create_network_icon():
    # 建立 256x256 高解析度透明畫布
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. 繪製現代圓角矩形背景 (Windows 藍 #007ACC)
    draw.rounded_rectangle([16, 16, 240, 240], radius=52, fill="#007ACC")
    
    # 2. 繪製內部網路拓樸圖標 (節點與連線)
    # 上方節點 (主路由)
    draw.rectangle([104, 55, 152, 95], fill="white")
    # 左右下方節點 (網卡/裝置)
    draw.rectangle([52, 160, 92, 200], fill="white")
    draw.rectangle([164, 160, 204, 200], fill="white")
    
    # 連接線
    draw.line([128, 95, 128, 125], fill="white", width=10)
    draw.line([72, 125, 184, 125], fill="white", width=10)
    draw.line([72, 125, 72, 160], fill="white", width=10)
    draw.line([184, 125, 184, 160], fill="white", width=10)
    
    # 3. 儲存為多解析度 Windows .ico 檔
    img.save("app_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("成功產生 app_icon.ico 圖示檔案！")

if __name__ == "__main__":
    create_network_icon()