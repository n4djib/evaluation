
var header = {{ header | safe | replace('None', 'null') }};

var header_merge = {{ header_merge | safe | replace("'", "") }};



// var header_merge = [

// {row: 0, col: 0, rowspan: 1, colspan: 3}, 
// {row: 1, col: 0, rowspan: 1, colspan: 3}, 
// {row: 2, col: 0, rowspan: 1, colspan: 3}, 
// {row: 3, col: 0, rowspan: 1, colspan: 3},
 
// {row: 0, col: 3, rowspan: 1, colspan: 12}, 

// {row: 1, col: 3, rowspan: 1, colspan: 2}, 
// {row: 2, col: 3, rowspan: 1, colspan: 2}, 
// {row: 3, col: 3, rowspan: 1, colspan: 2}, 

// {row: 1, col: 5, rowspan: 1, colspan: 2}, 
// {row: 2, col: 5, rowspan: 1, colspan: 2}, 
// {row: 3, col: 5, rowspan: 1, colspan: 2}, 

// {row: 1, col: 7, rowspan: 1, colspan: 2}, 
// {row: 2, col: 7, rowspan: 1, colspan: 2}, 
// {row: 3, col: 7, rowspan: 1, colspan: 2}, 

// {row: 1, col: 9, rowspan: 1, colspan: 2}, 
// {row: 2, col: 9, rowspan: 1, colspan: 2}, 
// {row: 3, col: 9, rowspan: 1, colspan: 2}, 

// {row: 1, col: 11, rowspan: 1, colspan: 2}, 
// {row: 2, col: 11, rowspan: 1, colspan: 2}, 
// {row: 3, col: 11, rowspan: 1, colspan: 2}, 

// {row: 1, col: 13, rowspan: 1, colspan: 2}, 
// {row: 2, col: 13, rowspan: 1, colspan: 2}, 
// {row: 3, col: 13, rowspan: 1, colspan: 2}, 

// {row: 1, col: 15, rowspan: 1, colspan: 2}, 
// {row: 2, col: 15, rowspan: 1, colspan: 2}, 
// {row: 3, col: 15, rowspan: 1, colspan: 2}, 

// {row: 1, col: 17, rowspan: 1, colspan: 2}, 
// {row: 2, col: 17, rowspan: 1, colspan: 2}, 
// {row: 3, col: 17, rowspan: 1, colspan: 2}, 

// {row: 1, col: 19, rowspan: 1, colspan: 2}, 
// {row: 2, col: 19, rowspan: 1, colspan: 2}, 
// {row: 3, col: 19, rowspan: 1, colspan: 2}, 

// {row: 1, col: 21, rowspan: 1, colspan: 2}, 
// {row: 2, col: 21, rowspan: 1, colspan: 2}, 
// {row: 3, col: 21, rowspan: 1, colspan: 2}, 

// {row: 1, col: 23, rowspan: 1, colspan: 2}, 
// {row: 2, col: 23, rowspan: 1, colspan: 2}, 
// {row: 3, col: 23, rowspan: 1, colspan: 2}, 

// {row: 1, col: 25, rowspan: 1, colspan: 2}, 
// {row: 2, col: 25, rowspan: 1, colspan: 2}, 
// {row: 3, col: 25, rowspan: 1, colspan: 2}, 

// {row: 1, col: 27, rowspan: 1, colspan: 2}, 
// {row: 2, col: 27, rowspan: 1, colspan: 2}, 
// {row: 3, col: 27, rowspan: 1, colspan: 2},

// {row: 1, col: 29, rowspan: 1, colspan: 2}, 
// {row: 2, col: 29, rowspan: 1, colspan: 2}, 
// {row: 3, col: 29, rowspan: 1, colspan: 2}, 

// {row: 1, col: 31, rowspan: 1, colspan: 2}, 
// {row: 2, col: 31, rowspan: 1, colspan: 2}, 
// {row: 3, col: 31, rowspan: 1, colspan: 2},

// ];



var data_arr = {{ data | safe | replace('None', 'null') }};




var dataHeader = [];

dataHeader = dataHeader.concat(header)

var d = [];

var data = dataHeader.concat(d);
data = data.concat(data_arr);


var hotElement = document.getElementById('hot_semester');
var hot = new Handsontable(hotElement, {
	data: data,
	rowHeaders: false,
	colHeaders: false,
  mergeCells: header_merge,
});



hot.updateSettings({ cells: function(row, col, prop){
    var cell = hot.getCell(row, col);
    if(cell === undefined || cell === null)
      return cell;

    var cellProperties = {}
    // if( (row >= 0 && row < 5 ) && (col >= 0 && col <= 5) ) {
    //   cellProperties.readOnly = true;
    // }
    cellProperties.testttt = true;

    if(row === 4 && (col >= 3 && col <= 10) ) {
      // cellProperties.readOnly = true;
    }
    // td.innerHTML = '<b>' + td.innerHTML + '</b>';

    return cellProperties;
  }

});


var elements = document.getElementsByClassName("wtHider");
var width_str = elements[0].style.width;
var width = parseInt(width_str.replace("px", "")) + 100;
document.getElementById("container").style.width = width+"px";
console.log(width_str + ' - ' + width);
