var options_arr = {{ (options_arr | safe) if options_arr else []  }};
var promos_with_options = get_promos_with_options();

function get_promos_with_options() {
  promos = [];
  for(const opt of options_arr){
    promos.push(opt[0]);
  }
  return promos;
}


var setting = {
  view: {
    dblClickExpand: false,
    fontCss: getFont,
    nameIsHTML: true,
    selectedMulti: false,
    addDiyDom: addDiyDom,
    
    //isHighLight: false  // i thought it will allow me to not show the highlight
  },
  check: {
    enable: true//checkbox
  },
  edit: {
    enable: false,
    editNameSelectAll: false
  },
  data: {
    simpleData: {
      enable: true
    }
  },
  callback: {
    onClick: onClick
  }
}; 

function getFont(treeId, node) {
  return node.font ? node.font : {};
}

function onClick(e,treeId, treeNode) {
  var zTree = $.fn.zTree.getZTreeObj("treeDemo");
  zTree.expandNode(treeNode);
}

function addDiyDom(treeId, treeNode) {
  var promo_id = parseInt( treeNode.id.replace('new_', '') );

  if ( Number.isInteger(promo_id) ) {
    var options = '';
    for(const opt_arr of options_arr) {
      var p_id = opt_arr[0];
      if(p_id == promo_id)
        options = opt_arr[1];
    }

    if(options != '') {
      // treeDemo_ 8 _a
      // treeDemo_ 47 _a
      var editStr = "<select id='diyBtn_" +treeNode.id+ "'>"+options+"</select>";
      var aObj = $("#" + treeNode.tId + "_a");
      aObj.after(editStr);


      // if(treeNode.tId == 'treeDemo_8')
      //   alert(treeNode.tId + ' - ' + treeNode.id);

      
      var btn = $("#diyBtn_"+treeNode.id);

      if (btn) btn.bind("change", function() {
        var href = aObj.attr("href");
        var index = href.indexOf("semester");
        //change the URL
        var new_href = href.substring(0, index+9) + btn.val() + '/';
        aObj.attr("href", new_href);
      });
    }

  }
  // else {

  //     // if (treeNode.id == 21) {
  //       // var editStr = "<span class='demoIcon' id='diyBtn_" +treeNode.id+ "' title='"+treeNode.name+"' onfocus='this.blur();'><span class='button icon01'></span></span>";
  //       var editStr = "<span class='demoIcon' id='diyBtn_14 title='"+treeNode.name+"' onfocus='this.blur();'><span class='button icon01'></span></span>";
  //       aObj.append(editStr);
  //       var btn = $("#diyBtn_"+treeNode.id);
  //       if (btn) btn.bind("click", function(){alert("diy Button for " + treeNode.name);});
  //     // }
  // }
}

var zNodes = {{ zNodes | safe }};;

$(document).ready(function(){
  $.fn.zTree.init($("#treeDemo"), setting, zNodes);
  //initialize fuzzysearch function
  fuzzySearch('treeDemo','#key', null, true); 
  // fuzzySearch('treeDemo','#key', isHighLight, true); 
});




