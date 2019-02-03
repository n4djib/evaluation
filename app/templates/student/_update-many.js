var data_arr = {{ data | safe | replace('None', 'null') }};
var colHeaders = ['id', 'Matricule', 'Nom', 'Prénom', 'Date de naissance', 'Lieu de Naissance', '        Wilaya        '];
var wilayas_name_list = {{ wilayas_name_list | safe }};
var username_list = {{ username_list | safe }};
var branch_list = {{ branch_list | safe }};


var separator = '-';

var hotElement = document.querySelector('#hot-update-many');


/*
  get all usernames
  get usernames in this Promo
  do not color the usernames of this Promo
    unless there is A duplication
*/
// function usernameRenderer(instance, td, row, col, prop, value, cellProperties) {
// 	Handsontable.renderers.TextRenderer.apply(this, arguments);

// 	var username = td.innerHTML.toLowerCase();
// 	var list = username_list.map(v => v.toLowerCase());

// 	if( /*username=='' ||*/ list.includes(username) )
//     	td.style.backgroundColor = '#ff4c42';

//     // username.match(/^([0-9]-{5,})$/)

//   return td;
// }

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


var clipboardCache = '';
var sheetclip = new SheetClip();

var hot = new Handsontable(hotElement, {
  data: data_arr,
  columns: [
    {data: 0, type: 'text', readOnly: true, renderer: closedRenderer, width: 0.1},
    {data: 1, type: 'text', /*renderer: usernameRenderer*/},
    {data: 2, type: 'text', readOnly: true, renderer: closedRenderer},
    {data: 3, type: 'text', readOnly: true, renderer: closedRenderer},
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
    //direction: 'vertical',
    direction: false,
  },
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
  // contextMenu: [
  //   'copy', 
  //   'cut', 
  //   '---------', 
  //   {
  //     key: 'paste',
  //     name: 'Paste',
  //     disabled: function() {
  //       return clipboardCache.length === 0;
  //     },
  //     callback: function() {
  //       var plugin = this.getPlugin('copyPaste');

  //       this.listen();
  //       plugin.paste(clipboardCache);
  //     }
  //   },
  //   'if <i>Paste</i> is not working use <b>CRTL+V</b> to <i>Paste</i>',
  //   // '<strike> paste </strike> (this is not working)</br>use <b>CRTL+V</b> to <i>paste</i>'
  // ],
});

/*****************/

// var save = document.getElementById("save");

$("#save").click(function(){
  Save();
});

// function add_branch(data_arr){
//   var branch_id = $("#select-branch").val();
//   for(var i=0; i<data_arr.length; i++) {
//     index = data_arr[i].length;
//     // data_arr[i][index-1] = branch_id;
//     data_arr[i].push(branch_id);
//   }
//   return data_arr;
// }

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
      window.location = '{{ url_for("students_update_many", session_id=session_id) }}';
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


