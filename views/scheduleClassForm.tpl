<!DOCTYPE html>
<html>
    <!-- Font -->
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
<head>
    <!-- CSS -->
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
    width: 80%;
    padding: 6px 0;
    border: 1px solid #ccc;
    font-size:16px;
    background-color: w;
}
input[type=submit] {
    width: 80%;
    background-color: #63AE45;
    padding: 10px 0;
    border: 1px solid;
    border-radius: 10px;
    color:white;
}
input[type=submit]:hover {
    background-color: #4ac44f;
}
#theForm {
    border-radius: 10px;
    padding: 20px;
    margin-left: 30%;
    margin-right: 30%;
    background-color: #e0e0e0;
}
    </style>
    
    <title>Schedule Class</title>
</head>
<body>
    <h1>Schedule Class</h1>
    <!-- The Form -->
    <div id="theForm">
    <form action="/boru/scheduleClass" method="post">
        
        Sender(will be hidden):<br>
        <input type="text" name="sender" placeholder=" Will be hidden: Type your Name Surname" autocomplete="off" required>
        
        <br><br>
        
        Instructor:<br>
        <input type="text" name="instructor" placeholder=" Name Surname" autocomplete="off" required>
        
        <br><br>
        
        Number Of SubOrgs:<br>
        <select name="numberOfSubOrgs" style="width:80%; height:30px;">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
        </select>

        <br><br>
        
        Password:<br>
        <input type="text" name="password" placeholder=" Example: Password1!"autocomplete="off" required>
        <br><br>
        
        Region:<br>
        <select name="region" style="width:80%; height:30px;">
            <option value="us-east-1">us-east-1</option>
        </select>
        
        <br><br>
        
        Course:<br>
        <select name="course" style="width:80%; height:30px;">
            <option value="littleBoruCourse">littleBoruCourse</option>
        </select>
        
        <br><br>

        Sensor:<br>
        <select name="sensor" style="width:80%; height:30px;">
            <option value="yes">Yes</option>
            <option value="no">No</option>
        </select>

        <br><br>
        
        Start Date:<br>
        <input type="date" name="startDate" style="width:80%; height:30px;" required>
        
        <br><br>

        Finish Date:<br>
        <input type="date" name="finishDate" style="width:80%; height:30px;" required>
        
        <br><br>

        Timezone:<br>
        <select name="timezone" style="width:80%; height:30px;">
            <option value="Europe/Dublin">Europe/Dublin</option>
            <option value="US/Central">US/Central</option>
            <option value="US/Eastern">US/Eastern</option>
            <option value="US/Central">US/Central</option>
            <option value="US/Pacific">US/Pacific</option>
            <option value="Australia/Sydney">Australia/Sydney</option>
        </select>
        
        <br><br>
        
        Suspend Over Night:<br>
        <select name="suspend" style="width:80%; height:30px;">
            <option value="yes">Yes</option>
            <option value="no">No</option>
        </select>
        
        <br><br>
        
        Tag:<br>
        <input type="text" name="tag" autocomplete="off" placeholder=" Example:  EU-May16-17-OC" required>
        
        <br><br>
        
        <input type="submit" value="Schedule Class">
        
        <br><br>
        
    </form>
    </div><br><br><br>
</body>
</html>
%rebase base
