var container = document.getElementById('classement-laureats');

var data_arr = {{ data_arr | safe | replace('None', 'null') }};

var decisions_list = {{ decisions_list | safe }};
var mergeCells = {{ mergeCells | safe | replace('None', 'null') }};
var years = '{{ years | safe }}';

var hot;



var mode = '{{ mode | safe }}';
var hiddenColumns = null;

if(mode == 'classement') {
  hiddenColumns = [0, 6, 8, 11, 13, 15, 16, 19, 21, 23, 25, 27, 28];
}

if(mode == 'progression') {
  hiddenColumns = [0, 3, 6, 8, 11, 12, 13, 14, 15, 16, 19, 21,22,23,24,25,26,27,28];
}




var columns = [
  { data: 'id', type: 'text', width: 1, readOnly: true },
  { data: 'index', type: 'text', width: 20/*shrink rather than width*/, readOnly: true },
  { data: 'name', type: 'text', readOnly: true },
  { data: 'average', type: 'numeric', readOnly: true },

  { data: 'year', type: 'text', width: 55, readOnly: true },
  { data: 'average_a', type: 'numeric' },
  { data: 'average_app_a', type: 'numeric', readOnly: true },
  { data: 'credit_a', type: 'numeric' },
  { data: 'credit_app_a', type: 'numeric', readOnly: true },
  { data: 'credit_cumul', type: 'numeric', readOnly: true },
  {
    data: 'decision', 
    type: 'dropdown',
    source: decisions_list,
    width: 120
  },
  { data: 'decision_app', type: 'text', readOnly: true },

  { data: 'R', type: 'numeric' },
  { data: 'R_app', type: 'numeric', readOnly: true },
  { data: 'S', type: 'numeric' },
  { data: 'S_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement_a', type: 'numeric', /*width: 12,*/ readOnly: true },

  { data: 'semester', type: 'text', width: 80, readOnly: true },
  { data: 'average_s', type: 'numeric' },
  { data: 'average_app_s', type: 'numeric', readOnly: true },
  { data: 'credit_s', type: 'numeric' },
  { data: 'credit_app_s', type: 'numeric', readOnly: true },

  { data: 'b', type: 'numeric' },
  { data: 'b_app', type: 'numeric', readOnly: true },
  { data: 'd', type: 'numeric' },
  { data: 'd_app', type: 'numeric', readOnly: true },
  { data: 's', type: 'numeric' },
  { data: 's_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement_s', type: 'numeric', /*width: 3,*/ readOnly: true },
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
    'Moy a', '(Moy a)', 'Cr a', '(Cr a)', '((Cr Cumul))', 'dec', '(dec 11)', 
    'R', '(R)', 'S', '(S)',  '[[Moy Clas. a]16]',
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

  customBorders: [
  {
    range: {
      from: {
        row: 0,
        col: 1
      },
      to: {
        row: 5,
        col: 28
      }
    },
    top: {
      width: 2,
      color: '#5292F7'
    },
    left: {
      width: 2,
      color: 'orange'
    },
    bottom: {
      width: 2,
      color: 'red'
    },
    right: {
      width: 2,
      color: 'magenta'
    }
  },
  // {
  //   row: 2,
  //   col: 2,
  //   left: {
  //     width: 2,
  //     color: 'red'
  //   },
  //   right: {
  //     width: 1,
  //     color: 'green'
  //   }
  // }
  ]


});


$("#save").click(function(){
  Save();
});


function Save(){
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



