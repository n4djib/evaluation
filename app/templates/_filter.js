
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

}


$('#filter').keyup(
  function () { search () }
)

