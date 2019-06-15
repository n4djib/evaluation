
function init_icons() {
  //find all sort- and loop through
  var icons = document.getElementsByClassName("sort-icon");
  for (var i = 0; i < icons.length; i++) {
    icons[i].src = "/static/img/sort-icons.png";
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


function sortTable(n) {
  init_icons();

  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  // table = document.getElementById("sort");
  table = document.getElementById("sort_tbody");
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 0; i < (rows.length - 2); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i+1].getElementsByTagName("TD")[n];

      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      var _x = "0000"+x.innerHTML.toLowerCase();
      var _y = "0000"+y.innerHTML.toLowerCase();

      if(n == 0){
        _x = "0000"+_x
        _y = "0000"+_y
        _x = _x.substring(_x.length-4, _x.length);
        _y = _y.substring(_y.length-4, _y.length);
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

  /****************************/
  //change icon
  // change_icons(n, dir);
}


