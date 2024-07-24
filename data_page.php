<?php

var_dump($_SERVER["REQUEST_METHOD"]);
header("Location ../contact.html")

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $firstname = htmlspecialchars($_POST["firstname"])
    $lastname = htmlspecialchars($_POST["lastname"])
    $email = htmlspecialchars($_POST["email"])
    $message = htmlspecialchars($_POST["message"])

    echo "This is the data, the user submitted";
    echo "<br>";
    echo $firstname;
    echo "<br>";
    echo $lastname;
    echo "<br>";
    echo $email;
    echo "<br>";
    echo $message;

    header("Location ../contact.html")
}