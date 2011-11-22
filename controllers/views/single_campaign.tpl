<!DOCTYPE html>
<html>
<head>
<title>{{item.desc}}</title>
      <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/base/jquery-ui.css">
  <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/flick/jquery-ui.css">

</head>
%import datetime
<body>
<form action='/campaigns/{{item.id}}' method=POST>
<input type=hidden id="uuid" name="uuid" value="{{item.uuid}}"></input>
<label for="desc">Description:</label> <input type=text id="desc" name="desc" value="{{item.desc}}"></input><br>
<label for="cash_spent">Cash Spent:</label> <input type=number id="cash_spent" name="cash_spent" value="{{item.cash_spent}}"></input><br>
<label for="time_spent">Time Spent:</label> <input type=number id="time_spent" name="time_spent" value="{{item.time_str}}"></input><br>
<label for="revenue">Revenue:</label> <input type=number id="revenue" name="revenue" value="{{item.revenue}}"></input><br>
<label for="conversions">Conversions:</label> <input type=number id="conversions" name="conversions" value="{{item.conversions}}"></input><br>
<label for="profit">Profit:</label> <input type=number id="profit" name="profit" value="{{item.profit}}"></input><br>
<label for="roi">Return on Investment:</label> <input type=number id="roi" name="roi" value="{{item.roi}}"></input><br>
<label for="sts">Start Time:</label> <input type=date id="sts" name="sts" value="{{datetime.datetime.fromtimestamp(item.startTs)}}"></input><br>
<label for="ets">End Time:</label> <input type=date id="ets" name="ets" value="{{datetime.datetime.fromtimestamp(item.endTs)}}"></input><br>
<label for="ctype">Campaign type</label> <select id="ctype" name="ctype"><br>
%if item.campaign_type != 0:
  <option value="{{item.campaign_type}}">{{item.campaign_desc}}</option><br>
%end
%for x in ctypes:
  <option value="{{x.id}}">{{x.desc}}</option>
%end
</select><br>
%if item.goal is not None:
<label for="goal">Goal: </label><input type=text id="goal" name="goal" value="{{item.goal}}"></input><br>
%else:
<label for="goal">Goal: </label><input type=text id="goal" name="goal" value=0></input><br>
%end
%if uattrs:
%for attr,val in uattrs.iteritems():
<label for="{{attr}}">{{attr}}: </label> <input type=text id="{{attr}}" name="{{attr}}" value="{{val}}"></input><br>
%end
%end
<input type="submit" value="Update"></input>   <input type="reset" value="Reset"></input><br>
</form>
<a href="/campaigns">HOME</a>
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
  <script> $( "input:submit, a, button,input:reset").button(); </script>

</body>

</html>
  