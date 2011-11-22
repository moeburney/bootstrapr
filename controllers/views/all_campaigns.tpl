<!DOCTYPE html>
<html>
<head>
<title>{{items[0].desc}}</title>
</head>
%import datetime
<body>
</body>
<table border="1">
<thead> <tr><th>Name</th><th>Money Spent</th><th>Revenue</th><th>Conversions</th><th>Profit</th><th>Return on Investment</th><th>Start Date</th><th>End Date</th><th>Time Spent</th><th>Type</th><th>Goals</th><th>Custom Attributes</th> </tr></thead>
<tfoot>
%for x in items:
<tr><td>{{x.desc}}</td><td>{{x.cash_spent}}</td><td>{{x.revenue}}</td><td>{{x.conversions}}</td><td>{{x.profit}}</td><td>{{x.roi}}</td><td>{{datetime.datetime.fromtimestamp(x.startTs)}}</td><td>{{datetime.datetime.fromtimestamp(x.endTs)}}</td><td>{{datetime.datetime.fromtimestamp(x.time_spent)}}</td><td>{{x.campaign_desc}}</td><td>{{x.goal}}</td><td>{{x.attrs}}</td><td><a href={{"/campaigns/"+str(x.id)}}>Edit</a></td></tr>
%end
</tfoot>
</table>
</html>