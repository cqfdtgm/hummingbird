function addTab(title, url){ 
if ($('#tt').tabs('exists', title)){ 
$('#tt').tabs('select', title); 
} else { 
var content = '<iframe scrolling="hidden" frameborder="0"  src="'+url+'" style="overflow-y:hidden;overflow-x:hidden;height:99%;width:100%"></iframe>' 
/* 这儿的高度不能使用100%， 否则多显示一个滚动条， 很奇特	*/
$('#tt').tabs('add',{ 
title:title, 
content:content,
fit:true,
closable:true
    ,height:'99%'
    ,style:"overflow-x:'hidden';overflow-y:'hidden'"
}); 
} 
} 

//  # 数据网格装载时，要将换行符，大小于符号等转义。
//  注意有坑：树形数据网格初次装入时为{total:3, rows:[{re1:0}]} 这种格式，但是展开时，是直接为rows里面的内容这种格式。要区别展开
//  content的内容只显示前100个字符，如有更多，在新的对话框或窗口中打开。
function esc_content(data) {
    if (data.rows!=undefined) {
	console.log(data.rows);
	data.rows = esc_rows(data.rows);
	console.log('OK rows');
	return data;
    }else {
	return esc_rows(data);
    }
}

function esc_str(str, row, index) {
    if (typeof(str) != "string") {
	return str;
    }
    if ('filename' in row && str==row.filename &&str!="") {  //增加下载链接
	res = "<a class='easyui-linkbutton' href='./_download?fileid=" + row.fileid + "'>"+row.filename+"</a>";
	return res;
    }
    res = $('<div />').text(str.substring(0,50)).html().replace(/\n/g,"<br />");
    if (str.length>50) {
	 res = res + "...更多..."
    }
    return res
}

var content_org = new Array();

function esc_rows(data) {
    if (data[0].content==undefined) {
	return data;
    }
    for (i=0; i<data.length;i++) {
	con = data[i].content;
	data[i].content = $('<div />').text(con.substring(0,50)).html().replace(/\n/g,"<br>"); 
	if (con.length>50) {
	    console.log(con.substring(0,50));
	    data[i].content_org = con;
	    data[i].content = data[i].content + "<br /><a href='#' class='easyui-linkbutton' onclick='javascript:more("+data[i].id+")'>...显示全部</a>"
	    content_org[data[i].id] = con;
	}
    }
    return data;
}

function addSubTab(title, url) {
var jq = top.jQuery;

if (jq("#tt").tabs('exists', title)) {
  jq("#tt").tabs('select', title);
} else {
  var content = '<iframe scrolling="auto" src="'+url+'" style="width:100%;height:100%;overflow:hidden;padding:10px;"></iframe>';
  jq("#tt").tabs('add', { title:title, content:content, closable:true, style:"overflow:'hidden';padding:'10px'"});
  }
  }

function test() {
    alert ('haha') ; 
}

/* 覆盖全局的onBeforeDestroy 事件, 以使tabs能正确释放内存 */
/*
$.fn.panel.defaults = $.extend({},$.fn.panel.defaults,{onBeforeDestroy:function(){  
    var frame=$('iframe', this);  
     if(frame.length>0){  
         frame[0].contentWindow.document.write('');  
         frame[0].contentWindow.close();  
         frame.remove();  
         if($.browser.msie){  
	 //if(!$.support.leadingWhitespace) {
	 
             CollectGarbage();  
         } 
     }  
     }  
 }); 
*/
/*
function myescape (data) {
    for (var i=0; i<data.rows.length;i++) {
	for (var att in data.rows[i]) {
	    if (typeof(data.rows[i][att])=="string") {
		data.rows[i][att] = data.rows[i][att].replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\r\n/g,'<br />');
	    };
	}
    }
    return data;
}
*/
function rf1() //一次性删除左边表格选中的记录, 成功的话刷新左右两个表格.
{
    ids = $('#dg1').datagrid('getSelections');
    //alert(ids);
    if (ids.length>0) {
	var delid = [];
	for (i in ids) {
	    delid.push(ids[i].id); } 
	//alert (delid);
	// 以array为参数提交的表单, 变量名会变为变量后面加方括号字样, 比如"id[]"
	$.getJSON($('#dg1').datagrid('options').destroyUrl, {id:delid}, function(json, status, jqr) {
	    if (status=="success") {
		$('#dg1').edatagrid('reload');
		$('#dg2').edatagrid('reload');
	    }
	});
    $('#dg1').datagrid('clearSelections');
    }
}
function rf2() //一次性删除右边选中的多个表格, 成功的话刷新左右两个表格
{
    ids = $('#dg2').datagrid('getSelections');
    if (ids.length>0) {
	//$('#dg2').datatgrid('clearChecked');
	var addid = [];
	for (i in ids) {
	   addid.push(ids[i].id); }
	//alert(addid);
	$.getJSON($('#dg2').datagrid('options').destroyUrl, {id:addid}, function(json, status, jqr) {	// aid: 主表中处于选中状态的行的id，这样就不需要通过session来保存aid了。
	//#$.getJSON('Save', {id:addid, aid:$('#dg').datagrid('getSelected').id}, function(json, status, jqr) {	// aid: 主表中处于选中状态的行的id，这样就不需要通过session来保存aid了。
	    if (status=="success") {
		$('#dg1').edatagrid('reload');
		$('#dg2').edatagrid('reload');
	    }
	});
    $('#dg2').datagrid('clearSelections');
    }
}

function setCookie(name, value, expires, path, domain, secure)
{
	var curCookie = name + "=" + encodeURI(value)
		+ ((expires) ? "; expires=" + expires.toGMTString() : "")
		+ ((path) ? "; path=" + path : "")
		+ ((domain) ? "; domain=" + domain : "")
		+ ((secure) ? "; secure" : "")
	document.cookie = curCookie
}

function getCookie(name)
{
	if (document.gookie.length>0)
	{
		start = document.cookie.indexOf(name+"=")
		if (start!=-1)
		{
			start = start+name.length+1
			end = document.cookie.indexOf(";",start)
			if (end==-1)
				end = document.cookie.length
			return docodeURI(document.cookie.substring(start,end))
		}
	}
	return ""
}
function delCookie(name) {
	var now = new date();
	now.setTime( now.getTime()-1);
	var v="";
	document.cookie = name + "=" + v + "; expire=" + now.toGMTString();
}

//  用于dataview 和treegrid的弹出窗口进行增，改，more， 删除的js函数。如果有通用性，则共用之。
function newBook() {
    console.log('newBook');
    //if($('#dlg').dialog('options').closed != true) {
    $('#dlg').dialog('open').dialog('center');
    //}	//防止重新打开和定位
    $('#dlg').dialog('setTitle','发布');
    $('#dlg_save').show();  //	显示保存按钮
    $('#fm').form('clear');
    $('#filebox').show();
    $('#fileid').hide();
    $('#filename').hide();
    url = 'Save?_log=false';
    action = 'newBook()';
}

var action_row;

function moreBook(row) {	//对于datagrid detail view, 要对展开的内容进行修改修改和显示全部,有2种选择:1.修改MORE和EDIT函数 2.在里面显示框架,每个子表显示菜单栏.
    if (!row) {
	var row = $('#dg').datagrid('getSelected');
	if (!row) {
	    row = action_row;
	}
    }
    if (row) {
	//if($('#dlg').dialog('options').closed == true) {
	 //   $('#dlg').dialog('open').dialog('center');
	//}	//防止重新打开
	//  总是重新关闭后打开,这样滚动时才能在正确位置打开.除非对话框用浮动定位始终显示在屏幕上.
	$('#dlg').dialog('close');
	$('#dlg').dialog('open').dialog('center');
	$('#dlg').dialog('setTitle','显示全部内容 #'+row.id);
	$('#dlg_save').hide();
	$('#filebox').hide();
	if (row.fileid>0) {
	    $('#fileid').show();
	    $('#filename').show();
	}
	else {
	    $('#fileid').hide();
	    $('#filename').hide();
	}
	$('#fm').form('load', row);
	action = "moreBook()";
	action_row = row;
    }
}
function mmoreBook(row) {   // 对于使用移动端，dialog改为navpanel
    //$.messager.show({'title':'error'});
    if (!row) {
	var row = $('#dg').datagrid('getSelected');
	if (!row) {
	    row = action_row;
	}
    }
    if (row) {
	//if($('#dlg').dialog('options').closed == true) {
	//    $('#dlg').dialog('open').dialog('center');
	//}	//防止重新打开
	//$.mobile.go('#p2');
	//$('#dlg').dialog('setTitle','显示全部内容 #'+row.id);
	$('#p2-title').html('修改 #'+row.id);
	//$('#dlg_save').hide();
	$('#filebox').hide();
	if (row.fileid>0) {
	    $('#fileid').show();
	    $('#filename').show();
	}
	else {
	    $('#fileid').hide();
	    $('#filename').hide();
	}
	$('#fm').form('load', row);
	action = "moreBook()";
	action_row = row;
	edit_no();	// 禁止编辑
	console.log($('.easyui-textbox'));
	$('#mm-r2').empty();
	$('#mm-r2').menu('appendItem', {
	    text:'修改',iconCls:'icon-edit', onClick:toEdit});
	$('#mm-r2').menu('appendItem', {
	    text:'回复',iconCls:'icon-edit', onClick:toEdit});

    }
}

function editBook(row) {
    if (!row) {
	var row = $('#dg').datagrid('getSelected');
	if (!row) {
	    row = action_row;
	} 
    }
    if (row) {
	if($('#dlg').dialog('options').closed == true) {
	    $('#dlg').dialog('open').dialog('center');
	}
	//row.title = 'None';
	$('#dlg').dialog('setTitle', '修改 #'+row.id);
	$('#p2-title').html('修改 #'+row.id);
	$('#fm').form('clear');
	$('#fm').form('load', row);
	$('#dlg_save').show();
	if (row.fileid==0) {	//没有文件则显示上传框
	    $('#filebox').show();
	    $('#fileid').hide();
	    $('#filename').hide();
	}
	else {	//有文件则显示只读
	    $('#filebox').hide();
	    $('#fileid').show();
	    $('#filename').show();
	}
	url = 'Update?_log=false&id=' + row.id;
	action = "editBook()";
	action_row = row;
    }
}

function replyBook(row) {
    var row = $('#dg').datagrid('getSelected');
    if (!row) {
	var row = $('#dg').datagrid('getSelected');
	if (!row) {
	    row = action_row;
	} 
    }
    if (row) {
	if($('#dlg').dialog('options').closed == true) {
	    $('#dlg').dialog('open').dialog('center');
	}
	//row.title = 'none';
	$('#dlg').dialog('setTitle', '回复 #'+row.id);
	$('#fm').form('clear');
	$('#filebox').show();
	$('#fileid').hide();
	$('#filename').hide();
	$('#dlg_save').show();
	url = 'Save?_log=false&parentid=' + row.id;
	action = "replyBook()";
	action_row = row;
    }
}

function delBook() {    // 删除记录， 在查看和编辑界面调用
    row = action_row;
    $.messager.confirm('警告','你确认要删除记录#'+row.id+'吗？', function(c) {
	    if(c) {
		delBook1();
	    }
    });
}
function delBook1() {
    row = action_row;
    $.getJSON('Destroy', {id:row.id}, function(json, status, jqr) {
	if (status=='success') {
	    index = $('#dg').datagrid('getRowIndex',row);
	    $('#dg').datagrid('reload');
	    //$.mobile.go('#p0');
	    //$('#dg').datagrid('reload');
	    //$('#dg').datagrid('fixDetailRowHeight', 1);
	}else {
	    console.log('err, ', json, status, jqr);
	}
    });
}

// 格式化字符串， 用法：
// "asfd{a}:{b}".format({a:'ra',b:23});
// "adf{0}:{1}, {0}".format(['a','b']);
String.prototype.format = function(args) {
    var result = this;
    if (arguments.length > 0 ) {
	if (arguments.length == 1 && typeof(args)=="object") {
	    for (var key in args) {
		if(args[key] != undefined) {
		    var reg = new RegExp("({"+key+"})", "g");
		    result = result.replace(reg, args[key]);
		}
	    }
	}
	else {
	    for (var i=0; i<arguments.length; i++) {
		if (arguments[i] != undefined) {
		    var reg = new RegExp("({["+i+"]})", "g");
		    result = result.replace(reg, arguments[i]);
		}
	    }
	}
    }
    return result;
}


//火狐,chrome和IE都支持的复制剪切板功能window.clipboardData.setData
//分类： 前端技术/ JS JAVASCRIPT/ 文章

function copyToClipboard(txt) {
	if (window.clipboardData) {
		window.clipboardData.clearData();
		window.clipboardData.setData("Text", txt);
		alert("复制成功！")
	} else if (navigator.userAgent.indexOf("Opera") != -1) {
		window.location = txt;
		alert("复制成功！");
	} else if (window.netscape) {
		try {
			netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
		} catch (e) {
			alert("被浏览器拒绝！\n请在浏览器地址栏输入'about:config'并回车\n然后将 'signed.applets.codebase_principal_support'设置为'true'");
		}
		var clip = Components.classes['@mozilla.org/widget/clipboard;1'].createInstance(Components.interfaces.nsIClipboard);
		if (!clip)
			return;
		var trans = Components.classes['@mozilla.org/widget/transferable;1'].createInstance(Components.interfaces.nsITransferable);
		if (!trans)
			return;
		trans.addDataFlavor('text/unicode');
		var str = new Object();
		var str = Components.classes["@mozilla.org/supports-string;1"].createInstance(Components.interfaces.nsISupportsString);
		var copytext = txt;
		str.data = copytext;
		trans.setTransferData("text/unicode", str, copytext.length * 2);
		var clipid = Components.interfaces.nsIClipboard;
		if (!clip)
			return false;
		clip.setData(trans, null, clipid.kGlobalClipboard);
		alert("复制成功！")
	}else if(copy){
		copy(txt);
		alert("复制成功！")
	}
}


function copyTextToClipboard(text) {	// execCommand
    var textArea = document.createElement("textarea");
    textArea.style.background = 'transparent';
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
	var succ = document.execCommand('copy');
	var msg = succ? 'success': 'error';
    } catch (err) {
	console.log('ops unable to copy', err);
    }
    document.body.removeChild(textArea);
}

function copyToTextarea(){  //将dg表格中的数据复制到textarea组件中, 并在dlg2窗口中展示组件和"复制"按钮
    console.log('copy start..');
    tbl = $('#'+'dg');
    console.log('typeof dg', typeof(tbl), tbl);
    try {   // 先尝试支treegrid方式获取数据, 出错的话以datagrtid方式取.
    opt = tbl.treegrid('options');
    console.log('opt[treeField]', opt['treeField']);
    data = tbl.treegrid('getData');
    rows = data;    // treegrid的数据,直接是行,没有totals, rows， 而且没有展开后的新行
    console.log('getData:', opt, data);
    tbl.treegrid('selectAll');
    data = tbl.treegrid('getSelections');
    rows = data;
    console.log('getSelections', data);
    } catch(err) {
    opt = tbl.datagrid('options');
    data = tbl.datagrid('getData');
    rows = data.rows;
    console.log('getData:', opt, data);
    }
    var field = new Array();
    var title = new Array();
    try {
	$.each(opt.frozenColumns[0], function(i, col){
	    field.push(col.field);
	    title.push(col.title);
	})
    } catch(err) {
	pass;
    }
    $.each(opt.columns[0], function(i, col) {
	field.push(col.field);
	title.push(col.title);
    });
    res = title.join('\t');
    $.each(rows, function(i,rec) {
	//  这儿没有严格按照展示时显示的顺序进行导出，查找原因？
	res += '\n';
	var line = new Array();
	$.each(field, function(j, col) {
	    line.push(rec[col]);
	});
	res += line.join('\t');
    });
    area = document.getElementById('textarea');
    area.value = res
    $('#dlg2').dialog('open').dialog('center');
}
