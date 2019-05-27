<!DOCTYPE html>
<html>
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
<head>
    <style>
html {
    text-align: center;
    font-family: 'Roboto', sans-serif;
}
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #63AE45;
    color: white;
    text-align: center;
}
ul {
  list-style-type: none;
  position: fixed;
  top: -16px;
  left: 0;
  width: 100%;

  overflow: hidden;
  background-color: #333;
}
li {
  float: left;
}
li a {
  display: block;
  color: white;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}
li a:hover:not(.active) {
  background-color: #63AE45;
}
    </style>
    <title>AlienVault</title>
</head>
<body>

    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/viewJobs/failedJobs">Failed Jobs</a></li>
        <li><a href="/viewJobs/scheduledJobs">Scheduled Jobs</a></li>
        <li><a href="/viewJobs/archivedJobs">Archived Jobs</a></li>
        <li><a href="/viewSubOrgs">SubOrgs</a></li>
    </ul>
    <br><br><br><br>
    <img src="/static/logo.png" alt="AlienVault Logo" height="100">

    <div id="pagebody">
        %include
    </div>
    
    <div class="footer">
        <p>AlienVault</p>
    </div>
</body>
</html>
