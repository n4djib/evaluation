
    $(document).ready(function () {
      (function ($) {
        $('#filter').keyup(function () {
            $('.searchable tr').hide();

            // var vals = $(this).val().split(" ");
            // vals = vals.filter(item => item !== "");

            var vals = $(this).val().split(",");
            // console.log("1 -- " + vals);
            vals = vals.filter(item => item.trim() !== "");
            // console.log("2 -- " + vals);

            for(let i=0; i<vals.length; i++){
              console.log( vals[i] );
              $('.searchable tr').filter(function () {
                  var rex = new RegExp( vals[i].trim() , 'i');
                  return rex.test( $(this).text() );
              }).show();
            }
        })
      }(jQuery));
    });

    // $(document).ready(function () {
    //   (function ($) {
    //     $('#filter').keyup(function () {
    //         var rex = new RegExp($(this).val(), 'i');
    //         var choice = "";
    //         $('.searchable tr').hide();
    //         $('.searchable tr').filter(function () {
    //             return rex.test( $(this).text() );
    //         }).show();
    //     })
    //   }(jQuery));
    // });
    