function main(workbook: ExcelScript.Workbook) {
  let selectedSheet = workbook.getActiveWorksheet();

  let usedRange = selectedSheet.getUsedRange();
  // fill in your working project row, the start index is 0
  const my_project_row = [ 889, 915  ]
  // change your name. please input your name here
  const myname = '' 

  // Loop through the rows of the range values
  // find your column
  for (let i = usedRange.getColumnCount(); i >= 0 ; i--) {
	let rangeValues = usedRange.getCell(2,i);
	if (rangeValues.getValue() == myname ){
		my_column=i
		total_work_time=usedRange.getCell(3,i).getValue();
		name=rangeValues.getValue()
		break;
	}
  }
	console.log("Name:" + name + "\ndetect work time: "+ total_work_time )
	let remain_hour: number = parseFloat(total_work_time)
	for (let i : number = 0 ; i < my_project_row.length; i++) {
		if ( i == my_project_row.length - 1 )
			signated_hour = remain_hour;
		else{ 
			signated_hour =Math.floor ( Math.floor (total_work_time) / my_project_row.length)
			remain_hour -= signated_hour;
		}
		
		usedRange.getCell(my_project_row[i],my_column).setValue(signated_hour.toString())
	}
  // Write the results to the column immediately to the right of the used range
  // getOffsetRange(0, usedRange.getColumnCount()) moves the range reference
  // to the next available column
  //let resultsRange = usedRange.getOffsetRange(0, usedRange.getColumnCount());
  //resultsRange.setValues(results);
}
