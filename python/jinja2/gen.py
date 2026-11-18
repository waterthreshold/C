from jinja2 import Environment, FileSystemLoader
from datetime import datetime

env = Environment(loader=FileSystemLoader('.'))
# cover_template = env.get_template('cover.html')s
cover_template = env.get_template('cover.html')
report_template = env.get_template('report.html')
data = {
    "title": "Test Report",
    "subtitle": "HW Stress Test Report",
    "author": "Jeff Chiang",
    "version": "v1.0",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "summary": "Folloing HW stress test guideline V1.0 GROUP A testing. <br><b>Bandwidth test<\b> + <b>Memtest</b> + <b>Vector process</b> + <b> JPEG encoding</b> + <b>Bit stream (bit diff stream)</b>+ <b> SD card R/W(@Max encoding performance) </b>",
    "info": [
        {"project":},
        {"odm":},
        {"fw_version": }
        {"SoC"}
        {"SDK Version"}
    ],
    "items": [
        {"name": "Temperature", "value": "36.5 C"},
        {"name": "Pressure", "value": "1 atm"},
        {"name": "Humidity", "value": "60%"},
    ],
    "image_path": "output.png",
    "logo_path" : "logo.png",
    "conclusion": "All tests passed successfully."
}

# output = template.render(data)
with open("cover_out.html", "w") as f:
    f.write(cover_template.render(data))
    
with open("report_out.html", "w") as f:
    f.write(report_template.render(data))

print("Report generated: report_output.html")