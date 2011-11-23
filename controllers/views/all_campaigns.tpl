<!DOCTYPE html>
<html>
<head>
<title>{{items[0].desc}}</title>
      <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/base/jquery-ui.css">
  <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/smoothness/jquery-ui.css">

</head>
%import datetime
<body>

<table border="1">
<thead> <tr><th>Name</th><th>Money Spent</th><th>Revenue</th><th>Conversions</th><th>Profit</th><th>Return on Investment</th><th>Start Date</th><th>End Date</th><th>Time Spent</th><th>Type</th><th>Goals</th><th>Custom Attributes</th> </tr></thead>
<tfoot>
%for x in items:
<tr><td>{{x.desc}}</td><td>{{x.cash_spent}}</td><td>{{x.revenue}}</td>
<td>{{x.conversions}}</td><td>{{x.profit}}</td><td>{{x.roi}}</td>
<td>{{datetime.datetime.fromtimestamp(x.startTs)}}</td><td>{{datetime.datetime.fromtimestamp(x.endTs)}}</td>
<td>{{x.time_str}}</td><td>{{x.campaign_desc}}</td><td>{{x.goal}}</td><td>{{x.attrs}}</td>
<td><a href={{"/campaigns/"+str(x.id)}}>Edit</a></td>
<td><a class="delete" href={{"/campaigns/"+str(x.id)+"/destroy"}}>Delete</a></td></tr>
%end
</tfoot>
</table>
<a href="/campaigns/new.html">Create New Campaign</a>
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
  <script> $( "input:submit, a, button,input:reset").button();
  function show_confirm(obj){
      var r=confirm("Are you sure you want to delete?");
      if (r==true)
         window.location = obj.attr('href');
  }
  $('.delete').click(function(event) {
      event.preventDefault();
      show_confirm($(this));

  });

  </script>
</body>
</html>