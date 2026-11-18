import json
import sys, os
import random
from openpyxl import Workbook

with open(sys.argv[1], "r") as f:
    cfg = json.load(f)

root_dir=sys.argv[1].split(".")[0]
log_dir=os.path.join(root_dir, "log")
result_dir=os.path.join(root_dir, "result")
os.makedirs(log_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

read_max_count = cfg["read"]["count"]
write_max_count  = cfg["write"]["count"]
# Top level
dut_types = cfg["DUT_type"]
env_temps = cfg["env_temp"]
groups = cfg["group"]

wb_r = Workbook()
wb_w = Workbook()

ws_r = wb_r.active
ws_w = wb_w.active

# header
row_count=0
for dut in cfg["DUT_type"]:
    for group in cfg["group"]:
        for temp in cfg["env_temp"]:
            ws_r.cell(row=2+row_count, column=1, value="{}{}_{}".format(dut,group,temp))
            ws_w.cell(row=2+row_count, column=1, value="{}{}_{}".format(dut,group,temp))
            row_count = row_count + 1

# Read section
ws_r.cell(row=1, column=1, value="ID (read)")
read_count=2
for term in  cfg["read"]["term"]:
    for ds in cfg["read"]["ds"]:
        ws_r.cell(row=1, column=read_count, value="term{}-ds{}".format(term,ds))
        for i in range(row_count):
            read_pos_min = cfg["read"]["boundary"]["pos_range"]["min"]
            read_pos_max = cfg["read"]["boundary"]["pos_range"]["max"]
            read_neg_min = cfg["read"]["boundary"]["neg_range"]["min"]
            read_neg_max = cfg["read"]["boundary"]["neg_range"]["max"]
            pos_val=random.randint(read_pos_min  , read_pos_max)  
            neg_val=random.randint(read_neg_min  , read_neg_max)  
            val_str=''
            logpath= os.path.join (log_dir, "{}-read-term{}-ds{}.log".format(ws_r.cell(row=2+i, column=1).value,term,ds))
            if os.path.exists(logpath):
                os.remove(logpath)
            with open(logpath, "w"):
                pass
                
            for j in range(read_max_count):
                read_pos_offset = cfg["read"]["bias"]["pos_offset"]
                read_neg_offset = cfg["read"]["bias"]["neg_offset"]
                bias_pos=random.randint(0,read_pos_offset)
                bias_neg=random.randint(0,read_neg_offset)
                
                if neg_val+bias_neg > read_neg_max:
                    result_neg = read_neg_max
                else:
                    result_neg = neg_val+bias_neg
                if pos_val+bias_pos > read_pos_max:
                    result_pos = read_pos_max
                else:
                    result_pos = pos_val+bias_pos
                with open(logpath, "a") as file:
                    file.write("Testing rdq negative offset: ")
                    for k in range(result_neg):
                        file.write("-{} ".format(k+1))
                    file.write("\n\n")
                    file.write("Testing rdq positive offset: ")
                    for k in range(result_pos):
                        file.write("{} ".format(k+1))
                    file.write("\n")
                val_str += "[-{},{}] ".format(result_neg,result_pos)
            ws_r.cell(row=2+i, column=read_count, value=val_str)
        read_count=read_count+1
    
write_count=2    
ws_w.cell(row=1, column=1, value="ID (write)")  
for pdds in  cfg["write"]["pdds"]:
    for dds in cfg["write"]["dds"]:
        for odt in cfg["write"]["odt"]:
            ws_w.cell(row=1, column=write_count, value="pdds{}-dds{}-odt{}".format(pdds,dds,odt))
            for i in range(row_count):
                write_pos_min = cfg["write"]["boundary"]["pos_range"]["min"]
                write_pos_max = cfg["write"]["boundary"]["pos_range"]["max"]
                write_neg_min = cfg["write"]["boundary"]["neg_range"]["min"]
                write_neg_max = cfg["write"]["boundary"]["neg_range"]["max"]
                pos_val=random.randint(write_pos_min  , write_pos_max)  
                neg_val=random.randint(write_neg_min  , write_neg_max)  
                val_str=''
                
                logpath= os.path.join (log_dir, "{}-write-pdds{}-dds{}-odt{}.log".format(ws_r.cell(row=2+i, column=1).value,pdds,dds,odt))
                if os.path.exists(logpath):
                    os.remove(logpath)
                with open(logpath, "w"):
                    pass
                    
                for j in range(write_max_count):
                    write_pos_offset = cfg["write"]["bias"]["pos_offset"]
                    write_neg_offset = cfg["write"]["bias"]["neg_offset"]
                    bias_pos=random.randint(0,write_pos_offset)
                    bias_neg=random.randint(0,write_neg_offset)
                    if neg_val+bias_neg > write_neg_max:
                        result_neg = write_neg_max
                    else:
                        result_neg = neg_val+bias_neg
                    if pos_val+bias_pos > write_pos_max:
                        result_pos = write_pos_max
                    else:
                        result_pos = pos_val+bias_pos
                    with open(logpath, "a") as file:
                        file.write("Testing wdq negative offset: ")
                        for k in range(result_neg):
                            file.write("-{} ".format(k+1))
                        file.write("\n")
                        file.write("Testing wdq positive offset: ")
                        for k in range(result_pos):
                            file.write("{} ".format(k+1))
                        file.write("\n")    
                        file.write("wdq offset boundary is [-{},{}]".format(result_neg-1 , result_pos -1 ))
                        file.write("\n\n")  

                    val_str += "[-{},{}] ".format(result_neg, result_pos)
                ws_w.cell(row=2+i, column=write_count, value=val_str)
            write_count=write_count+1
wb_r.save(os.path.join(result_dir,"read_result.xlsx"))
wb_w.save(os.path.join(result_dir,"write_result.xlsx"))
