var data_arr = {{ data | safe | replace('None', 'null') }};
var type = '{{ type | safe }}';

var session_is_rattrapage = {{ session.is_rattrapage | safe | replace('T', 't') | replace('F', 'f') }};
var session_is_closed = {{ session.is_closed | safe | replace('T', 't') | replace('F', 'f') }};
var maxRows = data_arr.length;


var hotElement = document.querySelector('#hot');


function get_fields_list(formula){
  var fields_list = [];
  for(key in formula)
    if(key !== 'credit' && key !== 'coefficient')
      fields_list.push(key);
  return fields_list;
}

function get_field_percentage(formula, field){
  var percentage = 0;
  for(key in formula)
    if(key == field)
      return formula[key] * 100 + '%';
  return '***';
}

function fill_cols() {
  var fields_list = [];
  for(var i=0; i<data_arr.length; i++)
    fields_list = fields_list.concat( get_fields_list(data_arr[i]['formula']) );

  var cour = td = tp = t_pers = stage = false;
  var formula = false;

  if(fields_list.includes('cour'))   
    cour = true;
  if(fields_list.includes('td'))
    td = true;
  if(fields_list.includes('tp'))
    tp = true;
  if(fields_list.includes('t_pers'))
    t_pers = true;
  if(fields_list.includes('stage'))
    stage = true;

  if('{{_all}}' == 'all'){
    cour = td = tp = t_pers = stage = true;
    formula = true;
  }

  var second_column_name = "Module Name";
  if (type == 'module')
    second_column_name = "Student Name";

  var cols = {
    'name':    {visible: true, name: second_column_name},
    'cour':    {visible: cour, name: "Cour"},
    'td':      {visible: td, name: "TD"},
    'tp':      {visible: tp, name: "TP"},
    't_pers':  {visible: t_pers, name: "T.Pers"},
    'stage':   {visible: stage, name: "Stage"},
    'average': {visible: true, name: "(Average)"},
    'credit':  {visible: true, name: "(Credit)"},
    'formula': {visible: formula, name: "(Formula)"},
  };

  if (type == 'module'){
    var _formula = data_arr[0]['formula'];
    var cour_label = 'Cour';
    // uncomment this Code to change the label Cour to Ratt.
    // if(session_is_rattrapage == true)
    //   cour_label = 'Ratt.'

    cols = {
      'username': {visible: true, name: "Username"},
      'name':     {visible: true, name: second_column_name},
      'cour':     {visible: cour, name: cour_label + " / " + get_field_percentage(_formula, 'cour') },
      'td':       {visible: td, name: "TD / " + get_field_percentage(_formula, 'td') },
      'tp':       {visible: tp, name: "TP / " + get_field_percentage(_formula, 'tp') },
      't_pers':   {visible: t_pers, name: "T.Pers / " + get_field_percentage(_formula, 't_pers') },
      'stage':    {visible: stage, name: "Stage / " + get_field_percentage(_formula, 'stage') },
      'average':  {visible: true, name: "(Average)"},
      'credit':   {visible: true, name: "(Credit)"},
      'formula':  {visible: formula, name: "(Formula)"},
    };
  }

  return cols;
}

var save = document.getElementById("save");
var autosave = document.getElementById("autosave");
var message = document.getElementById("message");
var autosaveNotification;

hotElement.innerHTML = '';

var cols = fill_cols();


var colHeaders = [];
var columns = [];

if(type == 'module') {
  colHeaders.push(cols['username']['name']);
  columns.push({ data: 'username', type: 'text', readOnly: true, renderer: nameRenderer });
}


colHeaders.push(cols['name']['name']),
columns.push({
  data: 'name', type: 'text', readOnly: true, renderer: nameRenderer
});

colHeaders.push(''),
columns.push({
  data: '__seperator1__', width: 1, readOnly: true, renderer: creditRenderer
});

//Create the Spreadsheet according to visibility
if (cols['cour']['visible'] === true)
  colHeaders.push(cols['cour']['name']),
  columns.push({
    data: 'cour', className: 'htRight', type: 'numeric', validator: rangeValidator,  
    // numericFormat: { pattern: '0.00', culture: 'en-US'},
    allowInvalid: true, allowEmpty: false, renderer: gradeRenderer
  });
if (cols['td']['visible'] === true)
  colHeaders.push(cols['td']['name']),
  columns.push({
    data: 'td', className: 'htRight', type: 'numeric', validator: rangeValidator,  
    // numericFormat: { pattern: '0,0.00', culture: 'en-US'},
    allowInvalid: true, allowEmpty: false, renderer: gradeRenderer
  });
if (cols['tp']['visible'] === true)
  colHeaders.push(cols['tp']['name']),
  columns.push({
    data: 'tp', className: 'htRight', type: 'numeric', validator: rangeValidator,  
    // numericFormat: { pattern: '0,0.00', culture: 'en-US'},
    allowInvalid: true, allowEmpty: false, renderer: gradeRenderer
  });
if (cols['t_pers']['visible'] === true)
  colHeaders.push(cols['t_pers']['name']),
  columns.push({
    data: 't_pers', className: 'htRight', type: 'numeric', validator: rangeValidator,  
    // numericFormat: { pattern: '0,0.00', culture: 'en-US'},
    allowInvalid: true, allowEmpty: false, renderer: gradeRenderer
  });
if (cols['stage']['visible'] === true)
  colHeaders.push(cols['stage']['name']),
  columns.push({
    data: 'stage', className: 'htRight', type: 'numeric', validator: rangeValidator,  
    // numericFormat: { pattern: '0,0.00', culture: 'en-US'},
    allowInvalid: true, allowEmpty: false, renderer: gradeRenderer
  });

colHeaders.push(''),
columns.push({
  data: '__seperator2__', width: 1, readOnly: true, renderer: creditRenderer
});

if (cols['average']['visible'] === true)
  colHeaders.push(cols['average']['name']),
  columns.push({
    data: 'average', className: 'htRight', /*readOnly: true,*/ 
    type: 'numeric', renderer: averageRenderer/* ,validator: rangeValidator*/
  });
if (cols['credit']['visible'] === true)
  colHeaders.push(cols['credit']['name']),
  columns.push({
    data: 'credit', className: 'htRight', /*readOnly: true,*/ 
    type: 'numeric', renderer: creditRenderer
  });
if (cols['formula']['visible'] === true)
  colHeaders.push(cols['formula']['name']),
  columns.push({
    data: 'formula', 
    type: 'text', 
    renderer: formulaRenderer
  });

/***************/
/***************/
/***************/

var is_dirty = false;
var msg_autosaved = 'Changes will not be autosaved';

if (autosave.checked)
  msg_autosaved = 'Changes will be autosaved';

Handsontable.dom.addEvent(autosave, 'click', function() {
  if (autosave.checked)
    msg_autosaved = 'Changes will be autosaved';
  else
    msg_autosaved = 'Changes will not be autosaved';

  shake_message();
});

function shake_message(){
  var shake = '';
  var color = '';
  
  var msg = '<b style="'+color+'"><div class="'+shake+'">';
  msg = msg + '<font size="2">' + msg_autosaved + '</font></div></b>';

  message.innerHTML = msg;
}

// Handsontable.dom.addEvent(save, 'click', function() {
//   if (autosave.checked){
//     msg_autosaved = 'Changes will be autosaved';
//     shake_message();
//   } else {
//     msg_autosaved = 'Changes will not be autosaved';
//     shake_message();
//   }
// });

//order by Student if type is module
var columnSorting = {};
if('module'=='{{type}}') {
  columnSorting = {column: 0, sortOrder: true};
}

var _first_after_change = 0;

var clipboardCache = '';
var sheetclip = new SheetClip();

var hot = new Handsontable(hotElement, {
  data: data_arr,
  rowHeaders: true,
  colHeaders: true,
  // columnSorting: true,
  sortIndicator: true,
  manualColumnResize: true,

  //autoWrapRow: true,
  //minSpareRows: true,
  // fillHandle: false,
  stretchH: "all",
  // readOnly: true,

  fillHandle: {
    autoInsertRow: false,
    direction: 'vertical',
    // direction: false,
  },
  maxRows: maxRows,

  colHeaders: colHeaders,
  columns: columns,
  columnSorting: columnSorting,
  // beforeChange: function (changes, source) {},
  afterChange: function (change, source) {
    if(_first_after_change != 0){
      is_dirty = true;
      // console.log('afterChange-------- '+_first_after_change);
    }
    shake_message();
    _first_after_change ++;

    autoSave(change, source);
    autoCalculate(change, source);
  },

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
  contextMenu: [
    'copy', 
    'cut', 
    '---------', 
    {
      key: 'paste',
      name: 'Paste',
      disabled: function() {
        return clipboardCache.length === 0;
      },
      callback: function() {
        var plugin = this.getPlugin('copyPaste');

        this.listen();
        plugin.paste(clipboardCache);
      }
    },
    'if <i>Paste</i> is not working use <b>CRTL+V</b> to <i>Paste</i>',
    // '<strike> paste </strike> (this is not working)</br>use <b>CRTL+V</b> to <i>paste</i>'
  ],
});








hot.validateCells(function() {
  hot.render();
});

hot.addHook('afterRender', function(){
  hot.validateCells();
})




/********************/
/********************/
/********************/

function GetColNameByCol(col){
  for(i=0; i<columns.length; i++)
    if(i==col)
      return columns[i]['data'];
  return '123';
}

function get_ratt_field(formula){
  // for(key in formula)
  //   if(key == 'rattrapable')
  //     return formula[key];

  if(formula['rattrapable'])
    return formula['rattrapable'];

  return 'cour';
}

hot.updateSettings({ cells: function(row, col, prop, td){
    var cell = hot.getCell(row, col);
    if(cell === undefined || cell === null)
      return cell;

    var current_field = GetColNameByCol(col);
    var fields_list = get_fields_list( data_arr[row]['formula'] );
    var is_rattrapage = data_arr[row]['is_rattrapage'];

    if(fields_list.indexOf(current_field) < 0)
      cell.readOnly = 'true';

    var ratt_field = get_ratt_field( data_arr[row]['formula'] );
    if( session_is_rattrapage && !(is_rattrapage && current_field==ratt_field) )
      cell.readOnly = 'true';

    if(session_is_closed)
      cell.readOnly = 'true';

    return cell;
  }
});

/********************/
/********************/
/********************/



$("#search").keyup(function(){
  filter(('' + this.value).toLowerCase());
});

$("#save").click(function(){
  clearTimeout(autosaveNotification);
  Save();
  message.innerHTML
     = '<b style="color: green;"><div class="shake-slow shake-constant"><font size="2">Data saved</font></div></b>';

  if (!autosave.checked)
    autosaveNotification = setTimeout(function() {
      shake_message();
    }, 1000);
});

function Save(){
  $.ajax({
    // url: '/grade/save/',
    url: '{{ url_for("grade_save") }}', 
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

// window.onbeforeunload = function (e) {
//     var e = e || window.event;
//     // For IE and Firefox prior to version 4
//     if (e) {
//         e.returnValue = 'Any string';
//     }
//     // For Safari
//     return 'Any string';
// };

// $(window).bind('beforeunload', function(){
//   console.log('leaving........');
//   alert('ffff');
//   var c = confirm ('Are you sure?');
//   return '>>>>>Before You Go<<<<<<<<  Your custom message go here';
// });


//////////////////////////////////////////////////////////////

function nullifyData(data_arr) {
  var row, r_len;
  for (row = 0, r_len = data_arr.length; row < r_len; row++) {
    for(var key in data_arr[row]){
      cols = ['cour', 'td', 'tp', 't_pers', 'stage'];
      if (cols.includes(key)){
        data = data_arr[row][key];
        if(data === '' || isNaN(data))
          data_arr[row][key] = null;
      }
    }
  }
  //maybe you can comment the next line
  //hot.loadData(data_arr);
  hot.validateCells(function() { hot.render(); });
  return data_arr;
}

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

//validate the range of input between 0 & 20
// var rangeValidator = function (value, callback) {
function rangeValidator(value, callback) {
  if ( value < 0 || value > 20 || isNaN(value) )
    callback(false);
  else
    callback(true);
}

function nameRenderer(instance, td) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  //td.style.backgroundColor = 'yellow';
  td.innerHTML = '<b>' + td.innerHTML + '</b>';
  return td;
}

function gradeRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);

  if(td.innerHTML !== '')
    td.innerHTML = Number(td.innerHTML).toFixed(2);
  else
    td.innerHTML = '';

  // coloring the read only cells
  if(cellProperties.readOnly=='true'){
    td.style.backgroundColor = '#EEE';
    td.innerHTML = '<i><font size="-1">' + td.innerHTML + '</font></i>';
  }

  //showing the original grade before rattrpage
  if(cellProperties.readOnly != 'true' && session_is_rattrapage == true){
    // original_grade = 'Avant Ratt.   ' + Number(data_arr[row]['original_grade']).toFixed(2)
    original_grade = Number(data_arr[row]['original_grade']).toFixed(2)
    if(td.innerHTML === '')
      td.innerHTML = '<font color="red" size="-1"><strike>'+original_grade+'</strike></font>';
    else
      td.innerHTML = '<div title="Avant Ratt.   '+original_grade+'">' + td.innerHTML + '</div>';
  }


  return td;
}

function averageRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.backgroundColor = '#EEE';
  if(td.innerHTML !== '')
    td.innerHTML = Number(td.innerHTML).toFixed(2);
  else
    td.innerHTML = '';
  
  if(cellProperties.readOnly=='true')
    td.innerHTML = '<b>' + td.innerHTML + '</b>';
  return td;
}

function creditRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.backgroundColor = '#EEE';
  td.innerHTML = '<b>' + td.innerHTML + '</b>';
  return td;
}

function formulaRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.backgroundColor = '#EEE';
  string = ' {';
  for(key in value)
      string = string + key + ':<b>' + value[key] + '</b>, ';
  string = string.substring(0, string.length - 2) + '} ';

  td.innerHTML = string;
  return td;
}

function autoSave(change, source) {
  if (source === 'loadData')
    return; //don't save this change
  if (!autosave.checked)
    return;
  
  clearTimeout(autosaveNotification);
  Save();
  message.innerHTML = '<div style="color: green;">Autosaved (cell)</div>';

  autosaveNotification = setTimeout(function() {
    shake_message(msg_autosaved);
  }, 1000);

  // $.ajax('/grade/save/', 
  //   'POST', 
  //   JSON.stringify({data: change}), function(data){
  //     message.innerText = 'Autosaved (' + 
  //       change.length + ' ' + 'cell' + (change.length > 1 ? 's' : '') + ')';
      // autosaveNotification = setTimeout(function() {
      //   message.innerText = msg_autosaved;
      // }, 2000);
  //   });
}

function calculateAverage(record, formula) {
  var average = 0;
  //traverse the formula and exclude credit
  for (key in formula) {
    if(key !== 'credit' && key !== 'coefficient' && key !== 'rattrapable') {
      var val = record[key];
      if(val === null || val === '')
        return null;
      var percentage = formula[key];
      average = average + (val * percentage);
    }
  }
  return Number(average).toFixed(2);
}

function calculateCredit(average, formula) {
  var credit = 0;
  if(average >= 10)
    credit = formula['credit'];
  
  if(average === null)
    credit = null;
  
  return credit;
}

function autoCalculate(change, source) {
  // commected it to allow calculation whan opening the grid
  // but that will cause hot to be undefined
  // if (source === 'loadData') return; 

  for(var i=0; i<data_arr.length; i++) {
    var formula = data_arr[i]['formula'];

    // average
    var average = calculateAverage(data_arr[i], formula);
    data_arr[i]['average'] = average;

    // credit
    var credit = calculateCredit(average, formula);
    data_arr[i]['credit'] = credit;
  }

  if (source !== 'loadData') 
    hot.render();

  // for (var i = 0; i < change.length; i++) {
  //   var ch = change[i]; var line = ch[0]; var col = ch[1]; var old = ch[2]; var val = ch[3];
  // }
}