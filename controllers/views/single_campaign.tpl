<!DOCTYPE html>
<html>
<head>
<title>{{item.desc}}</title>
</head>
%import datetime
<body>
<form action='/campaigns/{{item.id}}' method=POST>
<input type=hidden id="uuid" name="uuid" value="{{item.uuid}}"></input>
<label for="desc">Description:</label> <input type=text id="desc" name="desc" value="{{item.desc}}"></input><br>
<label for="cash_spent">Cash Spent:</label> <input type=text id="cash_spent" name="cash_spent" value="{{item.cash_spent}}"></input><br>
<label for="time_spent">Time Spent:</label> <input type=text id="time_spent" name="time_spent" value="{{datetime.datetime.fromtimestamp(item.time_spent)}}"></input><br>
<label for="revenue">Revenue:</label> <input type=text id="revenue" name="revenue" value="{{item.revenue}}"></input><br>
<label for="conversions">Conversions:</label> <input type=text id="conversions" name="conversions" value="{{item.conversions}}"></input><br>
<label for="profit">Profit:</label> <input type=text id="profit" name="profit" value="{{item.profit}}"></input><br>
<label for="roi">Return on Investment:</label> <input type=text id="roi" name="roi" value="{{item.roi}}"></input><br>
<label for="sts">Start Time:</label> <input type=text id="sts" name="sts" value="{{datetime.datetime.fromtimestamp(item.startTs)}}"></input><br>
<label for="ets">End Time:</label> <input type=text id="ets" name="ets" value="{{datetime.datetime.fromtimestamp(item.endTs)}}"></input><br>
<label for="ctype">Campaign type</label> <select id="ctype" name="ctype"><br>
%if main_ctype is not None:
  <option value="{{main_ctype.desc}}">{{main_ctype.desc}}</option><br>
%end
%for x in ctypes:
  <option value="{{x.desc}}">{{x.desc}}</option>
%end
</select><br>
%if item.goal is not None:
<label for="goal">Goal: </label><input type=text id="goal" name="goal" value="{{item.goal}}"></input><br>
%else:
<label for="goal">Goal: </label><input type=text id="goal" name="goal" value=0></input><br>
%end
%if uattrs["empty"] is not True:
%for attr,val in uattrs.iteritems():
<label for="{{attr}}">{{attr}}</label> <input type=text id="{{attr}}" name="{{attr}}" value="{{val}}"></input><br>
%end
%end
<input type="submit" value="Update"></input>   <input type="reset" value="Reset"></input><br>
</form>
</body>

</html>
  