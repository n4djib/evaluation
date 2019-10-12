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
  { data: 'credit', type: 'numeric' },
  { data: 'credit_app', type: 'numeric', readOnly: true },
  { data: 'credit_cumul', type: 'numeric', readOnly: true },
  { data: 'decision', type: 'text' },

  { data: 'semester', type: 'text', width: 80, readOnly: true },
  { data: 'average_s', type: 'numeric' },
  { data: 'average_app_s', type: 'numeric', readOnly: true },
  { data: 'credit_s', type: 'numeric' },
  { data: 'credit_app_s', type: 'numeric', readOnly: true },

  // { data: 'R', type: 'numeric' },
  // { data: 'R_app', type: 'numeric', readOnly: true },
  // { data: 'S', type: 'numeric' },
  // { data: 'S_app', type: 'numeric', readOnly: true },
  // { data: 'avr_classement', type: 'numeric', /*width: 12,*/ readOnly: true },
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
    'Moy a', '(Moy a)', 'Cr a', '(Cr a)', '(Cr Cumul)', 'Decision', 
    '(Semester)', 'Moy s', '(Moy s)', 'Cr s', '(Cr s)', 
    'R', '(R)', 'S', '(S)', '(((Moy Classement)))'],
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


