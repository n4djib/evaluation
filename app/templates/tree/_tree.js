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

  async: {
    enable: true,
    url: getUrl
  },
  callback: {
    onClick: onClick,

    beforeExpand: beforeExpand,
    onAsyncSuccess: onAsyncSuccess,
    onAsyncError: onAsyncError
  }
}; 


//async
var log, 
    className = "dark",
    startTime = 0, 
    endTime = 0, 
    perCount = 100, 
    perTime = 100;

function getUrl(treeId, treeNode) {
  var promo_id = parseInt( treeNode.id.replace('promo_', '') )
  // alert(treeId+' - '+id+' - '+promo_id);
  return '/get_async_sessions_by_promo/'+promo_id+'/'
}

function beforeExpand(treeId, treeNode) {
  if (!treeNode.isAjaxing) {
    startTime = new Date();
    treeNode.times = 1;
    ajaxGetNodes(treeNode, "refresh");
    return true;
  } else {
    alert("Downloading data, Please wait to expand node...");
    return false;
  }
}

function onAsyncSuccess(event, treeId, treeNode, msg) {
  if (!msg || msg.length == 0) {
    return;
  }
  var zTree = $.fn.zTree.getZTreeObj("treeDemo"),
  totalCount = treeNode.count;
  if (treeNode.children.length < totalCount) {
    setTimeout(function() {ajaxGetNodes(treeNode);}, perTime);
  } else {
    treeNode.icon = "";
    zTree.updateNode(treeNode);
    zTree.selectNode(treeNode.children[0]);
    endTime = new Date();
    var usedTime = (endTime.getTime() - startTime.getTime())/1000;
    className = (className === "dark" ? "":"dark");
    showLog("[ "+getTime()+" ]&nbsp;&nbsp;treeNode:" + treeNode.name );
    showLog("Child node has finished loading, a total of "+ (treeNode.times-1) +" times the asynchronous load, elapsed time: "+ usedTime + " seconds ");
  }
}

function onAsyncError(event, treeId, treeNode, XMLHttpRequest, textStatus, errorThrown) {
  var zTree = $.fn.zTree.getZTreeObj("treeDemo");
  alert("ajax error...");
  treeNode.icon = "";
  zTree.updateNode(treeNode);
}

    function ajaxGetNodes(treeNode, reloadType) {
      var zTree = $.fn.zTree.getZTreeObj("treeDemo");
      if (reloadType == "refresh") {
        treeNode.icon = "/static/ztree/img/loading.gif";
        zTree.updateNode(treeNode);
      }
      zTree.reAsyncChildNodes(treeNode, reloadType, true);
    }
   
    function showLog(str) {
      if (!log) log = $("#log");
      log.append("<li class='"+className+"'>"+str+"</li>");
      if(log.children("li").length > 4) {
        log.get(0).removeChild(log.children("li")[0]);
      }
    }
    
    function getTime() {
      var now= new Date(),
      h=now.getHours(),
      m=now.getMinutes(),
      s=now.getSeconds(),
      ms=now.getMilliseconds();
      return (h+":"+m+":"+s+ " " +ms);
    } 

//

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
}

var zNodes = {{ zNodes | safe }};;

$(document).ready(function(){
  $.fn.zTree.init($("#treeDemo"), setting, zNodes);
  //initialize fuzzysearch function
  // fuzzySearch('treeDemo','#key', null, true); 
  fuzzySearch('treeDemo','#key', null, true); 
  // fuzzySearch('treeDemo','#key', isHighLight, true); 
});




