import turtle
import math
import winsound
import threading
from PIL import Image  # 用於轉存 JPEG

NOTES = [
    (392, 300), (392, 300), (440, 600), (392, 600), (523, 600), (494, 1200),
    (392, 300), (392, 300), (440, 600), (392, 600), (587, 600), (523, 1200),
    (392, 300), (392, 300), (784, 600), (659, 600), (523, 600), (494, 600), (440, 600),
    (698, 300), (698, 300), (659, 600), (523, 600), (587, 600), (523, 1800)
]

def play_birthday_song():
    for freq, duration in NOTES:
        winsound.Beep(freq, duration)

def save_turtle_as_jpeg(screen, filename="taiwan_flag.jpg"):
    """將 turtle 畫布轉存為 JPEG 圖片"""
    canvas = screen.getcanvas()
    eps_file = "temp_flag.eps"
    
    # 1. 先將 canvas 輸出成 PostScript 檔案
    canvas.postscript(file=eps_file)
    
    try:
        # 2. 使用 Pillow 打開 eps 並轉存為 jpg
        img = Image.open(eps_file)
        img.load()  # 載入影像資料
        img.save(filename, "JPEG", quality=95)
        print(f"成功儲存圖片至：{filename}")
    except Exception as e:
        print(f"轉存失敗（可能需要安裝 Ghostscript）：{e}")

def draw_flag_and_party():
    screen = turtle.Screen()
    screen.title("中華民國國旗與生日快樂音樂動畫")
    screen.setup(width=650, height=550)
    screen.bgcolor("white")
    
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    
    flag_width = 450
    flag_height = 300
    start_x = -flag_width / 2
    start_y = -flag_height / 2 + 30
    
    # 1. 紅色底色
    t.penup()
    t.goto(start_x, start_y)
    t.pendown()
    t.color("#DE0000", "#DE0000")
    t.begin_fill()
    for _ in range(2):
        t.forward(flag_width)
        t.left(90)
        t.forward(flag_height)
        t.left(90)
    t.end_fill()
    
    # 2. 青色長方形
    canton_width = flag_width / 2
    canton_height = flag_height / 2
    canton_start_y = start_y + flag_height / 2
    
    t.penup()
    t.goto(start_x, canton_start_y)
    t.pendown()
    t.color("#0000AA", "#0000AA")
    t.begin_fill()
    for _ in range(2):
        t.forward(canton_width)
        t.left(90)
        t.forward(canton_height)
        t.left(90)
    t.end_fill()
    
    # 3. 白日與光芒幾何
    cx = start_x + canton_width / 2
    cy = canton_start_y + canton_height / 2
    R = canton_width / 8
    ring_width = (2 * R) / 15
    ring_outer_radius = R + ring_width
    tip_distance = 2 * R
    
    # 4. 青圈
    t.penup()
    t.goto(cx, cy - ring_outer_radius)
    t.setheading(0)
    t.pendown()
    t.color("#0000AA", "#0000AA")
    t.begin_fill()
    t.circle(ring_outer_radius)
    t.end_fill()
    
    # 5. 12 道白光芒
    t.color("#FFFFFF", "#FFFFFF")
    for i in range(12):
        angle_center = 90 - i * 30
        angle_left = angle_center + 15
        angle_right = angle_center - 15
        
        tip_x = cx + tip_distance * math.cos(math.radians(angle_center))
        tip_y = cy + tip_distance * math.sin(math.radians(angle_center))
        
        b_left_x = cx + ring_outer_radius * math.cos(math.radians(angle_left))
        b_left_y = cy + ring_outer_radius * math.sin(math.radians(angle_left))
        
        b_right_x = cx + ring_outer_radius * math.cos(math.radians(angle_right))
        b_right_y = cy + ring_outer_radius * math.sin(math.radians(angle_right))
        
        t.penup()
        t.goto(tip_x, tip_y)
        t.pendown()
        t.begin_fill()
        t.goto(b_left_x, b_left_y)
        t.goto(b_right_x, b_right_y)
        t.goto(tip_x, tip_y)
        t.end_fill()
        
    # 6. 白日體
    t.penup()
    t.goto(cx, cy - R)
    t.setheading(0)
    t.pendown()
    t.color("#FFFFFF", "#FFFFFF")
    t.begin_fill()
    t.circle(R)
    t.end_fill()
    
    # 7. 啟動音樂
    song_thread = threading.Thread(target=play_birthday_song)
    song_thread.start()
    
    # 8. 閃爍文字動畫
    writer = turtle.Turtle()
    writer.hideturtle()
    writer.penup()
    writer.goto(0, start_y - 55)
    
    colors = ["#FF0000", "#FF7F00", "#FFD700", "#008000", "#0000FF", "#4B0082", "#9400D3", "#DE0000"]
    for _ in range(20):
        for col in colors:
            writer.clear()
            writer.color(col)
            writer.write("🎉 Happy Birthday! 🎉", align="center", font=("Arial", 22, "bold"))
            screen.update()
            turtle.time.sleep(0.12)
            
    song_thread.join()
    
    # 9. 動畫結束後自動存成 JPEG 圖片
    # save_turtle_as_jpeg(screen, "taiwan_flag_birthday.jpg")
    
    turtle.done()

if __name__ == '__main__':
    draw_flag_and_party()