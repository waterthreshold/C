import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import winsound
import threading
import time

# 生日快樂歌音符頻率與拍子 (ms)
NOTES = [
    (392, 300), (392, 300), (440, 600), (392, 600), (523, 600), (494, 1200),
    (392, 300), (392, 300), (440, 600), (392, 600), (587, 600), (523, 1200),
    (392, 300), (392, 300), (784, 600), (659, 600), (523, 600), (494, 600), (440, 600),
    (698, 300), (698, 300), (659, 600), (523, 600), (587, 600), (523, 1800)
]

def play_birthday_song():
    """播放生日快樂歌"""
    for freq, duration in NOTES:
        winsound.Beep(freq, duration)

def draw_and_save_flag_with_music():
    # 建立圖形視窗 (3:2 比例)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(0, 300)
    ax.set_ylim(-30, 200)  # 多留下方空間給祝賀文字
    ax.set_aspect('equal')
    ax.axis('off')

    # 1. 紅色底色 (#DE0000)
    red_rect = patches.Rectangle((0, 0), 300, 200, facecolor='#DE0000', edgecolor='none')
    ax.add_patch(red_rect)

    # 2. 青色長方形 (#0000AA) - 左上角 1/4 面積
    blue_rect = patches.Rectangle((0, 100), 150, 100, facecolor='#0000AA', edgecolor='none')
    ax.add_patch(blue_rect)

    # 3. 白日與光芒幾何計算
    cx, cy = 75, 150
    R = 18.75  # 150 / 8
    ring_width = (2 * R) / 15
    ring_outer_radius = R + ring_width
    tip_distance = 2 * R

    # 4. 青圈
    blue_ring = patches.Circle((cx, cy), ring_outer_radius, facecolor='#0000AA', edgecolor='none')
    ax.add_patch(blue_ring)

    # 5. 12 道白尖角光芒
    for i in range(12):
        angle_center = np.pi / 2 - i * (2 * np.pi / 12)
        angle_left = angle_center + np.pi / 12
        angle_right = angle_center - np.pi / 12

        tip_x = cx + tip_distance * np.cos(angle_center)
        tip_y = cy + tip_distance * np.sin(angle_center)
        base_left_x = cx + ring_outer_radius * np.cos(angle_left)
        base_left_y = cy + ring_outer_radius * np.sin(angle_left)
        base_right_x = cx + ring_outer_radius * np.cos(angle_right)
        base_right_y = cy + ring_outer_radius * np.sin(angle_right)

        ray = patches.Polygon([[tip_x, tip_y], [base_left_x, base_left_y], [base_right_x, base_right_y]], facecolor='#FFFFFF', edgecolor='none')
        ax.add_patch(ray)

    # 6. 白日體
    sun_body = patches.Circle((cx, cy), R, facecolor='#FFFFFF', edgecolor='none')
    ax.add_patch(sun_body)

    # 7. 啟動背景音樂
    song_thread = threading.Thread(target=play_birthday_song)
    song_thread.start()

    # 8. 動態閃爍文字效果與視窗更新
    colors = ["#FF0000", "#FF7F00", "#FFD700", "#008000", "#0000FF", "#4B0082", "#9400D3", "#DE0000"]
    plt.ion()  # 開啟互動模式
    plt.show(block=False)

    text_artist = None
    for _ in range(18):
        for col in colors:
            if text_artist:
                text_artist.remove()
            text_artist = ax.text(150, -15, "🎉 Happy Birthday! 🎉", color=col, fontsize=20, fontweight='bold', ha='center', va='center')
            plt.draw()
            plt.pause(0.12)

    song_thread.join()

    # 9. 動畫與音樂結束後，自動儲存為 JPEG 圖片！
    output_filename = "taiwan_flag_birthday.jpg"
    fig.savefig(output_filename, format='jpeg', dpi=300, bbox_inches='tight')
    print(f"成功儲存圖片至：{output_filename}")

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    draw_and_save_flag_with_music()