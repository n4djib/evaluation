
var filter_word = "{{ params['filter_word'] }}";
var sort = {{ params['sort'] }};
var order = "{{ params['order'] }}";
var cols = {{ params['cols'] }};
var layout = "{{ params['layout'] }}";

var URL = "{{ params['URL'] }}";
var URL_PRINT = "{{ params['URL_PRINT'] }}";



sortTable( {{ params['sort'] }} , "{{ params['order'] }}" );

// launch at load from value in filter input
search ();

$('#filter').keyup(
  function () {
    search();
  }
);



if(layout === "landscape") {
  $('#checkbox-landscape').prop("checked", true);
} else {
  $('#checkbox-landscape').prop("checked", false);
}

if(cols == 3) {
  $('#checkbox-session').prop("checked", true);
}
if(cols == 2) {
  $('#checkbox-session').prop("checked", false);
}

$('#checkbox-session').change(function() {
    if(this.checked)
      cols = 3;
    else
      cols = 2;


    _params = change_url_params();

    // var new_url = location.origin + location.pathname + _params
    // console.log(new_url);
    var new_url = location.protocol + '//' + location.host + location.pathname + _params
    console.log(new_url);

    window.location.replace( new_url );
});




$('#checkbox-landscape').change(function() {

  if(this.checked)
    layout = 'landscape';
  else
    layout = 'portrait';

  _params = change_url_params();
  console.log(_params);
});



change_url_params();


/*******************/
/*******************/
/*******************/

function change_url_params() {
  var _params = '';

  // if(filter_word != "" && sort == 0 && cols == 2)
  //   _params = '?filter_word='+filter_word;

  // if(filter_word == "" && sort != 0 && cols == 2)
  //   _params = '?cols='+cols;

  // if(sort === 0 && filter_word == "" && cols == 2)
  //   _params = ''
  // else
  //   if(sort === 0)
  //     _params = '?filter_word='+filter_word+'&cols='+cols;
  //   else
  //      _params = '?filter_word='+filter_word+'&cols='+cols+'&sort='+sort+'&order='+order;
  
  var param_obj = {
    filter_word: filter_word,
    cols: cols,
    sort: sort,
    order: order,
    layout: layout,
  };

  // _params = $.param(param_obj);

  // var filter_word = "", sort = 0, order = "desc", cols = 2, layout = "";  

  // console.log('filter_word '+param_obj['filter_word'].length);
  // console.log(param_obj['filter_word'])

  var array = [];
  if (param_obj['filter_word'].length > 0)
    array.push('filter_word='+param_obj['filter_word']);
  if (param_obj['sort'] !== 0)
    array.push('sort='+param_obj['sort']);
  if (param_obj['order'] !== "desc")
    array.push('order='+param_obj['order']);
  if (param_obj['cols'] !== 2)
    array.push('cols='+param_obj['cols']);
  if (param_obj['layout'] !== "landscape")
    array.push('layout='+param_obj['layout']);

  console.log('array');
  console.log(array);
  // console.log('filter_word');
  // console.log(param_obj['filter_word']);

  for(var i=0; i<array.length; i++) {
    _params += array[i]+'&';
  }

  if(_params !== '')
    _params = '?'+_params



  // change url params
  window.history.pushState('*', '***', URL + _params);
  {% if print == True %}
  window.history.pushState('*', '***', URL_PRINT + _params);
  {% endif %}

  // change Print Button href
  var print_btn = document.getElementById('print-semester-result')
  if(print_btn !== null)
    print_btn.href = URL_PRINT + _params;

  return _params;
}



function init_icons() {
  //find all sort- and loop through
  var icons = document.getElementsByClassName("sort-icon");
  for (var i = 0; i < icons.length; i++) {
    {% if print == True %}
    icons[i].src = "";
    {% else  %}
    icons[i].src = "/static/img/sort-icons.png";
    {% endif  %}
  } 
}

function change_icons(n, dir) {
  //find sort-n
  var icon = document.getElementById("sort-"+n);
  if (dir == 'asc')
    icon.src = "/static/img/sort-icons-asc.png";
  else
    icon.src = "/static/img/sort-icons-decs.png";
}



function sortTable(n, dir = "desc") {
  if (n === 0)
    return;

  init_icons();

  var table, rows, switching, i, x, y, shouldSwitch, /*dir,*/ switchcount = 0;
  // table = document.getElementById("sort");
  table = document.getElementById("sort_tbody");
  switching = true;
  //Set the sorting direction to ascending:
  /*dir = "asc";*/  
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 0; i < (rows.length - 1); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i+1].getElementsByTagName("TD")[n];

      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      var _x = x.innerHTML.toLowerCase();
      var _y = y.innerHTML.toLowerCase();

      // all numerics
      if (n != 1 && n != 2) {
        _x = parseFloat( x.innerHTML.toLowerCase() );
        _y = parseFloat( y.innerHTML.toLowerCase() );
      }

      if (dir == "asc") {
        if (_x > _y) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (_x < _y) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }

    change_icons(n, dir);

    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      // var r = rows[i].getElementsByTagName("TD")[0].textContent;
      // console.log(r);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/

      // if (switchcount == 0 && dir == "asc") {
      //   dir = "desc";
      //   switching = true;
      // }
      if (switchcount == 0 && dir == "desc") {
        dir = "asc";
        switching = true;
      }
    }

  }

  // running it in search is enaugh
  reindex();

  // change_url_params
  sort = n;
  order = dir;
  change_url_params();
}


function search () {
  $('.searchable tr').hide();

  var vals = $('#filter').val().split(",");
  vals = vals.filter(item => item.trim() !== "");


  // to not return emty list when filter keyword is null
  if(vals == "")
    $('.searchable tr').filter(function () { return true; }).show();
    
  // var index = 1;
  for(let i=0; i<vals.length; i++){
    $('.searchable tr').filter(function () {
      var rex = new RegExp( vals[i].trim() , 'i');
      var t = rex.test( $(this).text() );
      return t;
    }).show();
  }

  // reindex
  reindex();

  // change_url_params
  filter_word = vals;
  change_url_params();
}

function isHidden(elem) {
  return !!( elem.offsetWidth || elem.offsetHeight );
}

function reindex(){
  var rows = document.getElementById("sort_tbody").rows;
  console.log('reindexing');
  var index = 1;
  for (i = 0; i < (rows.length ); i++) {

    if( isHidden( rows[i] ) ){
      // console.log('visible');
      rows[i].getElementsByTagName("TD")[0].textContent = index;
      index += 1;
    }

  }
}

