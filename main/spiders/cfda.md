The code for requesting data can be found in:

```javascript
function commitForECMA(callback,url,curForm)
{  
	//alert("*******enter commitForECMA"+url);
   request=createXMLHttp();      
   request.onreadystatechange=callback;   
   if(curForm==null)
   {
      request.open("GET",url);
	  request.setRequestHeader("Content-Type","text/html;encoding=gbk");
   }
   else
   {
      var fromEle="";
      var myElements=curForm.elements;
	  var myLength=myElements.length;
	  for(var i=0;i<myLength;i++)
	  {
		    var myEle=myElements[i];
		    if(myEle.type!="submit"&&myEle.value!="")
		    {
		       if(fromEle.length>0)
		       {
		         fromEle+="&"+myEle.name+"="+myEle.value;
		       }
		       else
		       {
		          fromEle+=myEle.name+"="+myEle.value;
		       }
		       
		       fromEle+="&State=1";
		    }
	  }
      request.open("POST",url);
      fromEle=encodeURI(fromEle);
      fromEle=encodeURI(fromEle);
      request.setRequestHeader("cache-control","no-cache"); 
      request.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	}
//	alert('FAFA44');
   request.send(fromEle);
//alert('AAA22');
   if(curForm != null){
   curForm.reset();	
   }
   
}
```

Here is the form:
```html
<form method="post" id="pageForm" name="pageForm">
<input type="hidden" name="tableId" value="25">
<input type="hidden" name="bcId" value="152904713761213296322795806604">
<input type="hidden" name="tableName" value="TABLE25">
<input type="hidden" name="viewtitleName" value="COLUMN167">
<input type="hidden" name="viewsubTitleName" value="COLUMN821,COLUMN170,COLUMN166">
<input type="hidden" name="keyword" value="">
<input type="hidden" name="curstart" value="">
<input type="hidden" name="tableView" value="国产药品">
</form>
```