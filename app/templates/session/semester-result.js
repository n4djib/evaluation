
var filter_word = "{{ params['filter_word'] }}";
var sort = {{ params['sort'] }};
var order = "{{ params['order'] }}";
var cols = {{ params['cols'] }};
var URL = "{{ params['URL'] }}";
var URL_PRINT = "{{ params['URL_PRINT'] }}";



sortTable( {{ params['sort'] }} , "{{ params['order'] }}" );

// launch at load from value in filter input
search ();

$('#filter').keyup(
  function () { search () }
)



change_url_params();



/*******************/
/*******************/
/*******************/

function change_url_params() {
  var _params = '';


  if(filter_word != "" && sort == 0 && cols == 2)
    _params = '?filter_word='+filter_word;

  if(filter_word == "" && sort != 0 && cols == 2)
    _params = '?cols='+cols;

  if(sort === 0)
    _params = '?filter_word='+filter_word+'&cols='+cols;
  else
     _params = '?filter_word='+filter_word+'&cols='+cols+'&sort='+sort+'&order='+order;
      

  // change url params
  window.history.pushState('*', '***', URL + _params);
  {% if print == True %}
  window.history.pushState('*', '***', URL_PRINT + _params);
  {% endif %}

  // change Print Button href
  var print_btn = document.getElementById('print-semester-result')
  if(print_btn !== null)
    print_btn.href = URL_PRINT + _params;
  
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



function sortTable(n, dir = "asc") {
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

      if (n !== 1 && n !== 2) {
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
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
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

