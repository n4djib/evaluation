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
  { 
    data: 'decision', 
    type: 'dropdown',
    source: ['yellow', 'red', 'orange', 'green', 'blue', 'gray', 'black', 'white'] 
  },
  { data: 'R', type: 'numeric' },
  { data: 'R_app', type: 'numeric', readOnly: true },
  { data: 'S', type: 'numeric' },
  { data: 'S_app', type: 'numeric', readOnly: true },
  { data: 'avr_classement', type: 'numeric', /*width: 12,*/ readOnly: true },

  { data: 'semester', type: 'text', width: 80, readOnly: true },
  { data: 'average_s', type: 'numeric' },
  { data: 'average_app_s', type: 'numeric', readOnly: true },
  { data: 'credit_s', type: 'numeric' },
  { data: 'credit_app_s', type: 'numeric', readOnly: true },

];

container.innerHTML = ""; 

hot = new Handsontable(container, {
  data: data_arr,
  rowHeaders: false,
  columnSorting: false,
  sortIndicator: true,
  manualColumnResize: true,
  // colHeaders: true,
  //saisir
  colHeaders: ['--ID--', '#', 'Name', '(Annee)', 
    'Moy a', '(Moy a)', 'Cr a', '(Cr a)', '((Cr Cumul))', 'Decision', 
    'R', '(R)', 'S', '(S)', 
    '(((Moy Clas.)))',
    '(Semester)', 'Moy s', '(Moy s)', 'Cr s', '(Cr s)'],
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


$("#save").click(function(){
  Save();
});


function Save(){
  $.ajax({
    // url: '/grade/save/',
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



