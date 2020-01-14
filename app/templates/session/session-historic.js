var container = document.getElementById('session-historic');

var data_arr = {{ data_arr | safe | replace('None', 'null') }};

var maxRows = data_arr.length;
// var session_is_closed = {{ session.is_closed | safe | replace('T', 't') | replace('F', 'f') }};
var hot;

var save = document.getElementById("save");
// var autosave = document.getElementById("autosave");
var message = document.getElementById("message");
// var autosaveNotification;



var columns = [
  { data: 'id', type: 'text', width: 0.1, readOnly: true },
  { data: 'name', type: 'text', readOnly: true },
  { data: 'average', type: 'numeric', validator: averageValidator, {{ 'readOnly: true' if session.is_closed }} },
  { data: 'credit', type: 'numeric', validator: creditValidator, {{ 'readOnly: true' if session.is_closed }}},
];

container.innerHTML = ""; 

hot = new Handsontable(container, {
  data: data_arr,
  rowHeaders: true,
  manualColumnResize: true,
  colHeaders: ['--ID--', 'Name', 'Average', 'Credit'],
  stretchH: "all",
  contextMenu: true,
  columns: columns,
  fillHandle: {
    autoInsertRow: false,
    //direction: 'vertical',s
    direction: false,
  },
  maxRows: maxRows,
});




function Save(){
  $.ajax({
    // url: '/grade/save/', 
    url: '{{ url_for("session_historic_save") }}', 
    type: 'POST',
    data: JSON.stringify( nullifyData(data_arr) ),
    // data: JSON.stringify(data_arr),
    contentType: 'application/json; charset=utf-8',
    dataType: 'text',
    async: true,
    success: function(msg) {
      shake_message();
      
      is_dirty = false;
      console.log('---' + msg + '---');
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("some error");
    }
  });
}

$("#save").click(function(){
  // clearTimeout(autosaveNotification);
  Save();
  message.innerHTML
     = '<b style="color: green;"><div class="shake-slow shake-constant"><font size="2">Data saved</font></div></b>';

  // if (!autosave.checked)
  //   autosaveNotification = setTimeout(function() {
  //     shake_message();
  //   }, 1000);
});

$(document).on('keydown', function(e){
    if(e.ctrlKey && e.which === 83){ 
      // Check for the Ctrl key being pressed, and if the key = [S] (83)
      console.log('Ctrl+S!');
      // $("#save").click();
      save.click();
      e.preventDefault();
      return false;
    }
});

function shake_message(){
  var shake = '';
  var color = '';
  
  var msg = '<b style="'+color+'"><div class="'+shake+'"> <font size="2">  </font></div></b>';

  message.innerHTML = msg;
}

function nullifyData(data_arr) {
  var row, r_len;

  for (row = 0, r_len = data_arr.length; row < r_len; row++) {
    if(data_arr[row]["average"] === '' || isNaN(data_arr[row]["average"]) )
      data_arr[row]["average"] = null;

    if( data_arr[row]["credit"] === '' || isNaN(data_arr[row]["credit"]) )
      data_arr[row]["credit"] = null;

  }

  //maybe you can comment the next line
  //hot.loadData(data_arr);
  hot.validateCells(function() { hot.render(); });
  return data_arr;
}





$("#search").keyup(function(){
  filter(('' + this.value).toLowerCase());
});

function filter(search) {
  var row, r_len;
  var data = data_arr;
  var array = [];
  for (row = 0, r_len = data.length; row < r_len; row++) {
    d = data[row];


    for(var key in d) {
      if(key !== "id") {
    	var value = d[key];
    	if( ('' + value).toLowerCase().indexOf(search) > -1) {
    		array.push(d);
    		break;
    	}
      }
    }



  }
  hot.loadData(array);
  hot.validateCells(function() { hot.render(); });
}



/******** validation **********/

function averageValidator(value, callback) {
  if ( value < 0 || value > 20 || isNaN(value) )
    callback(false);
  else
    callback(true);
}

function  creditValidator(value, callback) {
  if ( value < 0 || value > 30 || isNaN(value) )
    callback(false);
  else
    callback(true);
}

hot.validateCells(function() {
  hot.render();
});

/*******************************/
