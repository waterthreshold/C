import matplotlib.pyplot as plt
import re, sys, os
from pathlib import Path





# Sample data
time = []
temp =[]
path = Path(sys.argv[1])
for entry in path.iterdir():
    idx=0 
    time.clear()
    temp.clear()
    full_path = entry.resolve()
    with open(os.path.join(full_path,"g.log"), "r") as f:
        for line in f:
            match = re.search(r"\] (\d+)", line)
            if match:
                number = match.group(1)
                num = int (number) / 1000
                #print(num)
                time.append(idx)
                temp.append(num)
                idx+=1

    # Create line chart
    plt.plot(time, temp)

    # Add labels and title
    plt.xlabel("X")
    plt.ylabel("Temperature")
    plt.title("{} Chart".format(entry.name))
    plt.savefig("{}.png".format(entry.name)) 
    plt.close()
    # Show the chart
    # plt.show()
