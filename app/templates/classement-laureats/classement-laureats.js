var container = document.getElementById('classement-laureats');

var data_arr = {{ data_arr | safe | replace('None', 'null') }};

var mergeCells = {{ mergeCells | safe | replace('None', 'null') }};

var years = '{{ years | safe }}';

var hot;



var columns = [
  { data: 'id', type: 'text', width: 1, readOnly: true },
  { data: 'index', type: 'text', width: 20/*shrink rather than width*/, readOnly: true },
  { data: 'name', type: 'text', readOnly: true },
  { data: 'year', type: 'text', width: 55, readOnly: true },
  { data: 'average', type: 'numeric' },
  { data: 'average_app', type: 'numeric', readOnly: true },
  { data: 'R', type: 'numeric' },
  { data: 'R_app', type: 'numeric', readOnly: true },
  { data: 'S', type: 'numeric' },
  { data: 'S_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement', type: 'numeric', /*width: 12,*/ readOnly: true },
];

container.innerHTML = ""; 

hot = new Handsontable(container, {
  data: data_arr,
  rowHeaders: false,
  columnSorting: true,
  sortIndicator: true,
  manualColumnResize: true,
  // colHeaders: true,
  //saisir
  colHeaders: ['--ID--', '#', 'Name', '(Annee)', 
    'Moy', '(Moy app)', 'R', '(R app)', 'S', '(S app)', '(Moy Classement)'],
  stretchH: "all",
  nestedRows: true,
  contextMenu: true,
  mergeCells: mergeCells,
  columns: columns,
  // hiddenColumns: {
  //   columns: [0],
  //   indicators: false
  // }
});

