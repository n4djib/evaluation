var container = document.getElementById('classement-laureats');

var data_arr = {{ data_arr | safe | replace('None', 'null') }};

var decisions_list = {{ decisions_list | safe }};
var mergeCells = {{ mergeCells | safe | replace('None', 'null') }};
var years = '{{ years | safe }}';

var hot;



var mode = '{{ mode | safe }}';
var hiddenColumns = null;



// hiddenColumns = [0, 5, 7,     9,    10, 12, 14, 18, 20, 22, 24, 26];

// hide app fetched
// if(mode == 'unfetched') {
  hiddenColumns = [0, 6, 8,   9/*cumul*/,    11, 13, 15, /*16*/, 19, 21, 23, 25, 27, /*28*/];
// }



if(mode == 'all') {
  // hiddenColumns = [3, 9,    16, 28];
  hiddenColumns = [];
}

// if(mode == 'classement') {
//   hiddenColumns = [0, 6, 8,     9,     11, 13, 15, 16, 19, 21, 23, 25, 27, 28];
// }

// if(mode == 'progression') {
//   hiddenColumns = [0, 3, 6, 8,     9,     11, 12, 13, 14, 15, 16, 19, 21,22,23,24,25,26,27,28];
// }

// if(mode == 'fetched') {
//   hiddenColumns = [0, 5, 7,     9,     10, 12, 14, 18, 20, 22, 24, 26];
// }

// hide app fetched
if(mode == 'unfetched') {
  hiddenColumns = [0, 6, 8, 9,    11, 13, 15, /*16*/16, 19, 21, 23, 25, 27, /*28*/28];
}








var columns = [
  { data: 'id', type: 'text', width: 1, readOnly: true },
  { data: 'index', type: 'text', width: 20/*shrink rather than width*/, readOnly: true },
  { data: 'name', type: 'text',    width: 100,           readOnly: true },
  { data: 'average', type: 'numeric', readOnly: true },

  { data: 'year', type: 'text', width: 55, readOnly: true, renderer: centerRenderer },
  { data: 'average_a', type: 'numeric', renderer: fillEmptyDecimalRenderer },
  { data: 'average_app_a', type: 'numeric', readOnly: true },
  { data: 'credit_a', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'credit_app_a', type: 'numeric', readOnly: true },
  { data: 'credit_cumul', type: 'numeric', readOnly: true },
  {
    data: 'decision', 
    type: 'dropdown',
    source: decisions_list,
    width: 120
    , renderer: fillEmptyDecisionRenderer
  },
  { data: 'decision_app', type: 'text', readOnly: true },

  { data: 'R', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'R_app', type: 'numeric', readOnly: true },
  { data: 'S', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'S_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement_a', type: 'numeric', /*width: 12,*/ readOnly: true },

  { data: 'semester', type: 'text', width: 80, readOnly: true, renderer: centerRenderer },
  { data: 'average_s', type: 'numeric', renderer: fillEmptyDecimalRenderer },
  { data: 'average_app_s', type: 'numeric', readOnly: true },
  { data: 'credit_s', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'credit_app_s', type: 'numeric', readOnly: true },

  { data: 'b', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'b_app', type: 'numeric', readOnly: true },
  { data: 'd', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 'd_app', type: 'numeric', readOnly: true },
  { data: 's', type: 'numeric', renderer: fillEmptyTextRenderer },
  { data: 's_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement_s', type: 'numeric', /*width: 3,*/ readOnly: true },
];


customBorders = [
  {
    range: {
      from: { row: 0, col: 1 },
      to: { row: 5, col: 28 }
    },
    top: { width: 2, color: '#5292F7' },
    left: { width: 2, color: 'orange' },
    bottom: { width: 2, color: 'red' },
    right: { width: 2, color: 'magenta' }
  },
  {
    row: 2, col: 2,
    left: { width: 2, color: 'red' },
    right: { width: 1, color: 'green' }
  }
];



container.innerHTML = ""; 

hot = new Handsontable(container, {
  data: data_arr,
  rowHeaders: false,
  columnSorting: false,
  sortIndicator: true,
  manualColumnResize: true,
  //saisir
  colHeaders: ['--ID--', '#', 'Name', '[[Moy Clas.]]', '(Annee)', 
    'Moy a', '(Moy a)', 'Cr a', '(Cr a)', '((Cr Cumul))', 'dec', '(dec)', 
    'R', '(R)', 'S', '(S)',  '[[Moy Clas. a]]',
    '(Semester)', 'Moy s', '(Moy s)', 'Cr s', '(Cr s)', 
    'b', '(b)', 'd', '(d)', 's', '(s)', '[[Moy Clas. s]]'
  ],
  stretchH: "all",
  nestedRows: true,
  contextMenu: true,
  mergeCells: mergeCells,
  columns: columns,
  hiddenColumns: {
    columns: hiddenColumns,
    /* hide app fields */
    // columns: [0, 6, 8, 11, 13, 15, 16, 19, 21, 23, 25, 27, /*28*/],
    /* show progression */
    // columns: [0, 3, 6, 8, 11, 12, 13, 14, 15, 16, 19, 21,22,23,24,25,26,27,28],
    indicators: false
  },

  // customBorders: customBorders,


});


$("#save").click(function(){
  Save();
});


function Save() {
  $.ajax({
    url: '{{ url_for("classement_laureats_save") }}', 
    type: 'POST',
    data: JSON.stringify( data_arr ),
    contentType: 'application/json; charset=utf-8',
    dataType: 'text',
    async: true,
    success: function(msg) {
      console.log('success');
      console.log(msg);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      console.log('some error');
      alert("some error");
    }
  });

}





function getDataCell(instance, td, row, col,  format='', align='right') {
  // if Empty -> grab the adjacent cell data
  if(td.innerHTML === '') {
    var data = instance.getDataAtCell(row, col+1);
    if (data !== null) {
      td.innerHTML = data;
      if (format === 'Number')
        td.innerHTML = Number(data).toFixed(2);
    }
  }
  else {
    td.style.backgroundColor = 'yellow';
    if (format === 'Number')
      td.innerHTML = Number(parseFloat(td.innerHTML)).toFixed(2);

  }
  td.innerHTML = '<b>' + td.innerHTML + '</b>';
  td.style.textAlign = align;
  return td
}


function fillEmptyDecimalRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  return getDataCell(instance, td, row, col,   'Number', 'right');
}

function fillEmptyTextRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  return getDataCell(instance, td, row, col,   '', 'center');
}

function fillEmptyDecisionRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  return getDataCell(instance, td, row, col,   '', 'left');
}


function centerRenderer(instance, td, row, col, prop, value, cellProperties) {
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.textAlign = 'center';
  td.innerHTML = '<b><i>' + td.innerHTML + '</i></b>';
  return td;
}


// $("#search").keyup(function(){
//   filter(('' + this.value).toLowerCase());
// });

// function filter(search) {
//   var row, r_len;
//   var data = data_arr;
//   var array = [];
//   for (row = 0, r_len = data.length; row < r_len; row++) {
//     // d = data[row];
//     // for(var key in d) {
//     //   var value = d[key];
//     //   if( ('' + value).toLowerCase().indexOf(search) > -1) {
//     //     array.push(d);
//     //     break;
//     //   }
//     // }
//     var value = data[row][name];
//     if( ('' + value).toLowerCase().indexOf(search) > -1) {
//       array.push(data[row]);
//       break;
//     }
//   }
//   hot.loadData(array);
//   hot.validateCells(function() { hot.render(); });
// }


