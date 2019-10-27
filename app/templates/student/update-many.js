var data_arr = {{ data | safe | replace('None', 'null') }};
var colHeaders = ['id', 'Matricule', 'Nom et Prénom', 'Prénom', 'Date de naissance', 'Lieu de Naissance', '        Wilaya        '];
var wilayas_name_list = {{ wilayas_name_list | safe }};
var username_list = {{ username_list | safe }};
var branch_list = {{ branch_list | safe }};

var promo_has_closed = {{ promo_has_closed | safe | replace('T', 't') | replace('F', 'f') }};

var maxRows = data_arr.length;

// var username_readOnly = true;

var separator = '-';

var hotElement = document.querySelector('#hot-update-many');


/*
  get all usernames
  get usernames in this Promo
  do not color the usernames of this Promo
    unless there is A duplication
*/

function usernameRenderer(instance, td, row, col, prop, value, cellProperties) {
	Handsontable.renderers.TextRenderer.apply(this, arguments);

  if (promo_has_closed)
    td.style.backgroundColor = '#EEE';

// 	var username = td.innerHTML.toLowerCase();
// 	var list = username_list.map(v => v.toLowerCase());

// 	if( /*username=='' ||*/ list.includes(username) )
//     	td.style.backgroundColor = '#ff4c42';

//     // username.match(/^([0-9]-{5,})$/)

  return td;
}


function wilayaRenderer(instance, td, row, col, prop, value, cellProperties) {
	Handsontable.renderers.TextRenderer.apply(this, arguments);

	var str = td.innerHTML.toLowerCase();
	str = str.charAt(0).toUpperCase() + str.slice(1);
	td.innerHTML = str;
  data_arr[row][col] = str;

  // map
  var list = wilayas_name_list.map(v => v.toLowerCase());
  if( !list.includes(str.toLowerCase()) )
    td.style.backgroundColor = '#ff4c42';

  // if(!wilayas_name_list.includes(str))
  //     td.style.backgroundColor = '#ff4c42';
  // if(str!='')
  //     td.style.backgroundColor = '#ff4c42';

  return td;
}

function closedRenderer(instance, td) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.backgroundColor = '#EEE';
  // td.innerHTML = '<b>' + td.innerHTML + '</b>';
  return td;
}

//safeHtmlRenderer
function lastNameRenderer(instance, td, row, col, prop, value, cellProperties) {
  // var escaped = Handsontable.helper.stringify(value);
  // escaped = strip_tags(escaped, '<em><b><strong><a><big>'); //be sure you only allow certain HTML tags to avoid XSS threats (you should also remove unwanted HTML attributes)
  // td.innerHTML = escaped;
  td.style.backgroundColor = '#EEE';

  // Handsontable.renderers.TextRenderer.apply(this, arguments);
  Handsontable.renderers.HtmlRenderer.apply(this, arguments);
  // Handsontable.renderers.TextRenderer.apply(this, arguments);
  // td.style.backgroundColor = '#EEE';
  return td;
}

function firstNameRenderer(instance, td) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.backgroundColor = '#E0E';
  td.innerHTML = '';
  return td;
}


var clipboardCache = '';
var sheetclip = new SheetClip();

var hot = new Handsontable(hotElement, {
  data: data_arr,
  columns: [
    {data: 0, type: 'text', readOnly: true, renderer: closedRenderer, width: 0.1},
    {data: 1, type: 'text', renderer: usernameRenderer, {{ 'readOnly: true' if promo_has_closed }} },
    {data: 2, type: 'text', readOnly: true, renderer: lastNameRenderer},
    {data: 3, type: 'text', readOnly: true, renderer: firstNameRenderer, width: 0.1},
    {data: 4, type: 'date', dateFormat: 'DD/MM/YYYY'},
    {data: 5, type: 'text'},
    {
      data: 6, 
      type: 'dropdown',
      source: wilayas_name_list,
      type: "autocomplete",

      // type: 'text',
      // editor: 'select',
      // selectOptions: wilayas_name_list, 
      
      // renderer: wilayaRenderer
    },

  ],

  colHeaders: colHeaders,
  // columnSorting: true,
  columnSorting: {column: 1, sortOrder: true},
  sortIndicator: true,
  stretchH: 'all',
  fillHandle: {
    autoInsertRow: false,
    //direction: 'vertical',s
    direction: false,
  },
  maxRows: maxRows,
  autoWrapRow: true,
  manualRowResize: true,
  manualColumnResize: true,
  rowHeaders: true,
  manualRowMove: true,
  manualColumnMove: true,
  afterCopy: function(changes) {
    clipboardCache = sheetclip.stringify(changes);
  },
  afterCut: function(changes) {
    clipboardCache = sheetclip.stringify(changes);
  },
  afterPaste: function(changes) {
    // we want to be sure that our cache is up to date, even if someone pastes data from another source than our tables.
    clipboardCache = sheetclip.stringify(changes);
  },

});



/*****************/

// var save = document.getElementById("save");

$("#save").click(function(){
  Save();
});


function Save(){
  $.ajax({
    url: '{{ url_for("update_many_student_save") }}', 
    type: 'POST',
    // data: JSON.stringify( add_branch(data_arr) ),
    data: JSON.stringify( data_arr ),
    contentType: 'application/json; charset=utf-8',
    dataType: 'text',
    async: true,
    success: function(msg) {
      // alert('---' +msg+ '---');
      console.log('Success: \n' + msg + ' \n------------');
      window.location = '{{ url_for("students_update_many", promo_id=promo_id) }}';
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("fix the errors before Updating...");
      console.log('Error --- ');
    }
  });
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
      var value = d[key];
      if( ('' + value).toLowerCase().indexOf(search) > -1) {
        array.push(d);
        break;
      }
    }
  }
  hot.loadData(array);
  hot.validateCells(function() { hot.render(); });
}


