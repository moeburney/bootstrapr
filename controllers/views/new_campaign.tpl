<!DOCTYPE html>
<html>
<head>
    <title>Add Campaign</title>
      <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/base/jquery-ui.css">
  <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/smoothness/jquery-ui.css">
</head>
<body>
<form id="cform" action="/campaigns" method="POST">
    <h3>General: </h3>
    <input type="text" id="desc" name="desc" placeholder="Name of Campaign" required/><br/>
    <label for="ctype">Type of Campaign: </label> <select id="ctype" name="ctype">
    %for x in ctypes:
      <option value="{{x.id}}">{{x.desc}}</option>
    %end
    </select><br>
     <br>
        <input type=text id="goal" name="goal" placeholder="Goals of Campaign"/><br/>
    <input type=date id="sts" name="sts" placeholder="Campaign Start DateTime"/><br/>
    <input type=date id="ets" name="ets" placeholder="Campaign End DateTime"/><br/>
    <h3>Expenses: </h3>
     <label for="gains">Type of Campaign: </label> <select id="gains" name="gains">
    %for x in gains:
      <option value="{{x}}">{{x}}</option>
    %end
    </select><br>
     <br>
    <h3>Gains: </h3>
    <input type=number id="revenue" name="revenue" placeholder="Revenue"/><br/>
    <input type=number id="conversions" name="conversions" placeholder="Number of Conversions"/><br/>
    <input type=number id="profit" name="profit" placeholder="Profits Earned"/><br/>
    <input type=number id="roi" name="roi" placeholder="Return on Investment"/><br/>
    <h3>Custom Data: </h3>
    <input type=hidden id="attrs" name="attrs"/>
    <a id="addData">Add Custom Data</a><br/><br/>
    <input type="submit" id="submit" value="Create Campaign"/> <input type="reset" value="Clear"/>  <a href="/campaigns">Home</a><br/>
    </form>
</form>
<div id="dialog-form" title="Create new data">
	<form>
	<fieldset>
        <label for="name">Name: </label>
		<input required type="text" name="name" id="name" class="text ui-widget-content ui-corner-all" placeholder="Name"/>
         <select required id="dtype" name="dtype">
        <option value="Text">Text</option>
        <option value="TextArea">Big Text</option>
        <option value="Number">Number</option>
        <option value="Date">Date</option>
        <option value="Email">Email</option>
    <option value="url">url</option></select>
    </fieldset>

	</form>
</div>
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
<script type="text/javascript"> $(function() {
        
		$( "input:submit, a, button,input:reset").button();
		$( "#addData" ).click(function() { $( "#dialog-form" ).dialog( "open" ) });
        $("#cform").submit(function(event){
            var attrs = {}
            $("input[id^=custom-]").each(function(item,value){
               attrs[$(value).attr('placeholder')] = $(value).val()
            })
            var stringi = JSON.stringify(attrs)
            $('#attrs').val(stringi)
           
                return true;
        })
	$( "#dialog-form" ).dialog({
			autoOpen: false,
			height: 300,
			width: 350,
			modal: true,
			buttons: {
				"Create custom data": function() {
				$("#submit").before("<input value='' id=custom-"+$("#name").val()+" required placeholder="+$("#name").val()+" type="+$("#dtype").val()+"/><br/>");
                 $( this ).dialog( "close" );
				},
				Cancel: function() {
					$( this ).dialog( "close" );
				},
                close: function(){$(this).dialog("close")}
			}

		});
	});
</script>
</body>
</html>


