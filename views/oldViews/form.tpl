<!DOCTYPE html>
<html>
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
<head>
    <style>
        html {
    font-family: 'Roboto', sans-serif;
}
h1 {
    text-align: center;
}
p {
    text-align: center;
}
form {
    text-align: center;
}
input[type=text] {
    width: 60%;
    padding: 15px 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    font-size:18px;
}
input[type=submit] {
    width: 50%;
    background-color: #FF9226;
    padding: 20px 0;
    border: 1px solid;
    border-radius: 10px;
    color:white;
}
input[type=submit]:hover {
    background-color: #FFA54C;    
}
#theForm {
    border-radius: 15px;
    background-color: #ececec;
    padding: 20px;
}
    </style>
    
    <title>AlienVault - Start Lab</title>
</head>
<body>
    <h1>Start Lab</h1>
    <div id="theForm">
    <form action="/boru/form" method="post">
        Account Name:<br>
        <input type="text" name="field1" autocomplete="off">
        <br><br>
        Password:<br>
        <input type="text" name="field2" autocomplete="off">
        <br><br>
        Region:<br>
        <select name="field3" style="width:62%; height:50px;">
            <option value="us-east-1">US East 1</option>
        </select>
        <br><br>
        Course:<br>
        <select name="field4" style="width:62%; height:50px;">
            <option value="ANYDC">ANYDC</option>
        </select>
        <br><br>
        Sensor:<br>
        <select name="field5" style="width:62%; height:50px;">
            <option value="yes">Yes</option>
            <option value="no">No</option>
        </select>
        <br><br>
        Tag:<br>
        <input type="text" name="field6" autocomplete="off">
        <br><br>
        Begin Date:<br>
        <select name="field7" style="width:62%; height:50px;">
            <option value="now">Now</option>
	</select>        
	<br><br>
        End Date:<br>
        <input type="date" name="field8" style="width:62%; height:50px;">
        <br><br>
        Timezone:<br>
        <select name="field9" style="width:62%; height:50px;">
            <option value="WET">WET (Dublin)</option>
            <option value="CET">CET (Paris)</option>
            <option value="EST">EST (New York)</option>
            <option value="CST">CST (Austin)</option>
            <option value="PST">PST (San Francisco)</option>
            <option value="APJ">APJ (Sydney)</option>
        </select>
        <br><br>
        <input type="submit" value="Submit">
    </form> 
    </div><br><br><br>
</body>
</html>
%rebase base
